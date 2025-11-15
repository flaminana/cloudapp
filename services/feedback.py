def generate_pronunciation_advice(target: str, spoken: str) -> str:
    if target.lower() == spoken.lower():
        return "Perfect pronunciation!"
    return f"Try to pronounce '{target}' more clearly. You said '{spoken}', which sounds different."
