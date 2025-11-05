import requests
import os

def call_openrouter_model(prompt: str):
    api_key = os.getenv("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mistral",  # or whatever model you're using
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    # You must parse the content into JSON if OpenRouter returns a string
    import json
    return json.loads(content)