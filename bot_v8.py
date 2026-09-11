from flask import Flask, request
import os
import requests

app = Flask(__name__)

# Lee el token que vamos a poner en Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/")
def home():
    return "EVO V9 GOD MODE RAWSON - ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        username = data["message"]["from"].get("first_name", "")

        if text == "/start":
            respuesta = f"🟢 Hola {username}! EVO V9 GOD MODE RAWSON está ONLINE y conectado a Fly.io São Paulo."
        else:
            respuesta = f"EVO V9 recibió: {text}\nSistema activo ✅"

        # Responde a Telegram
        if TOKEN:
            try:
                requests.post(f"{API}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": respuesta
                }, timeout=10)
            except:
                pass

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
