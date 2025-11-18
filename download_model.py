import os, zipfile, requests
from tqdm import tqdm

MODEL_DIR = "models"
MODEL_NAME = "vosk-model-de-0.21"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)
ZIP_PATH = os.path.join(MODEL_DIR, f"{MODEL_NAME}.zip")
MODEL_URL = f"https://alphacephei.com/vosk/models/{MODEL_NAME}.zip"

if os.path.exists(MODEL_PATH):
    print("✅ Vosk model already exists. Skipping download.")
else:
    os.makedirs(MODEL_DIR, exist_ok=True)
    print("⬇️ Downloading Vosk model...")

    try:
        with requests.get(MODEL_URL, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            with open(ZIP_PATH, "wb") as f, tqdm(
                desc="⬇️ Downloading",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
    except Exception as e:
        print("❌ Download failed:", e)
        exit(1)

    print("📦 Extracting model...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(MODEL_DIR)

    os.remove(ZIP_PATH)
    print("✅ Model ready.")