import os
import gdown

# Resolve relative to the repo root so the model lands where backend/app.py
# loads it from, regardless of the current working directory.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "best_model.h5")
MODEL_URL = "https://drive.google.com/uc?export=download&id=1IEKhFUE3xHpXeHpU8OtSIjKFf3yzVu6k"


def download_model_if_not_exists():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model...")
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        tmp_path = MODEL_PATH + ".part"
        # Download to a temp file first so an interrupted download doesn't
        # leave a truncated best_model.h5 that crashes every later start-up.
        result = gdown.download(MODEL_URL, tmp_path, quiet=False)
        if not result or not os.path.exists(tmp_path):
            raise RuntimeError("Model download failed")
        os.replace(tmp_path, MODEL_PATH)
        print("Model downloaded successfully!")
    else:
        print("Model already exists.")
