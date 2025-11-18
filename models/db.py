from supabase import create_client
import os
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_objective_score(user_id: str, correct: int, available: int):
    supabase.table("objective_exercise_scores").insert({
        "user_id": user_id,
        "correct_answer": correct,
        "available_question": available,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

def save_qna_score(user_id: str, correct: int, available: int):
    supabase.table("qna_exercise_scores").insert({
        "user_id": user_id,
        "correct_answer": correct,
        "available_question": available,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

def save_pronunciation_score(user_id: str, score: float):
    supabase.table("pronunciation_check_scores").insert({
        "user_id": user_id,
        "score_percentage": score,
        "created_at": datetime.utcnow().isoformat()
    }).execute()