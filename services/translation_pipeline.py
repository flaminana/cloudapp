# services/translation_pipeline.py
import datetime
import requests
from services.google_stt import transcribe_audio_google
from services.openrouter import translate_text
from utils.tts import synthesize_audio
from utils.audio_utils import convert_to_mono
from models.db import supabase

def process_supabase_record(record: dict) -> dict:
    try:
        history_id = record["id"]
        user_id = record["user_id"]
        direction = record["direction"]
        input_url = record["voice_input_url"]

        if direction == "de_to_en":
            direction = "GER-ENG"
        elif direction == "en_to_de":
            direction = "ENG-GER"

        wav_data = requests.get(input_url).content
        input_path = "temp_input.wav"
        with open(input_path, "wb") as f:
            f.write(wav_data)

        mono_path = "temp_input_mono.wav"
        convert_to_mono(input_path, mono_path)

        original_text = transcribe_audio_google(mono_path, direction)
        translated_text = translate_text(original_text, direction)

        output_path = f"temp_output.wav"
        synthesize_audio(translated_text, output_path, direction)

        with open(output_path, "rb") as f:
            processed_wav = f.read()

        timestamp = datetime.datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        output_key = f"translated/{user_id}_{timestamp}.wav"

        supabase.storage.from_("voice-recordings").upload(
            output_key, processed_wav, {
                "content-type": "audio/wav",
                "upsert": "true"
            })

        output_url = supabase.storage.from_("voice-recordings").get_public_url(output_key)

        supabase.table("translation_history").update({
            "original_text": original_text,
            "translated_text": translated_text,
            "voice_output_url": output_url
        }).eq("id", history_id).execute()

        return {
            "history_id": history_id,
            "original_text": original_text,
            "translated_text": translated_text,
            "voice_input_url": input_url,
            "voice_output_url": output_url
        }

    except Exception as e:
        print("❌ Error in process_supabase_record:", e)
        return {"error": str(e)}