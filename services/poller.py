# services/poller.py
import time
import os
from threading import Thread
from supabase import create_client, Client
from services.processed_tracker import load_processed, save_processed
from services.translation_pipeline import process_supabase_record
from models.db import supabase

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def poll_supabase():
    while True:
        try:
            # 🔍 Get the latest 10 rows from translation_history
            response = supabase.table("translation_history") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(10) \
                .execute()

            # 🧠 Find the first row that has a voice_input_url but no voice_output_url
            for record in response.data:
                url = record.get("voice_input_url")
                if isinstance(url, str) and url.startswith("http") and not record.get("voice_output_url"):
                    print(f"🆕 Found unprocessed record: {record['id']}")
                    process_supabase_record(record)
                    break

        except Exception as e:
            print("❌ Polling error:", e)

        time.sleep(5)  # ⏱️ Wait before checking again