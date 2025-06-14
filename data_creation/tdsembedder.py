import json
import os
import numpy as np
import faiss
from tqdm import tqdm
from langchain_nomic import NomicEmbeddings

# === Paths ===
DISCOURSE_PATH = "chunks/discourse_chunks.json"
CONTENT_PATH = "chunks/tds_contentchunks.json"
OUTPUT_INDEX = "vectorstore/tds_index.faiss"
OUTPUT_META = "vectorstore/tds_metadata.json"
os.makedirs("vectorstore", exist_ok=True)

# === Initialize Embedder ===
EMBED_MODEL = "nomic-embed-text-v1.5"
DIMENSIONALITY = 256  # Must match what you use in API

embedder = NomicEmbeddings(
    model=EMBED_MODEL,
    dimensionality=DIMENSIONALITY,
    nomic_api_key=os.environ.get("NOMIC_API_KEY", "")  # Set in environment
)

# === Load & Normalize ===
all_texts = []
all_metadata = []

def load_data(path, data_type):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for entry in data:
            all_texts.append(entry['text'])
            meta = {
                "type": data_type,
                "text": entry["text"],
                "url": entry.get("url", ""),
                "chunk_id": entry.get("chunk_id", -1)
            }
            if data_type == "discourse":
                meta["title"] = entry.get("title", "")
            else:
                meta["source"] = entry.get("source", "")
            all_metadata.append(meta)

load_data(DISCOURSE_PATH, "discourse")
load_data(CONTENT_PATH, "content")

# === Generate Embeddings ===
print(f"🔍 Generating {DIMENSIONALITY}D embeddings for {len(all_texts)} chunks...")

# Batch process embeddings with progress bar
batch_size = 32
embeddings = []
for i in tqdm(range(0, len(all_texts), batch_size), desc="Embedding"):
    batch = all_texts[i:i+batch_size]
    embeddings.extend(embedder.embed_documents(batch))

# === Create FAISS Index ===
dim = len(embeddings[0])  # Should match DIMENSIONALITY
assert dim == DIMENSIONALITY, f"Embedding dim mismatch: {dim} vs {DIMENSIONALITY}"

index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings, dtype="float32"))

# === Save Outputs ===
faiss.write_index(index, OUTPUT_INDEX)
with open(OUTPUT_META, "w", encoding="utf-8") as f:
    json.dump(all_metadata, f, indent=2)

print(f"✅ FAISS index ({dim}D) saved to {OUTPUT_INDEX}")
print(f"📎 Metadata saved to {OUTPUT_META}")
