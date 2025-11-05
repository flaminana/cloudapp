import requests
import os
import json
from dotenv import load_dotenv
import uuid


load_dotenv()  # Load environment variables from .env file
prompt_store = {}

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Set in your environment variables

print("🔑 Loaded API Key:", OPENROUTER_API_KEY)  #Optional debug print

def get_objective_question():
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        "Generate a German vocabulary multiple-choice question for learners. "
        "Return JSON like: {\"question\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"answer\": \"A\"}"
    )
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a German quiz generator."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print("🧠 OpenRouter raw content:", content)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("❌ Failed to parse OpenRouter response:", content)
            raise

    except Exception as e:
        print("❌ OpenRouter error:", e)
        raise

def check_objective_answer(correct_answer, user_answer):
    # Returns True if the user's answer matches the correct answer
    return correct_answer == user_answer


def generate_german_prompt():
    prompt = (
        "Generate a German sentence with one missing word for daily conversation practice. "
        "Return JSON with 'sentence' (use ___ for missing word) and 'answer' (the correct word)."
    )
    try:
        result = call_openrouter_model(prompt)
        print("🧠 OpenRouter returned:", result)

        if "sentence" not in result or "answer" not in result:
            raise ValueError("Missing 'sentence' or 'answer' in OpenRouter response")

        prompt_id = str(uuid.uuid4())
        prompt_store[prompt_id] = result["answer"]

        return {
            "id": prompt_id,
            "sentence": result["sentence"]
        }
    except Exception as e:
        print("❌ Failed to generate prompt:", e)
        raise

def call_openrouter_model(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",  # or "mistral" if you're using that
        "messages": [
            {"role": "system", "content": "You are a helpful German language assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print("❌ OpenRouter error:", e)
        raise

def generate_pronunciation_word():
    prompt = (
        "Give me one useful German word for pronunciation practice and its English translation. "
        "Return JSON like: {\"word\": \"Fenster\", \"translation\": \"window\"}"
    )
    try:
        result = call_openrouter_model(prompt)
        print("🧠 OpenRouter returned:", result)

        if "word" not in result or "translation" not in result:
            raise ValueError("Missing 'word' or 'translation' in OpenRouter response")

        word_id = str(uuid.uuid4())
        return {
            "id": word_id,
            "german": result["word"],
            "english": result["translation"]
        }
    except Exception as e:
        print("❌ Failed to generate pronunciation word:", e)
        raise