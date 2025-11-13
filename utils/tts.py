import subprocess

def synthesize_audio(text: str, output_path: str):
    with open("temp.txt", "w", encoding="utf-8") as f:
        f.write(text)
    subprocess.run([
        "piper",
        "--model", "models/piper/de_piper.onnx",
        "--input", "temp.txt",
        "--output", output_path
    ])