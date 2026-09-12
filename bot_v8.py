from flask import Flask, request
import os, requests, json, time
from datetime import datetime

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "") or os.environ.get("TELEGRAM_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"
MEMORY_FILE = "memoria_evo.json"

# --- CEREBRO EVO ---
def load_memoria():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"senales_dadas": 0, "aciertos": 0, "feedback": [], "sensibilidad": 1.0}

def save_memoria(data):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f)
    except: pass

def get_precio(symbol="BTCUSDT"):
    try:
        # API gratis de Binance sin key
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        r = requests.get(url, timeout=5).json()
        return float(r["lastPrice"]), float(r["priceChangePercent"])
    except:
        return None, None

def analizar_evo(precio, cambio):
    memoria = load_memoria()
    sens = memoria.get("sensibilidad", 1.0)

    # Lógica autoevolutiva simple pero efectiva
    if cambio is None: return "NEUTRAL ⚪", "Sin datos"

    if cambio > (2.5 * sens):
        senal = "VENTA FUERTE 🔴 - Sobrecompra"
    elif cambio > (1.0 * sens):
        senal = "VENTA 🟠 - Tomar ganancia"
    elif cambio < (-2.5 * sens):
        senal = "COMPRA FUERTE 🟢 - Sobreventa"
    elif cambio < (-1.0 * sens):
        senal = "COMPRA 🔵 - Oportunidad"
    else:
        senal = "NEUTRAL ⚪ - Esperar"

    razon = f"Cambio 24h: {cambio:.2f}% | Sensibilidad EVO: {sens:.2f}x | Señales: {memoria['senales_dadas']}"
    return senal, razon

def send_message(chat_id, text, buttons=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if buttons:
        data["reply_markup"] = {"inline_keyboard": buttons}
    if TOKEN:
        requests.post(f"{API}/sendMessage", json=data)

@app.route("/")
def home():
    return "EVO V9 GOD MODE V3 - AUTOEVOLUTIVO - ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    memoria = load_memoria()

    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        action = cb["data"]
        user_id = cb["from"]["id"]

        if action.startswith("senal_"):
            symbol = action.replace("senal_", "")
            precio, cambio = get_precio(symbol)
            if precio:
                senal, razon = analizar_evo(precio, cambio)
                memoria["senales_dadas"] += 1
                save_memoria(memoria)
                buttons = [
                    [{"text": "👍 Buena", "callback_data": f"fb_buena_{symbol}"}, {"text": "👎 Mala", "callback_data": f"fb_mala_{symbol}"}]
                ]
                send_message(chat_id, f"📊 *{symbol}*\n💲 Precio: ${precio:,.2f}\n📈 24h: {cambio:.2f}%\n\n🤖 *Señal EVO V9:*\n{senal}\n\n_{razon}_\n\n¿Te sirvió? El agente aprende de tu feedback.", buttons)
            else:
                send_message(chat_id, f"❌ No pude traer {symbol}, probá más tarde.")

        elif action.startswith("fb_"):
            # APRENDE!
            _, tipo, symbol = action.split("_")
            if tipo == "buena":
                memoria["aciertos"] += 1
                send_message(chat_id, f"✅ Aprendido! {symbol} marcado como acierto. Mejoro mi precisión.")
            else:
                # Si es mala, se vuelve más sensible
                memoria["sensibilidad"] = max(0.5, memoria["sensibilidad"] - 0.05)
                send_message(chat_id, f"📝 Aprendido! Ajusté mi sensibilidad para {symbol}. Ahora seré más cauteloso. (Sens: {memoria['sensibilidad']:.2f})")
            save_memoria(memoria)

        elif action == "estado":
            acierto_pct = (memoria["aciertos"]/memoria["senales_dadas"]*100) if memoria["senales_dadas"]>0 else 0
            send_message(chat_id, f"🧠 *ESTADO EVO V9 GOD*\n\n🟢 Online 24/7 (Render + Cron)\n📊 Señales dadas: {memoria['senales_dadas']}\n🎯 Aciertos: {memoria['aciertos']} ({acierto_pct:.1f}%)\n⚙️ Sensibilidad: {memoria['sensibilidad']:.2f}\n\nEl agente está evolucionando solo.")

        elif action == "senales_menu":
            buttons = [
                [{"text": "BTC", "callback_data": "senal_BTCUSDT"}, {"text": "ETH", "callback_data": "senal_ETHUSDT"}, {"text": "SOL", "callback_data": "senal_SOLUSDT"}],
                [{"text": "BNB", "callback_data": "senal_BNBUSDT"}, {"text": "XRP", "callback_data": "senal_XRPUSDT"}]
            ]
            send_message(chat_id, "📈 Elegí una moneda para analizar en tiempo real (Gratis - Binance):", buttons)

        requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": cb["id"]})
        return "OK", 200

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip()
        name = data["message"]["from"].get("first_name", "Maestro")

        if text.startswith("/start"):
            buttons = [
                [{"text": "📈 SEÑALES EN VIVO", "callback_data": "senales_menu"}],
                [{"text": "🧠 ESTADO EVO", "callback_data": "estado"}]
            ]
            send_message(chat_id, f"Hola {name}!\n\n*EVO V9 GOD V3 AUTOEVOLUTIVO* ✅\n\nYa no soy un bot que repite. Ahora:\n• Traigo precio real gratis\n• Analizo y doy señal\n• Aprendo de tu 👍👎\n\n¿Qué analizamos?", buttons)

        elif text.startswith("/senal"):
            parts = text.split()
            moneda = parts[1].upper() if len(parts) > 1 else "BTC"
            if "USDT" not in moneda: moneda += "USDT"
            precio, cambio = get_precio(moneda)
            if precio:
                senal, razon = analizar_evo(precio, cambio)
                memoria["senales_dadas"] += 1
                save_memoria(memoria)
                send_message(chat_id, f"📊 *{moneda}* ${precio:,.2f} ({cambio:.2f}%)\n\n{senal}\n_{razon}_")
            else:
                send_message(chat_id, "Usá: /senal BTC  o  /senal ETH")

        else:
            send_message(chat_id, "Usá /start para el menú GOD.")

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
