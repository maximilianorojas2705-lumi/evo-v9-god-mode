import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Carga segura de variables - si no existen no crashea
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
AFILIADO_LINK = os.getenv("AFILIADO_LINK", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

print(f"Bot iniciado. BOT_TOKEN cargado: {bool(BOT_TOKEN)}")

@app.route("/")
def home():
    return "EVO V9 GOD MODE - ONLINE", 200

@app.route("/health")
def health():
    return {"status": "ok", "version": "v9-god-mode"}, 200

# Webhook de Telegram
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if not BOT_TOKEN:
        return "no token", 400
    data = request.get_json()
    # Acá va tu lógica de agente autoevolutivo
    print(data)
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
