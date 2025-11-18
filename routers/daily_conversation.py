from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from models.schemas import DailyPrompt, STTResult, FinalAnswer, ScoreFeedback
from services.openrouter import generate_german_prompt
from services.google_stt import transcribe_audio_google
from services.audio_convert import convert_webm_to_wav
from services.evaluation import evaluate_fill_answer
from services.evaluation import prompt_cache
from models.db import save_qna_score
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/daily", tags=["Daily Conversation"])

# In-memory state (replace with DB/session for production)
user_state = {}

@router.get("/prompt", response_model=DailyPrompt)
async def get_prompt():
    try:
        prompt = generate_german_prompt()
        prompt_cache[prompt["id"]] = prompt["answer"]

        return DailyPrompt(prompt_id=prompt["id"], sentence=prompt["sentence"])
    except Exception as e:

        print("❌ /daily/prompt error:", e)
        raise HTTPException(status_code=500, detail=f"Failed to get prompt: {e}")

@router.post("/record")
async def record_audio(
    file: UploadFile = File(...),
    direction: str = Form("GER-ENG") #default fallback
):
    try:
        print("📥 Received file:", file.filename)
        contents = await file.read()

        with open("temp.webm", "wb") as f:
            f.write(contents)
        print("✅ Saved temp.webm")

        convert_webm_to_wav("temp.webm", "temp.wav")
        print("🔄 Converted to temp.wav")

        result = transcribe_audio_google("temp.wav", language_code="de-DE" if direction == "GER-ENG" else "en-US")
        print("🧠 Final transcription:", result)
        return {"recognized_text": result}
    
    except Exception as e:
        print("❌ STT error:", e)
        raise HTTPException(status_code=500, detail="STT failed")

@router.post("/finalize", response_model=ScoreFeedback)
async def finalize_answer(answer: FinalAnswer):
    try:
        print("📦 Finalize payload:", answer)

        if not answer.final_text.strip():
            raise HTTPException(status_code=400, detail="No speech detected. Please try again.")

        # Validate UUID format
        try:
            uuid.UUID(answer.user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format. Must be a UUID.")

        # Initialize score state
        if answer.user_id not in user_state:
            user_state[answer.user_id] = {"score": 0, "question": 0}

        result = evaluate_fill_answer(answer.prompt_id, answer.final_text)

        # Update score
        user_state[answer.user_id]["score"] += result["score"]
        user_state[answer.user_id]["question"] += 1

        # Save to Supabase if finished
        if user_state[answer.user_id]["question"] >= 5:
            try:
                save_qna_score(
                    answer.user_id,
                    correct=user_state[answer.user_id]["score"],
                    available=user_state[answer.user_id]["question"]
                )
            except Exception as e:
                print("❌ Supabase save error:", e)

        return ScoreFeedback(
            score=result["score"],
            feedback=result["feedback"],
            total_score=user_state[answer.user_id]["score"],
            question_number=user_state[answer.user_id]["question"],
            is_finished=user_state[answer.user_id]["question"] >= 5
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")