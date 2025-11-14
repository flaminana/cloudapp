<<<<<<< HEAD
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
=======
def save_pronunciation_attempt(user_id: str, word_id: str, final_text: str, score: float):
    print(f"📦 Saved pronunciation: {user_id} | {word_id} | '{final_text}' | {score}%")
    # Replace with real DB logic later
>>>>>>> 4daf35df3639cf69d5b0bd39ee5223fb11288d9b
