import os
from google.cloud import speech
import io

# Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/google_stt_key.json"

def transcribe_audio_google(wav_path, language_code="de-DE")-> str:
    
    print(f"📥 Transcribing file: {wav_path}")
    try:
        client = speech.SpeechClient()
        with open(wav_path, "rb") as audio_file:
            content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code
        )
        response = client.recognize(config=config, audio=audio)

        for result in response.results:
            print("🧠 Transcript:", result.alternatives[0].transcript)

        if not response.results:
            print("❌ No transcription results.")
            return ""

        return response.results[0].alternatives[0].transcript
        if not response.results:
            return ""
        return response.results[0].alternatives[0].transcript
    except Exception as e:
        print("❌ STT error:", e)
        raise
