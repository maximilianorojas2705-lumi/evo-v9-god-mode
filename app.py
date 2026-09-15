import os, threading, time, json
from flask import Flask, request
import requests
from groq import Groq
from github import Github
from supabase import create_client

app = Flask(__name__)

# --- CONFIG SEGURA ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "maximilianorojas2705-lumi")
REPO_NAME = "evo-v9-god-mode"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def evolucionar():
    """Este es el loop que vive solo, cada 1 hora se mejora a si mismo"""
    while True:
        try:
            print(">>> [EVO] Iniciando ciclo de auto-evolución...")
            # 1. Lee memoria de Supabase
            memoria = ""
            if supabase:
                try:
                    data = supabase.table("evolucion").select("*").order("id", desc=True).limit(3).execute()
                    memoria = str(data.data)
                except: pass

            # 2. Le pide a Groq que se mejore
            prompt = f"""
            Sos EVO V9 GOD MODE. Tu objetivo es auto-mejorarte.
            Memoria pasada: {memoria}
            Herramientas disponibles: search_web(), write_file(), github_commit(), supabase_save()
            Genera una mejora concreta para app.py. Solo responde con la mejora en formato JSON:
            {{"mejora": "descripcion", "codigo_python": "codigo"}}
            """

            if groq_client:
                resp = groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                mejora = resp.choices[0].message.content
                print(f">>> [EVO] Mejora propuesta: {mejora[:500]}")

                # 3. Guarda en Supabase como memoria
                if supabase:
                    supabase.table("evolucion").insert({"mejora": mejora[:1000]}).execute()

                # 4. Autocommit a GitHub (Darwin Godel Machine style)
                if GITHUB_TOKEN:
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_user().get_repo(REPO_NAME)
                    # Aquí se auto-escribe una nueva herramienta
                    # Por seguridad solo crea un archivo nuevo, no se sobreescribe a si mismo
                    repo.create_file(f"tools/auto_tool_{int(time.time())}.py", f"auto mejora {time.time()}", mejora[:2000])
                    print(">>> [EVO] Autocommit realizado!")

        except Exception as e:
            print(f">>> [EVO] Error en evolución: {e}")

        time.sleep(3600) # Evoluciona cada 1 hora

# Iniciar el hilo evolutivo en background para que no frene la web
threading.Thread(target=evolucionar, daemon=True).start()

@app.route("/")
def home():
    return "EVO V9 GOD MODE LIVE - Agente autoevolutivo corriendo", 200

@app.route("/health")
def health():
    return {"status": "live", "evolution": "active"}, 200

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.json
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    text = data.get("message", {}).get("text", "")

    if chat_id and BOT_TOKEN:
        # Respuesta con Groq
        if groq_client:
            ia = groq_client.chat.completions.create(model="llama-3.1-70b-versatile", messages=[{"role":"user","content":text}])
            respuesta = ia.choices[0].message.content
        else:
            respuesta = f"EVO V9 recibió: {text}. Estoy evolucionando..."

        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": respuesta})

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
