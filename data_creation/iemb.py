import os
import json
import numpy as np
import faiss
from PIL import Image
import torch
import open_clip

# --- Config ---
IMAGE_DIR = "scraped_images"
OUTPUT_INDEX = "vectorstore/tds_imageembeddings.faiss"
OUTPUT_METADATA = "vectorstore/tds_image_metadata.json"

# --- Setup ---
os.makedirs("vectorstore", exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
model = model.to(device)
model.eval()

# --- Helper to embed image ---
def embed_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image_tensor)
    return embedding.cpu().numpy().astype("float32")[0]

# --- Main loop ---
embeddings = []
metadata = []

for filename in os.listdir(IMAGE_DIR):
    filepath = os.path.join(IMAGE_DIR, filename)
    ext = os.path.splitext(filename)[-1].lower()

    if ext in [".svg", ".avif"]:
        print(f"⚠️ Skipping unsupported format: {filename}")
        continue

    try:
        vec = embed_image(filepath)
        embeddings.append(vec)

        metadata.append({
            "filename": filename,
            "local_path": filepath.replace("\\", "/")
        })

        print(f"✅ Embedded: {filename}")
    except Exception as e:
        print(f"❌ Failed to embed {filename}: {e}")

# --- Save results ---
if embeddings:
    vecs_np = np.stack(embeddings)
    index = faiss.IndexFlatL2(vecs_np.shape[1])
    index.add(vecs_np)
    faiss.write_index(index, OUTPUT_INDEX)

    with open(OUTPUT_METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n💾 Saved {len(embeddings)} image embeddings to {OUTPUT_INDEX}")
else:
    print("⚠️ No embeddings were generated.")
