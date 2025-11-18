from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from services.openrouter import generate_pronunciation_word
from services.google_stt import transcribe_audio_google
from services.audio_convert import convert_webm_to_wav
from services.evaluation import evaluate_pronunciation_score
from services.feedback import generate_pronunciation_advice
from models.db import save_pronunciation_score
#from models.db import save_pronunciation_attempt
from utils.lcd import display_on_lcd

router = APIRouter(prefix="/pronunciation", tags=["Pronunciation Exercise"])

from fastapi import FastAPI

# 1. Get a new word and display it
@router.get("/word")
async def get_pronunciation_word():
    word_pair = generate_pronunciation_word()
    display_on_lcd(word_pair["german"], word_pair["english"])
    return {
        "word_id": word_pair["id"],
        "german": word_pair["german"],
        "english": word_pair["english"]
    }

# 2. Record and transcribe audio
@router.post("/record")
async def record_pronunciation(file: UploadFile = File(...)):
    print("📦 Received audio file:", file.filename)
    try:
        contents = await file.read()
        with open("temp.webm", "wb") as f:
            f.write(contents)
        convert_webm_to_wav("temp.webm", "temp.wav")
        result = transcribe_audio_google("temp.wav", language_code="de-DE")
        if not result or not result.strip():
            raise HTTPException(status_code=400, detail="STT returned empty result")
        return {"recognized_text": result}
        
    except Exception as e:
        print("❌ Pronunciation STT error:", e)
        raise HTTPException(status_code=500, detail="STT failed")

# 3. Evaluate pronunciation
class PronunciationAttempt(BaseModel):
    word_id: str
    user_id: str
    target_word: str
    recognized_text: str

def generate_pronunciation_advice(target: str, actual: str) -> str:
    if target.lower() == actual.lower():
        return "Perfect pronunciation!"
    else:
        return f"Try again. You said '{actual}', but the target was '{target}'."

@router.post("/evaluate")
async def evaluate_pronunciation(attempt: PronunciationAttempt):
    print("📦 Evaluate payload:", attempt.dict())
    try: 
        score = evaluate_pronunciation_score(attempt.target_word, attempt.recognized_text)
        advice = generate_pronunciation_advice(attempt.target_word, attempt.recognized_text)
        return {"score": score, "advice": advice}
    except Exception as e:
        print("❌ Evaluation error:", e)
        raise HTTPException(status_code=500, detail="Evaluation failed")
    
    #return {"score": score, "advice": advice}

# 4. Finalize and save attempt
class FinalPronunciation(BaseModel):
    word_id: str
    user_id: str
    final_text: str
    score: float

@router.post("/finalize")
async def finalize_pronunciation(data: FinalPronunciation):
    save_pronunciation_score(data.user_id, data.score)
    return {"status": "saved"}
