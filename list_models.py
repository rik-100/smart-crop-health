import os

from google import genai
from dotenv import load_dotenv

# Never hard-code API keys: read GEMINI_API_KEY from the environment / .env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY is not set. Add it to .env or your environment.")

client = genai.Client(api_key=api_key)
models = [m.name for m in client.models.list()]
with open("models.txt", "w", encoding="utf-8") as f:
    for m in models:
        f.write(m + "\n")
