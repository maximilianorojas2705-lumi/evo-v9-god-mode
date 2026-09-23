#!/usr/bin/env python3
"""Cambia ask_vision para usar Gemini en vez de Groq (más robusto para visión)."""
import shutil
from datetime import datetime

SRC = "app.py"
shutil.copy(SRC, f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
print("backup creado")

src = open(SRC, encoding="utf-8").read()

# Buscar ask_vision
i = src.find("def ask_vision")
j = src.find("\n\n", i + 10)  # siguiente doble salto de línea
if i < 0:
    print("ERROR: ask_vision no encontrada")
    raise SystemExit(1)

# Nueva implementación con Gemini
NUEVA_FUNCION = '''def ask_vision(prompt, png_b64):
    if not GEMINI_API_KEY:
        print("[vision] GEMINI_API_KEY no configurada")
        return ""
    try:
        import requests
        # Extraer solo el base64 (sin el data:image/... prefix si existe)
        if png_b64.startswith("data:"):
            png_b64 = png_b64.split(",", 1)[1]
        
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/png", "data": png_b64}}
                    ]
                }]
            },
            timeout=60
        )
        
        if r.status_code == 200:
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"[vision] Gemini error {r.status_code}: {r.text[:100]}")
            return ""
    except Exception as e:
        print(f"[vision] error: {str(e)[:150]}")
        return ""
'''

src = src[:i] + NUEVA_FUNCION + src[j:]
open(SRC, "w", encoding="utf-8").write(src)
print("✅ ask_vision cambiada a Gemini")
