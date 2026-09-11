from flask import Flask, request
import os
import requests

app = Flask(__name__)
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
        name = data["message"]["from"].get("first_name", "")
        if text == "/start":
            msg = f"Hola {name}! EVO V9 GOD MODE RAWSON ONLINE ✅"
        else:
            msg = f"Recibido: {text}"
        if TOKEN:
            requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": msg})
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
