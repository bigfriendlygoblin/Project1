import json
import os
from tqdm import tqdm
import numpy as np
import faiss

# Try nomic first, fallback to sentence-transformers
try:
    from nomic import embed
    USE_NOMIC = True
except ImportError:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    USE_NOMIC = False

# === Paths ===
DISCOURSE_PATH = "chunks/discourse_chunks.json"
CONTENT_PATH = "chunks/tds_contentchunks.json"
OUTPUT_INDEX = "vectorstore/tds_index.faiss"
OUTPUT_META = "vectorstore/tds_metadata.json"
os.makedirs("vectorstore", exist_ok=True)

# === Load & Normalize ===
all_texts = []
all_metadata = []

def load_discourse(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for entry in data:
            all_texts.append(entry['text'])
            all_metadata.append({
                "type": "discourse",
                "title": entry.get("title", ""),
                "url": entry.get("url", ""),
                "chunk_id": entry.get("chunk_id", -1),
                "text": entry["text"]  # ✅ add text for parity
            })

def load_content(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for entry in data:
            all_texts.append(entry['text'])
            all_metadata.append({
                "type": "content",
                "source": entry.get("source", ""),
                "chunk_id": entry.get("chunk_id", -1),
                "url": entry.get("url", ""),              # ✅ URL from chunker
                "text": entry['text']                     # ✅ Add text for later display
            })

load_discourse(DISCOURSE_PATH)
load_content(CONTENT_PATH)

# === Generate Embeddings ===
print(f"🔍 Generating embeddings for {len(all_texts)} chunks...")

if USE_NOMIC:
    embeddings = embed.text(
        texts=all_texts,
        model="nomic-embed-text-v1"
    )['embeddings']
else:
    embeddings = model.encode(all_texts, show_progress_bar=True)

# === Create FAISS Index ===
dim = len(embeddings[0])
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings).astype("float32"))

# === Save Outputs ===
faiss.write_index(index, OUTPUT_INDEX)
with open(OUTPUT_META, "w", encoding="utf-8") as f:
    json.dump(all_metadata, f, indent=2)

print(f"✅ FAISS index saved to {OUTPUT_INDEX}")
print(f"📎 Metadata saved to {OUTPUT_META}")

