import subprocess
import os

def synthesize_audio(text: str, output_path: str, direction: str):
    # Choose model based on direction
    if direction == "ENG-GER":
        model_path = "models/piper/de_DE-karlsson-low.onnx"
    else:
        model_path = "models/piper/en_US-amy-low.onnx"

    command = [
        "piper",
        "--model", model_path,
        "--output_file", output_path,
        "--text", text
    ]
    print(f"🔊 Synthesizing with {model_path}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ TTS synthesis failed:", e)
        raise Exception("TTS synthesis failed")