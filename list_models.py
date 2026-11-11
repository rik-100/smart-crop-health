import os
import google.generativeai as genai

genai.configure(api_key='AIzaSyBCpGep6jX8VMAbD-h0R7ctwOoMuoiLliQ')
models = [m.name for m in genai.list_models()]
with open("models.txt", "w", encoding="utf-8") as f:
    for m in models:
        f.write(m + "\n")
