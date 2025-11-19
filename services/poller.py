# services/poller.py
import time
from threading import Thread
from supabase import create_client, Client
from services.processed_tracker import load_processed, save_processed
from services.translation_pipeline import process_audio_file  # You’ll define this

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def poll_supabase():
    processed = load_processed()

    while True:
        try:
            response = supabase.storage.from_("voice-recordings").list("English")  # or "German"
            files = response or []

            for file in files:
                name = file["name"]
                if name.endswith(".wav") and name not in processed:
                    print(f"🆕 New file detected: {name}")
                    process_audio_file(name)
                    processed.add(name)
                    save_processed(processed)

        except Exception as e:
            print("❌ Polling error:", e)

        time.sleep(5)