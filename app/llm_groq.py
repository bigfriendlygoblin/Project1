import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY=os.getenv("GROQ_API_KEY")

def query_groq_mistral(system_msg, user_msg):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.7,
        "max_tokens": 1024  # ✅ Add this explicitly!
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        print("Groq response status:", response.status_code)
        print("Groq response body:", response.text)  # ✅ DEBUG OUTPUT

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.HTTPError as e:
        print("HTTPError from Groq:", e)
        raise e
