<<<<<<< HEAD
from vosk import Model, KaldiRecognizer
import wave
import json

def transcribe_audio(file_path: str, direction: str) -> str:
    # Choose model based on direction
    if direction == "GER-ENG":
        model_path = "models/vosk-model-small-de-0.15"
    elif direction == "ENG-GER":
        model_path = "models/vosk-model-small-en-us-0.15"
    else:
        raise ValueError(f"Unsupported direction: {direction}")

    wf = wave.open(file_path, "rb")
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())

    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            partial_result = json.loads(rec.Result())
            result_text += partial_result.get("text", "") + " "

    return result_text.strip()
=======
from vosk import Model, KaldiRecognizer
import wave
import json

def transcribe_audio(file_path: str):
    wf = wave.open(file_path, "rb")
    model_path = "models/vosk-model-small-de-0.15"  # Update with your model path
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())

    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            partial_result = json.loads(rec.Result())
            result_text += partial_result.get("text", "") + " "

    return result_text.strip()
>>>>>>> 4daf35df3639cf69d5b0bd39ee5223fb11288d9b
