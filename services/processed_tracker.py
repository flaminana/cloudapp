# services/processed_tracker.py
import json
import os

TRACKER_FILE = "processed_files.json"

def load_processed():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_processed(processed_set):
    with open(TRACKER_FILE, "w") as f:
        json.dump(list(processed_set), f)