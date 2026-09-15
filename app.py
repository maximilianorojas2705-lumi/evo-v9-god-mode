import os, sys, time, traceback
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROQ_KEY = os.getenv("GROQ_API_KEY", "").strip()

print(f"=== DEBUG BOT START ===")
print(f"BOT_TOKEN set: {bool(BOT_TOKEN)} len={len(BOT_TOKEN)}")
print(f"GROQ set: {bool(GROQ_KEY)}")
if BOT_TOKEN:
    print(f"BOT_TOKEN empieza con: {BOT_TOKEN[:6]}...")

def send_telegram(chat_id, text):
    if not BOT_TOKEN or not chat_id:
        print(f"NO PUEDO ENVIAR: token={bool(BOT_TOKEN)} chat={chat_id}")
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": chat_id, "text": text[:4000]}, timeout=10)
        print(f"Telegram send: {r.status_code} {r.text[:200]}")
        return r.ok
    except Exception as e:
        print(f"ERROR send_telegram: {e} {traceback.format_exc()}")
        return False

@app.route("/")
def home():
    return "EVO V9 DEBUG - Telegram debe responder", 200

@app.route("/health")
def health():
    return jsonify({"bot": bool(BOT_TOKEN), "groq": bool(GROQ_KEY), "token_len": len(BOT_TOKEN)}), 200

@app.route("/telegram", methods=["POST"])
def telegram():
    try:
        print("=== LLEGO MENSAJE TELEGRAM ===")
        data = request.get_json(force=True)
        print(f"DATA: {data}")

        msg = data.get("message", {}) or data.get("edited_message", {})
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "") or ""
        print(f"chat_id={chat_id} text={text}")

        if not chat_id:
            return "ok", 200

        # Respuesta 100% blindada que siempre funciona
        reply = f"✅ ESTOY VIVO! Recibí: {text}\n\nBot funcionando en Render Live."

        # Intenta Groq solo si hay key, pero si falla no rompe
        if GROQ_KEY and text:
            try:
                from groq import Groq
                client = Groq(api_key=GROQ_KEY)
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"user","content": text}]
                )
                reply = completion.choices[0].message.content
                print(f"Groq OK: {reply[:100]}")
            except Exception as e:
                print(f"Groq FAIL (pero sigo vivo): {e}")
                reply += f"\n\n(Nota: Groq falló: {e} - pero el bot está vivo)"

        send_telegram(chat_id, reply)

    except Exception as e:
        print(f"ERROR TOTAL en /telegram: {e} {traceback.format_exc()}")

    return "ok", 200

@app.route("/set_webhook")
def set_webhook():
    """Entra a https://evo-v9-god-service.onrender.com/set_webhook para setearlo sin usar api.telegram.org"""
    if not BOT_TOKEN:
        return "Falta BOT_TOKEN", 500
    url = f"https://evo-v9-god-service.onrender.com/telegram"
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={url}")
    return r.text, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
