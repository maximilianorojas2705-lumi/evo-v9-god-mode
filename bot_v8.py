from flask import Flask, request
import os
import requests

app = Flask(__name__)

# Acepta BOT_TOKEN o TELEGRAM_TOKEN
TOKEN = os.environ.get("BOT_TOKEN", "") or os.environ.get("TELEGRAM_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/")
def home():
    return "EVO V9 GOD MODE RAWSON - ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        name = data["message"]["from"].get("first_name", "")

        if text == "/start":
            reply = f"Hola {name}! EVO V9 GOD MODE ONLINE ✅"
        else:
            reply = f"Recibido: {text}"

        if TOKEN:
            requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": reply})

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
