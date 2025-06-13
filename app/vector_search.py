# app/vector_search.py
import os
import numpy as np
import faiss
import json

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

# Assuming these paths
IMAGE_EMBEDDING_INDEX = "vectorstore/tds_imageembeddings.faiss"
IMAGE_EMBEDDING_METADATA = "vectorstore/tds_image_metadata.json"
TEXT_CHUNKS_FILE = "chunks/discourse_chunks.json"

# Load index and metadata once (you can optimize with lazy loading)
image_index = faiss.read_index(IMAGE_EMBEDDING_INDEX)
with open(IMAGE_EMBEDDING_METADATA, "r", encoding="utf-8") as f:
    image_metadata = json.load(f)


with open(TEXT_CHUNKS_FILE, "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

def search_similar_image(clip_embedding, k=1):
    """
    Searches for similar images and returns topic_id(s) extracted from filename.
    """
    clip_embedding = np.array(clip_embedding).astype("float32")
    distances, indices = image_index.search(clip_embedding, k)
    topic_ids = set()

    for idx in indices[0]:
        filename = image_metadata[idx]["filename"]
        topic_id = filename.split("_")[0]  # Extract '141413' from '141413_img1.jpeg'
        topic_ids.add(topic_id)

    return list(topic_ids)

def get_chunks_by_topic_id(topic_id):
    """
    Returns all text chunks that belong to a specific topic ID.
    Assumes each chunk dict has 'topic' key with 'id'.
    """
    chunks = [
        chunk for chunk in all_chunks
        if str(chunk.get("topic", {}).get("id", "")) == str(topic_id)
    ]
    return chunks
