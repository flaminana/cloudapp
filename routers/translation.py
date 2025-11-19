from fastapi import APIRouter, HTTPException, UploadFile, Form
from fastapi.responses import JSONResponse
from services.google_stt import transcribe_audio_google
from services.openrouter import translate_text
from utils.tts import synthesize_audio
from models.schemas import TranslationResponse
from models.db import supabase
import uuid
import requests
import datetime
import os

router = APIRouter()

@router.get("/translate/process-latest")
async def process_latest_voice():
    try:
        response = supabase.table("translation_history") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="No translation history found")

        record = next((r for r in response.data if r.get("voice_input_url", "").startswith("http")), None)
        if not record:
            raise HTTPException(status_code=400, detail="No valid voice_input_url found")

        return process_supabase_record(record)

    except Exception as e:
        print("❌ Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/translate/audio", response_model=TranslationResponse)
async def translate_audio(
    file: UploadFile,
    direction: str = Form(...),  # "ENG-GER" or "GER-ENG"
    user_id: str = Form(...)
):
    # Save uploaded audio
    file_id = str(uuid.uuid4())
    input_path = f"static/audio/{file_id}_input.wav"
    output_path = f"static/audio/{file_id}_translated.wav"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # STT (German-only for now)
    original_text = transcribe_audio(input_path, direction)

    # Translation
    translated_text = translate_text(original_text, direction)

    # TTS
    synthesize_audio(translated_text, output_path, direction)

    # Save history to Supabase
    supabase.table("translation_history").insert({
        "user_id": user_id,
        "original_text": original_text,
        "translated_text": translated_text
    }).execute()

    # Return metadata
    return JSONResponse({
        "original_text": original_text,
        "translated_text": translated_text,
        "audio_url": f"https://cloudapp-1-ug0v.onrender.com/{output_path}"
    })

@router.post("/translate/text")
async def translate_text_only(
    text: str = Form(...),
    direction: str = Form(...),
    user_id: str = Form(...)
):
    translated = translate_text(text, direction)

    # Save to Supabase
    supabase.table("translation_history").insert({
        "user_id": user_id,
        "original_text": text,
        "translated_text": translated
    }).execute()

    return JSONResponse({
        "original_text": text,
        "translated_text": translated
    })

@router.get("/translate/history")
async def get_translation_history(user_id: str):
    response = supabase.table("translation_history").select("*").eq("user_id", user_id).execute()
    return response.data