<<<<<<< HEAD
def generate_pronunciation_advice(target: str, spoken: str) -> str:
    if target.lower() == spoken.lower():
        return "Perfect pronunciation!"
=======
def generate_pronunciation_advice(target: str, spoken: str) -> str:
    if target.lower() == spoken.lower():
        return "Perfect pronunciation!"
>>>>>>> 4daf35df3639cf69d5b0bd39ee5223fb11288d9b
    return f"Try to pronounce '{target}' more clearly. You said '{spoken}', which sounds different."