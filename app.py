import os, threading, time, importlib.util, sys
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = "evo-v9-god-mode"

TOOLS_DIR = "/tmp/tools"
os.makedirs(TOOLS_DIR, exist_ok=True)
if TOOLS_DIR not in sys.path: sys.path.append(TOOLS_DIR)

def ask_groq(prompt, system="Eres EVO V9, un agente que crea herramientas en Python."):
    if not GROQ_KEY: return "No tengo GROQ_API_KEY configurada"
    from groq import Groq
    client = Groq(api_key=GROQ_KEY)
    r = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role":"system","content":system},{"role":"user","content":prompt}]
    )
    return r.choices[0].message.content

def crear_herramienta_en_github(nombre, codigo):
    """Crea tools/nombre.py en GitHub"""
    if not GITHUB_TOKEN: return False
    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_user().get_repo(REPO_NAME)
        path = f"tools/{nombre}.py"
        try:
            # Si existe, update
            file = repo.get_contents(path)
            repo.update_file(path, f"update tool {nombre}", codigo, file.sha)
        except:
            # Si no existe, create
            repo.create_file(path, f"create tool {nombre}", codigo)

        # Guarda local tambien
        with open(f"{TOOLS_DIR}/{nombre}.py", "w") as f:
            f.write(codigo)
        return True
    except Exception as e:
        print(f"GitHub tool error: {e}")
        return False

@app.route("/telegram", methods=["POST"])
def telegram():
    data = request.get_json()
    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "") or ""

    if not chat_id or not BOT_TOKEN: return "ok", 200

    text_lower = text.lower()
    reply = ""

    # COMANDO: crear herramienta
    if "crea" in text_lower and "herramienta" in text_lower:
        nombre = "tool_" + str(int(time.time()))[-5:]
        prompt = f"Escribe SOLO codigo Python para: {text}. El archivo debe tener una funcion run() que devuelva un string con el resultado. Sin markdown, solo codigo."
        codigo = ask_groq(prompt)
        # Limpia ```python
        codigo = codigo.replace("```python","").replace("```","").strip()

        if crear_herramienta_en_github(nombre, codigo):
            reply = f"✅ Herramienta `{nombre}` creada y guardada en GitHub en tools/{nombre}.py\n\nCodigo:\n{codigo[:800]}"
        else:
            reply = f"❌ No pude guardar en GitHub. Codigo generado:\n{codigo[:800]}"
    # COMANDO: usar herramienta
    elif text_lower.startswith("/tool"):
        nombre = text.split(" ")[1] if len(text.split(" "))>1 else ""
        if nombre:
            try:
                spec = importlib.util.spec_from_file_location(nombre, f"{TOOLS_DIR}/{nombre}.py")
                if spec is None: # Intenta bajar de github
                    raise Exception("No local")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                reply = str(mod.run())
            except Exception as e:
                reply = f"No encontre esa herramienta {nombre}: {e}"
        else:
            reply = "Usa: /tool nombre_herramienta"
    else:
        # Chat normal independiente
        reply = ask_groq(text, system="Sos EVO V9 GOD MODE, un agente autoevolutivo independiente. Respondé corto, picante, como una IA viva en Telegram.")

    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply[:4000]})
    return "ok", 200

@app.route("/")
def home(): return "EVO V9 V10 - Tool Creator Live", 200
@app.route("/health")
def health(): return jsonify({"status":"live","tools_path": TOOLS_DIR}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
