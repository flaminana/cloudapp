import requests
import os
import json
from dotenv import load_dotenv
import uuid
import random
import re
from services.evaluation import prompt_cache

A1_TOPICS = [
    "Guten Tag. Mein Name ist",
    "Meine Familie",
    "Essen und Trinken",
    "Meine Wohnung",
    "Mein Tag",
    "Freizeit",
    "Lernen – Ein Leben Lang"
]


def extract_json_block(text):
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    raise ValueError("No valid JSON block found in OpenRouter response.")

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
    if not OPENROUTER_API_KEY:
            print("❌ Missing OpenRouter API key")
            return {"error": "Missing OpenRouter API key", "raw": ""}
    
    prompt = (
        "Generate a German vocabulary multiple-choice question for A1 learners." 
        "Respond ONLY with JSON in this format: {\"question\": \"...\", \"options\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}, \"answer\": \"A\"}"
    )
    data = {
        "model": "mistralai/mistral-7b-instruct",
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
            cleaned = content.strip()
            if cleaned.startswith("<s>"):
                cleaned = cleaned[3:].strip()

            parsed = json.loads(cleaned)

            if "question" not in parsed or "options" not in parsed or "answer" not in parsed:
                raise ValueError("Missing required fields in OpenRouter response")

            # Convert list to labeled dict
            options = parsed.get("options", {})

            # If it's a list, convert to labeled dict
            if isinstance(options, list):
                options = dict(zip(["A", "B", "C", "D"], options))

            return {
                "question": parsed.get("question", ""),
                "options": options,
                "answer": parsed.get("answer", "")
            }

        except json.JSONDecodeError as e:
            print("❌ Failed to parse OpenRouter response:", content)
            return {"error": str(e), "raw": content}

    except Exception as e:
            print("❌ OpenRouter error:", e)
            return {"error": str(e), "raw": "No content returned due to error"}

def check_objective_answer(correct_answer, user_answer):
    # Returns True if the user's answer matches the correct answer
    return correct_answer == user_answer


def generate_german_prompt():
    topic = random.choice(A1_TOPICS)
    print(f"🎯 Selected topic: {topic}")  # Optional debug

    prompt = (
        f"Generate a simple A1-level German sentence with one missing word (fill-in-the-blank) "
        f"related to the topic: '{topic}'. "
        f"Respond ONLY with JSON like this: ```json {{\"sentence\": \"Ich ___ gerne Kaffee.\", \"answer\": \"trinke\"}} ```"
    )
    try:
        result = call_openrouter_model(prompt)
        print("🧠 OpenRouter returned:", result)

        if "sentence" not in result or "answer" not in result:
            raise ValueError("Missing 'sentence' or 'answer' in OpenRouter response")

        prompt_id = str(uuid.uuid4())
        prompt_cache[prompt_id] = result["answer"]

        return {
            "id": prompt_id,
            "sentence": result["sentence"],
            "answer": result["answer"]
        }
    except Exception as e:
        print("❌ Failed to generate prompt:", e)
        raise

def call_openrouter_model(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    if not OPENROUTER_API_KEY:
        print("❌ Missing OpenRouter API key")
        return {"error": "Missing OpenRouter API key", "raw": ""}

    data = {
        "model": "mistralai/mistral-7b-instruct",  
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
        print("🧾 Full OpenRouter JSON:", json.dumps(result, indent=2))
        if "choices" not in result or not result["choices"]:
            raise ValueError("OpenRouter returned no choices.")
        content = result["choices"][0]["message"]["content"]
        if not content.strip():
            raise ValueError("OpenRouter returned empty content.")

        cleaned = content.strip()
        if cleaned.startswith("<s>"):
            cleaned = cleaned[3:].strip()

        # Extract the first JSON object only
        json_match = re.search(r"\{.*?\}", cleaned, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON object found in OpenRouter response.")

        json_str = json_match.group(0)
        return json.loads(json_str)
    
    except Exception as e:
        print("❌ OpenRouter error:", e)
        raise

def generate_pronunciation_word():
    prompt = (
        "Give me one useful German word for pronunciation practice and its English translation. "
        "Respond ONLY with JSON like this: {\"word\": \"Fenster\", \"translation\": \"window\"}. "
        "Do not include any explanation or commentary."
    )
    try:
        result = call_openrouter_model(prompt)
        print("🧠 OpenRouter returned:", result)

        if "word" not in result or "translation" not in result:
            raise ValueError("Missing 'word' or 'translation' in OpenRouter response")
        return {
            "id": str(uuid.uuid4()),
            "german": result["word"],
            "english": result["translation"]
        }
    
    except Exception as e:
        print("❌ Failed to generate pronunciation word:", e)

        return {
            "id": str(uuid.uuid4()),
            "german": "Haus",
            "english": "house"
        }

def translate_text(text: str, direction: str) -> str:
    target_lang = "de" if direction == "ENG-GER" else "en"
    prompt = f"Translate this to {target_lang}: {text}"

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={
            "model": "mistralai/mistral-small-3.2-24b-instruct",  # double-check this model name
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a strinct translation engine, Only return the translated sentence or text. No greeting, no suggestions, no formatting"
                },
                {
                    "role": "user",
                    "content": f"Translate this to German: {text}" if direction == "ENG-GER" else f"Translate this to English: {text}"

                }
                
            ]
        }
    )

    print("🔍 OpenRouter raw response:", response.text)

    try:
        data = response.json()
        if "choices" not in data or not data["choices"]:
            raise ValueError("No translation returned from model.")
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Translation failed:", e)
        return "[Translation failed]"