# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from vector_search import search_similar_chunks
from llm_groq import query_groq_mistral
from nomic import embed  # for query embedding
from PIL import Image
import io
import base64
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    image: str | None = None  # Optional base64 image

@app.post("/ask")
def ask_question(request: QueryRequest):
    question = request.question
    image_b64 = request.image

    ocr_text = ""

    if image_b64:
        try:
            # Decode base64 image to PIL Image
            image_data = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_data))

            # OCR text extraction
            ocr_text = pytesseract.image_to_string(image)
        except Exception as e:
            print(f"OCR failed: {e}")

    # Combine question with OCR text if any
    combined_text = question
    if ocr_text.strip():
        combined_text += "\n\nExtracted from image:\n" + ocr_text.strip()

    # Get embedding for combined text
    embedding = embed.text([combined_text], model="nomic-embed-text-v1")["embeddings"]
    embedding = np.array(embedding).astype("float32")

    # Search similar chunks
    chunks = search_similar_chunks(embedding, k=3)
    print(chunks)
    context = "\n\n".join(
        f"Title: {c.get('title', c.get('source', 'Unknown'))}\nChunk: {c['text']}" 
        for c in chunks
    )

    system_msg = "You are a helpful teaching assistant for the TDS course. Use the given context to provide a clear, helpful and DETAILED answer."
    user_msg = f"Context:\n{context}\n\nQuery: {question}"

    answer = query_groq_mistral(system_msg, user_msg)
    links = [{"url": chunk.get("url"), "text": chunk.get("title", "Source")} for chunk in chunks]
    return {
        "answer": answer,
        "links": links
    }
