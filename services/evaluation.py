from services.openrouter import prompt_store

def evaluate_fill_answer(prompt_id, user_text):
    expected = prompt_store.get(prompt_id, "")
    score = 100 if expected and expected.lower() in user_text.lower() else 0
    feedback = "✅ Gut gemacht!" if score == 100 else f"❌ Versuche es nochmal. Erwartet: '{expected}'"
    return {"score": score, "feedback": feedback}

def evaluate_pronunciation_score(target: str, spoken: str) -> float:
    from difflib import SequenceMatcher
    return round(SequenceMatcher(None, target.lower(), spoken.lower()).ratio() * 100, 2)