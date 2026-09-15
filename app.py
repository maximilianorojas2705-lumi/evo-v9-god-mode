import os
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

@app.route("/")
def home():
    return "EVO V9 GOD MODE - LIVE - Con cerebro Groq", 200

@app.route("/health")
def health():
    return jsonify({"groq": bool(GROQ_KEY), "bot": bool(BOT_TOKEN)}), 200

@app.route("/telegram", methods=["POST"])
def telegram():
    try:
        data = request.get_json()
        chat_id = data.get("message", {}).get("chat", {}).get("id")
        text = data.get("message", {}).get("text", "")

        if chat_id and text and BOT_TOKEN:
            reply = f"Recibido: {text}"
            # Solo usa Groq si hay key
            if GROQ_KEY:
                try:
                    from groq import Groq
                    client = Groq(api_key=GROQ_KEY)
                    r = client.chat.completions.create(
                        model="llama-3.1-70b-versatile",
                        messages=[{"role": "user", "content": text}]
                    )
                    reply = r.choices[0].message.content
                except Exception as e:
                    reply = f"Estoy vivo pero Groq fallo: {e}"

            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                          json={"chat_id": chat_id, "text": reply})
    except Exception as e:
        print(f"Error: {e}")
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
