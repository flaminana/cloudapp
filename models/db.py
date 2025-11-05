def save_pronunciation_attempt(user_id: str, word_id: str, final_text: str, score: float):
    print(f"📦 Saved pronunciation: {user_id} | {word_id} | '{final_text}' | {score}%")
    # Replace with real DB logic later