import os
from google.cloud import speech
import io
from pydub import AudioSegment
from google.oauth2 import service_account
import json

# 🔤 Map user-facing codes to valid Google STT language codes
LANGUAGE_CODE_MAP = {
    "GER-ENG": "de-DE",
    "ENG": "en-US",
    "JPN": "ja-JP",
    "MS": "ms-MY",
    "DE": "de-DE",
    "EN": "en-US",
    "GER": "de-DE",
    "GERMAN": "de-DE",
    "ENGLISH": "en-US",
}

# Set credentials
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/google_stt_key.json"

def convert_to_mono(input_path, output_path):
    audio = AudioSegment.from_wav(input_path)
    mono_audio = audio.set_channels(1)
    mono_audio.export(output_path, format="wav")


def transcribe_audio_google(wav_path, language_code="de-DE")-> str:
    print(f"📥 Transcribing file: {wav_path}")
    try:
        #Normalise langauge code
        language_code = LANGUAGE_CODE_MAP.get(language_code.upper(), "en-US")
        print(f"🔍 Using language_code: {language_code}")

        key_data = os.environ.get("GOOGLE_STT_KEY_JSON")
        if not key_data:
            raise RuntimeError("Missing GOOGLE_STT_KEY_JSON in environment")

        credentials = service_account.Credentials.from_service_account_info(json.loads(key_data))
        client = speech.SpeechClient(credentials=credentials)

        with open(wav_path, "rb") as audio_file:
            content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        print(f"🔍 Using language_code: {language_code}")
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            #sample_rate_hertz=16000,
            language_code=language_code
        )
        response = client.recognize(config=config, audio=audio)

        for result in response.results:
            print("🧠 Transcript:", result.alternatives[0].transcript)

        if not response.results:
            print("❌ No transcription results.")
            return ""

        return response.results[0].alternatives[0].transcript
        
    except Exception as e:
        print("❌ STT error:", e)
        raise
