from difflib import SequenceMatcher

prompt_cache = {}

def evaluate_fill_answer(prompt_id: str, user_answer: str) -> dict:
    if prompt_id not in prompt_cache:
        raise ValueError(f"Prompt ID '{prompt_id}' not found in cache.")
    
    print("🧠 Evaluating:", prompt_id, "→", user_answer)
    print("📦 prompt_cache keys:", list(prompt_cache.keys()))

    correct_answer = prompt_cache[prompt_id]
    score = int(user_answer.strip().lower() == correct_answer.strip().lower())
    feedback = "Correct!" if score else f"Oops! The correct answer was '{correct_answer}'."

    return {"score": score, "feedback": feedback}


def evaluate_pronunciation_score(target: str, actual: str) -> float:
    ratio = SequenceMatcher(None, target.strip().lower(), actual.strip().lower()).ratio()
    return round(ratio * 100, 2)

