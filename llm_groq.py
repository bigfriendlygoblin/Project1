import requests

GROQ_API_KEY = "xx"  # Replace with environment variable in production
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def query_groq_mistral(system_msg, user_msg):
    headers = {
        "Authorization": "Bearer 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",
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

