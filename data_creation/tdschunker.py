from pathlib import Path
import re
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ------------------------------
# CONFIG
# ------------------------------
MARKDOWN_DIR = "tds_content"         # Folder with your .md files
CHUNK_OUTPUT_FILE = "chunks/tds_contentchunks.json"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ------------------------------
# Strip Images from Markdown
# ------------------------------
def remove_markdown_images(text):
    return re.sub(r'!\[.*?\]\(.*?\)', '', text)

# ------------------------------
# Load and Clean Markdown Files
# ------------------------------
def load_and_process_markdown_files(folder_path):
    docs = []
    for file in Path(folder_path).glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            raw = f.read()
        cleaned = remove_markdown_images(raw)
        docs.append({
            "source": file.name,
            "text": cleaned
        })
    return docs

# ------------------------------
# Chunking
# ------------------------------
def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    all_chunks = []
    for doc in docs:
        filename_no_ext = Path(doc["source"]).stem
        url = f"https://tds.s-anand.net/#/{filename_no_ext}"
        chunks = splitter.create_documents([doc["text"]])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source": doc["source"],
                "chunk_id": i,
                "text": chunk.page_content,
                "url": url
            })
    return all_chunks

# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    docs = load_and_process_markdown_files(MARKDOWN_DIR)
    chunks = chunk_documents(docs)

    Path("chunks").mkdir(exist_ok=True)
    with open(CHUNK_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ Chunked {len(docs)} markdown files into {len(chunks)} clean chunks (images stripped).")
