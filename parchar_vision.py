#!/usr/bin/env python3
"""Agrega endpoint /vision a app.py: seguro, idempotente, posicion correcta."""
import shutil
from datetime import datetime

SRC = "app.py"
shutil.copy(SRC, f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
print("backup creado")
src = open(SRC, encoding="utf-8").read()

if '@app.route("/vision"' in src:
    print("endpoint /vision ya existe, no se toca nada")
    raise SystemExit

# 1) Detectar si ask_vision ya arma el data URI internamente
i = src.find("def ask_vision")
j = src.find("\ndef ", i + 10)
bloque = src[i:j if j > 0 else len(src)]
arma_uri = "data:image" in bloque
print(f"ask_vision arma data URI internamente: {arma_uri}")
prefijo = "" if arma_uri else '    if not image_b64.startswith("data:"):\n        image_b64 = "data:image/png;base64," + image_b64\n'

ENDPOINT = '''
# ---------- Endpoint de vision para el agente de vision ----------
@app.route("/vision", methods=["POST"])
def vision_endpoint():
    """Analiza un screenshot y decide la siguiente accion."""
    data = request.get_json(silent=True) or {}
    image_b64 = (data.get("image") or "").strip()
    prompt = data.get("prompt") or "Describe esta pantalla y que accion seguir."
    if not image_b64:
        return jsonify({"error": "falta image"}), 400
''' + prefijo + '''    try:
        respuesta = ask_vision(prompt, image_b64)
    except Exception as e:
        return jsonify({"error": f"vision fallo: {e}"}), 500
    return jsonify({"answer": respuesta})
'''

# 2) Insertar ANTES del bloque __main__ si existe; si no, al final
k = src.find("if __name__")
if k > 0:
    src = src[:k] + ENDPOINT + "\n" + src[k:]
    print("endpoint insertado ANTES del bloque __main__ (correcto)")
else:
    src = src.rstrip() + "\n" + ENDPOINT
    print("endpoint agregado al final (no hay bloque __main__)")

open(SRC, "w", encoding="utf-8").write(src)
print("app.py reescrito")
