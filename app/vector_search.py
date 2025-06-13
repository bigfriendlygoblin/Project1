# app/vector_search.py
import faiss
import json
import numpy as np

# Load index and metadata
index = faiss.read_index("vectorstore/tds_index.faiss")
with open("vectorstore/tds_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

def search_similar_chunks(query_embedding: np.ndarray, k=3):
    D, I = index.search(query_embedding, k)
    results = []
    for idx in I[0]:
        if idx >= 0:
            results.append(metadata[idx])
            # Optional: fetch neighbors here
    return results
