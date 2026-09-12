from flask import Flask, request
import os
import requests

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "") or os.environ.get("TELEGRAM_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text, buttons=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if buttons:
        data["reply_markup"] = {"inline_keyboard": buttons}
    requests.post(f"{API}/sendMessage", json=data)

@app.route("/")
def home():
    return "EVO V9 GOD MODE RAWSON - ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}

    # Botones apretados
    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        action = cb["data"]

        if action == "estado":
            send_message(chat_id, "✅ *EVO V9 GOD MODE*\n\n🟢 Servidor: Render Free - ONLINE\n🟢 Webhook: Conectado\n📍 Rawson - Chubut\n\nTodo funcionando perfecto.")
        elif action == "senales":
            send_message(chat_id, "📈 *SEÑALES EVO V9*\n\nEscribí:\n`/senal BTC`\n`/senal ETH`\n`/senal SOL`\n\nPronto conectamos con Binance.")
        elif action == "ayuda":
            send_message(chat_id, "🆘 *AYUDA*\n\nComandos:\n/start - Menú\n/senal [moneda] - Ver señal\n/estado - Estado del servidor")

        # Responder al callback para sacar el relojito
        requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": cb["id"]})
        return "OK", 200

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        name = data["message"]["from"].get("first_name", "Maestro")

        if text.startswith("/start"):
            buttons = [
                [{"text": "📈 SEÑALES", "callback_data": "senales"}],
                [{"text": "🟢 ESTADO", "callback_data": "estado"}, {"text": "🆘 AYUDA", "callback_data": "ayuda"}]
            ]
            send_message(chat_id, f"Hola {name}! \n\n*EVO V9 GOD MODE ONLINE* ✅\n\n¿Qué querés hacer?", buttons)

        elif text.startswith("/estado"):
            send_message(chat_id, "✅ Servidor Render: ONLINE\n✅ Bot: @Maxxv9 funcionando\n✅ Región: Oregon")

        elif text.startswith("/senal"):
            moneda = text.replace("/senal","").strip().upper() or "BTC"
            send_message(chat_id, f"📊 Analizando {moneda}...\n\n🔜 Señal EVO V9: Esperando conexión a API de precios.\n\n(Próximo paso: conectamos Binance)")

        else:
            send_message(chat_id, f"Recibido: {text}\n\nUsá /start para ver el menú.")

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
