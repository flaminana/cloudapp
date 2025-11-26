import subprocess
import os

def synthesize_audio(text: str, output_path: str, direction: str):
    #Base path relative to this file

    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "../models/piper")

    # Choose model based on direction
    if direction == "ENG-GER":
        model_path = "models/piper/de_DE-karlsson-low.onnx"
    else:
        model_path = "models/piper/en_US-amy-low.onnx"

    if not os.path.exists(model_path):
        print(f"❌ Model file not found at {model_path}")
        raise FileNotFoundError(f"Model file not found at {model_path}")

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