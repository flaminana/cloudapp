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
        # 1. Get latest record with voice_input_url
        response = supabase.table("translation_history") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute()
        
        #print("🧾 All rows:")
        #for r in response.data:
            #print(f"ID: {r['id']} | Created: {r['created_at']} | URL: {r['voice_input_url']}")

        if not response.data:
            raise HTTPException(status_code=404, detail="No translation history found")

        # Find the first valid row with a usable voice_input_url
        record = None
        for r in response.data:
            url = r.get("voice_input_url")
            if url and isinstance(url, str) and url.startswith("http"):
                record = r
                print(f"✅ Selected ID: {record['id']} | URL: {record['voice_input_url']}")
                break

        if not record:
            raise HTTPException(status_code=400, detail="No valid voice_input_url found in recent rows")

        history_id = record["id"]
        user_id = record["user_id"]
        direction = record["direction"]
        input_url = record["voice_input_url"]

        # Normalize direction from Supabase
        if direction == "de_to_en":
            direction = "GER-ENG"
        elif direction == "en_to_de":
            direction = "ENG-GER"

        #print(f"📥 Processing ID: {history_id} | URL: {input_url}")

        # 2. Download input audio
        wav_data = requests.get(input_url).content
        input_path = "temp_input.wav"
        with open(input_path, "wb") as f:
            f.write(wav_data)

        # ✅ Convert stereo to mono
        from utils.audio_utils import convert_to_mono  # or wherever you define it
        mono_path = "temp_input_mono.wav"
        convert_to_mono(input_path, mono_path)

        # 3. STT using mono file
        original_text = transcribe_audio_google(mono_path, direction)

        # 4. Translate
        translated_text = translate_text(original_text, direction)

        # 5. TTS
        output_path = f"temp_output.wav"
        synthesize_audio(translated_text, output_path, direction)

        # 6. Upload output audio to Supabase Storage
        with open(output_path, "rb") as f:
            processed_wav = f.read()

        timestamp = datetime.datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        output_key = f"translated/{user_id}_{timestamp}.wav"

        upload_response = supabase.storage.from_("voice-recordings") \
            .upload(output_key, processed_wav, {
                "content-type": "audio/wav",
                "upsert": "true"
            })

        if hasattr(upload_response, "status_code") and upload_response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Upload failed with status {upload_response.status_code}")

        # 7. Get public URL
        public_url = supabase.storage.from_("voice-recordings") \
            .get_public_url(output_key)
        output_url = public_url

        # 8. Update Supabase row
        supabase.table("translation_history") \
            .update({
                "original_text": original_text,
                "translated_text": translated_text,
                "voice_output_url": output_url
            }) \
            .eq("id", history_id) \
            .execute()

        return {
            "history_id": history_id,
            "original_text": original_text,
            "translated_text": translated_text,
            "voice_input_url": input_url,
            "voice_output_url": output_url
        }

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