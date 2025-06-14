# Askmi — Your Virtual TA

**Askmi** is an API-based virtual teaching assistant that answers student queries using scraped course content and forum discussions. It uses both text and image embeddings to retrieve the most relevant material and generate concise answers using Groq's **LLaMA 3 7B Versatile** model.

**Live Endpoint**:  
`https://tds-service-498040420684.asia-south1.run.app`

Send POST requests with a student question and (optionally) a base64-encoded image file as JSON.

---

## Usage

### POST request format:

`POST https://tds-service-498040420684.asia-south1.run.app`

### Example using curl:
```bash
curl "https://tds-service-498040420684.asia-south1.run.app" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
    "image": "'$(base64 -w0 project-tds-virtual-ta-q1.webp)'"
  }'
```

---

## Project Structure

```
app/
├── main.py             # FastAPI app
├── llm_groq.py         # Answer generation via Groq (LLaMA 3 7B)
└── vector_search.py    # Chunk retrieval via cosine similarity

data creation/
├── project1scraping.py     # Scrapes course content
├── scrapefromtopics.py     # Scrapes Discourse (edit start/end dates here)
├── scrapigntopics.py       # Processes topic JSON into individual files
├── imagescraper.py         # Scrapes related images
├── tdschunker.py           # Chunks course content
├── tdsdischunker.py        # Chunks forum content
├── tdsembedder.py          # Embeds text chunks using LangChain + Nomic
└── iemb.py                 # Embeds images using OpenCLIP ViT-B/32

chunks/                     # Contains chunked text content
vectorstore/                # Contains text and image embeddings

requirements.txt            # Python dependencies
LICENSE                     # MIT License
```

---

## Workflow Overview

1. **Scraping**  
   - `project1scraping.py`: Scrapes main course material  
   - `scrapefromtopics.py`: Scrapes Discourse content (configure dates in the script)  
   - `scrapigntopics.py`: Converts topic data into individual files  
   - `imagescraper.py`: Downloads image content

2. **Chunking**  
   - `tdschunker.py`: Chunks course material  
   - `tdsdischunker.py`: Chunks forum content  
   (Modify these to include additional info in chunks if needed)

3. **Embedding**  
   - `tdsembedder.py`: Embeds text using LangChain and Nomic  
   - `iemb.py`: Embeds images using OpenCLIP (ViT-B/32)

4. **Serving**  
   - `main.py`: API built with FastAPI  
   - `vector_search.py`: Finds relevant chunks via cosine similarity  
   - `llm_groq.py`: Assembles answers using **Groq’s LLaMA 3 7B Versatile** model

---

## Installation

```bash
git clone https://github.com/bigfriendlygoblin/Project1.git
cd askmi
pip install -r requirements.txt
```

---

## License

This project is licensed under the [MIT License](./LICENSE).
