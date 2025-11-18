#!/bin/bash
echo "🚀 Starting cloudapp..."

# Download Vosk model if needed
python download_model.py

# Start the FastAPI app
uvicorn main:app --host 0.0.0.0 --port 10000