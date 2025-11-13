from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_pronunciation_attempt(user_id: str, word: str, score: float):
    supabase.table("pronunciation_attempts").insert({
        "user_id": user_id,
        "word": word,
        "score": score
    }).execute()
