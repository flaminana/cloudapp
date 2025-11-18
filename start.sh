#!/bin/bash
echo "🚀 Starting cloudapp..."

# ✅ Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$PYTHON_VERSION" != "3.11" ]]; then
  echo "❌ Python $PYTHON_VERSION detected. Render is ignoring runtime.txt."
  echo "Please ensure Python 3.11 is selected in render.yaml or runtime.txt."
  exit 1
fi

# ✅ Optional: activate virtualenv if needed
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

# ✅ Download Vosk model if needed
python3 download_model.py

# ✅ Start FastAPI app
uvicorn main:app --host 0.0.0.0 --port 10000