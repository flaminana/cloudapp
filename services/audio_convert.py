<<<<<<< HEAD
import subprocess

def convert_webm_to_wav(input_path: str, output_path: str):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", output_path
=======
import subprocess

def convert_webm_to_wav(input_path: str, output_path: str):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", output_path
>>>>>>> 4daf35df3639cf69d5b0bd39ee5223fb11288d9b
    ], check=True)