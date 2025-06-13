import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

# CONFIG
TOPIC_POSTS_DIR = "topic_posts"
OUTPUT_FILE = "chunks/discourse_chunks.json"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

def load_topic_post_files(folder_path):
    files = list(Path(folder_path).glob("*.json"))
    return [json.load(open(file, "r", encoding="utf-8")) for file in files]

def format_post(post):
    author = post.get("author", "Unknown")
    content = post.get("content", "").strip()
    
    # Try to detect reply targets via @mention
    match = re.search(r"@(\w+)", content)
    if match:
        replied_to = match.group(1)
        header = f"{author} (replying to @{replied_to}):"
    else:
        header = f"{author}:"
    
    return f"{header}\n{content.strip()}"

def combine_topic_posts(topic_data):
    posts = topic_data.get("posts", [])
    formatted_posts = [format_post(post) for post in posts]
    return "\n\n".join(formatted_posts)

def chunk_topic_texts(topics_data):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    all_chunks = []

    for topic_data in topics_data:
        topic_meta = topic_data.get("topic", {})
        title = topic_meta.get("title", "Untitled")
        url = topic_meta.get("link", "")
        topic_id = topic_meta.get("id", "unknown")

        combined_text = combine_topic_posts(topic_data)
        chunks = splitter.create_documents([combined_text])

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "topic_id": topic_id,
                "title": title,
                "url": url,
                "chunk_id": i,
                "text": chunk.page_content,
            })

    return all_chunks

if __name__ == "__main__":
    Path("chunks").mkdir(exist_ok=True)
    topic_files = load_topic_post_files(TOPIC_POSTS_DIR)
    chunks = chunk_topic_texts(topic_files)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ Chunked {len(topic_files)} topics into {len(chunks)} chunks.")



  - vars:
      question: If a student scores 10/10 on GA4 as well as a bonus, how would it appear on the dashboard?
      link: https://discourse.onlinedegree.iitm.ac.in/t/ga4-data-sourcing-discussion-thread-tds-jan-2025/165959/388
    assert:
      - type: contains
        transform: output.answer
        value: 110
      - type: contains
        transform: JSON.stringify(output.links)
        value: https://discourse.onlinedegree.iitm.ac.in/t/ga4-data-sourcing-discussion-thread-tds-jan-2025/165959

  - vars:
      question: I know Docker but have not used Podman before. Should I use Docker for this course?
    assert:
      - type: contains
        transform: output.answer
        value: Podman
      - type: contains
        transform: output.answer
        value: Docker
      - type: contains
        transform: JSON.stringify(output.links)
        value: https://tds.s-anand.net/#/docker

  - vars:
      question: When is the TDS Sep 2025 end-term exam?
    assert:
      - type: contains
        transform: output.answer
        value: doesn't know