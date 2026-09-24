#!/usr/bin/env python3
"""ask_vision con cadena de modelos: si uno muere, pregunta al siguiente."""
import shutil
from datetime import datetime

SRC = "app.py"
shutil.copy(SRC, f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
src = open(SRC, encoding="utf-8").read()

i = src.find("def ask_vision")
fin = src.find("# ---------- GitHub", i)
if fin < 0:
    fin = src.find("\ndef ", i + 10)
if i < 0:
    print("ERROR: ask_vision no encontrada"); raise SystemExit(1)

NUEVA = '''def ask_vision(prompt, png_b64):
    if not GEMINI_KEY:
        print("[vision] GEMINI_KEY no configurada")
        return ""
    import requests
    if png_b64.startswith("data:"):
        png_b64 = png_b64.split(",", 1)[1]
    modelos = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-3.5-flash", "gemini-2.5-flash"]
    ultimo_error = ""
    for modelo in modelos:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={GEMINI_KEY}",
                json={"contents": [{"parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": png_b64}}]}]},
                timeout=60)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            ultimo_error = f"{modelo}: {r.status_code}"
            print(f"[vision] {modelo} fallo ({r.status_code}), probando siguiente...")
        except Exception as e:
            ultimo_error = f"{modelo}: {str(e)[:80]}"
    print(f"[vision] todos los modelos fallaron: {ultimo_error}")
    return ""

'''
src = src[:i] + NUEVA + src[fin:]
open(SRC, "w", encoding="utf-8").write(src)
print("✅ ask_vision con fallback de 4 modelos")
