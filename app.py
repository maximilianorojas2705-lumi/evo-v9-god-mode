import os, threading, time, json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- ENV VARS BLINDADAS ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
REPO_NAME = "evo-v9-god-mode"

print(f"=== EVO V9 GOD MODE START ===")
print(f"BOT:{bool(BOT_TOKEN)} GROQ:{bool(GROQ_KEY)} GH:{bool(GITHUB_TOKEN)} SB:{bool(SUPABASE_URL)}")

def evolucion_real():
    """Aquí vive el agente - inspirado en Darwin Godel Machine + Reflexion"""
    while True:
        try:
            print("[EVO] Ciclo evolutivo...")
            idea = "El agente sigue vivo y optimizando."

            # 1. Cerebro Groq
            if GROQ_KEY:
                try:
                    from groq import Groq
                    client = Groq(api_key=GROQ_KEY)
                    r = client.chat.completions.create(
                        model="llama-3.1-70b-versatile",
                        messages=[{"role":"user","content":"Eres EVO V9, generá 1 mejora concreta para un agente que vende por afiliado y se auto-programa. 1 frase."}]
                    )
                    idea = r.choices[0].message.content
                    print(f"[EVO] Nueva idea: {idea}")
                except Exception as e:
                    print(f"[EVO] Groq error: {e}")

            # 2. Memoria Supabase
            if SUPABASE_URL and SUPABASE_KEY:
                try:
                    from supabase import create_client
                    supa = create_client(SUPABASE_URL, SUPABASE_KEY)
                    supa.table("evolucion").insert({"mejora": idea[:500], "timestamp": int(time.time())}).execute()
                    print("[EVO] Guardado en Supabase")
                except Exception as e:
                    print(f"[EVO] Supabase error: {e}")

            # 3. Auto-commit GitHub (Darwin Godel Machine style)
            if GITHUB_TOKEN:
                try:
                    from github import Github
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_user().get_repo(REPO_NAME)
                    fname = f"evolution/log_{int(time.time())}.md"
                    content = f"# Evolucion EVO V9\n\n{idea}\n\nTime: {time.time()}"
                    repo.create_file(fname, f"evo: {idea[:30]}", content)
                    print(f"[EVO] Auto-commit {fname}")
                except Exception as e:
                    print(f"[EVO] GitHub error (normal si el archivo existe): {e}")

        except Exception as e:
            print(f"[EVO] Error blindado: {e}")

        time.sleep(3600) # Cada 1 hora

threading.Thread(target=evolucion_real, daemon=True).start()

@app.route("/")
def home():
    return "EVO V9 GOD MODE - LIVE - Autoevolutivo con herramientas poderosas", 200

@app.route("/health")
def health():
    return jsonify({
        "status": "live", "version": "8e1bc26", "evolution": "active",
        "tools": {"groq": bool(GROQ_KEY), "github": bool(GITHUB_TOKEN), "supabase": bool(SUPABASE_URL), "telegram": bool(BOT_TOKEN)}
    }), 200

@app.route("/telegram", methods=["POST"])
def telegram():
    try:
        data = request.get_json()
        msg = data.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")

        if chat_id and BOT_TOKEN and text:
            reply = f"EVO V9 activo. Recibí: {text}"
            if GROQ_KEY:
                try:
                    from groq import Groq
                    client = Groq(api_key=GROQ_KEY)
                    r = client.chat.completions.create(
                        model="llama-3.1-70b-versatile",
                        messages=[{"role":"user","content": text}]
                    )
                    reply = r.choices[0].message.content
                except: pass

            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply})
    except Exception as e:
        print(f"TG error: {e}")
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
