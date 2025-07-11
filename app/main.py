from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from app.vector_search import search_similar_chunks, search_similar_image, get_chunks_by_topic_id
from app.llm_groq import query_groq_mistral
from langchain_nomic import NomicEmbeddings
from PIL import Image
import io
import base64
import pytesseract
import torch
import open_clip
import os
from fastapi.middleware.cors import CORSMiddleware

pytesseract.pytesseract.tesseract_cmd = "tesseract"

# Load CLIP model and preprocess
clip_model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
clip_tokenizer = open_clip.get_tokenizer('ViT-B-32')

# Initialize Nomic Embeddings (API key picked up from env var)
nomic_embedder = NomicEmbeddings(
    model="nomic-embed-text-v1.5",
    dimensionality=256
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or set to your frontend domain like ["https://your-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    image: str | None = None

@app.post("/ask")
def ask_question(request: QueryRequest):
    question = request.question
    image_b64 = request.image

    ocr_text = ""
    image_embedding = None
    extra_chunks = []

    if image_b64:
        try:
            image_data = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_data)).convert("RGB")

            # OCR
            ocr_text = pytesseract.image_to_string(image)

            # CLIP image embedding
            processed = preprocess(image).unsqueeze(0)
            with torch.no_grad():
                image_embedding = clip_model.encode_image(processed).detach().cpu().numpy().astype("float32")

            # Search image index
            topic_id = search_similar_image(image_embedding)
            print("Closest image topic:", topic_id)

            if topic_id:
                extra_chunks = get_chunks_by_topic_id(topic_ids[0])

        except Exception as e:
            print(f"Image processing failed: {e}")

    # Combine text from question and OCR
    combined_text = question
    if ocr_text.strip():
        combined_text += "\n\nExtracted from image:\n" + ocr_text.strip()

    # Embed and search using text
    try:
        embedding = nomic_embedder.embed_query(combined_text)
    except Exception as e:
        print(f"Nomic Embedding Error: {e}")
        raise

    embedding = np.array(embedding, dtype="float32").reshape(1, -1)

    semantic_chunks = search_similar_chunks(embedding, k=3)

    # Combine both sets of chunks, avoid duplicates
    all_chunks = semantic_chunks
    seen_ids = {c.get("id") for c in semantic_chunks}
    for c in extra_chunks:
        if c.get("id") not in seen_ids:
            all_chunks.append(c)

    # Build context
    context = "\n\n".join(
        f"Title: {c.get('title', c.get('source', 'Unknown'))}\nChunk: {c['text']}"
        for c in all_chunks
    )

    system_msg = (
        "You are a helpful teaching assistant for the TDS course. "
        "Use the given content to provide a concise, HELPFUL answer.If some information is not available, say you don't know. "
        "If using discourse data, look for answers by the course TA Jivraj."
    )
    user_msg = f"Context:\n{context}\n\nQuery: {question}"

    answer = query_groq_mistral(system_msg, user_msg)
    links = [{"url": c.get("url"), "text": c.get("title", c.get("source"))} for c in all_chunks]
    print(links)
    return {
        "answer": answer,
        "links": links
    }
