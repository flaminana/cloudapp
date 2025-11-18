from services.openrouter import call_openrouter_model

def generate_pronunciation_advice(target: str, actual: str) -> str:
    prompt = (
        f"Give pronunciation advice for a German learner who tried to say '{target}' "
        f"but said '{actual}'. Respond with one sentence of advice."
    )
    try:
        result = call_openrouter_model(prompt)
        return result if isinstance(result, str) else result.get("advice", "Keep practicing!")
    except Exception as e:
        print("❌ Failed to generate advice:", e)
        return "Keep practicing!"