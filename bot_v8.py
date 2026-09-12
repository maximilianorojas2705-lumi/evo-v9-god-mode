from flask import Flask, request
import os, requests, json

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "") or os.environ.get("TELEGRAM_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"
MEMORY_FILE = "memoria_evo.json"

def load_memoria():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"senales_dadas": 0, "aciertos": 0, "sensibilidad": 1.0}

def save_memoria(data):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f)
    except: pass

# MAPA para CoinGecko gratis
MAPA = {
    "BTCUSDT": "bitcoin", "ETHUSDT": "ethereum", "SOLUSDT": "solana",
    "BNBUSDT": "binancecoin", "XRPUSDT": "ripple", "BTC": "bitcoin", "ETH": "ethereum"
}

def get_precio(symbol="BTCUSDT"):
    try:
        coin_id = MAPA.get(symbol.upper(), "bitcoin")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=8).json()
        precio = r[coin_id]["usd"]
        cambio = r[coin_id].get("usd_24h_change", 0)
        return float(precio), float(cambio)
    except Exception as e:
        print(f"Error precio: {e}")
        return None, None

def analizar_evo(precio, cambio):
    memoria = load_memoria()
    sens = memoria.get("sensibilidad", 1.0)
    if cambio is None: return "NEUTRAL ⚪", "Sin datos"
    if cambio > (3.0 * sens): senal = "VENTA FUERTE 🔴 - Sobrecompra extrema"
    elif cambio > (1.2 * sens): senal = "VENTA 🟠 - Tomar ganancia"
    elif cambio < (-3.0 * sens): senal = "COMPRA FUERTE 🟢 - Sobreventa extrema"
    elif cambio < (-1.2 * sens): senal = "COMPRA 🔵 - Oportunidad"
    else: senal = "NEUTRAL ⚪ - Esperar, mercado lateral"
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
    return "EVO V9 GOD MODE V3.1 - COINGECKO - ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    memoria = load_memoria()

    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        action = cb["data"]

        if action.startswith("senal_"):
            symbol = action.replace("senal_", "")
            precio, cambio = get_precio(symbol)
            if precio:
                senal, razon = analizar_evo(precio, cambio)
                memoria["senales_dadas"] += 1
                save_memoria(memoria)
                buttons = [[{"text": "👍 Buena", "callback_data": f"fb_buena_{symbol}"}, {"text": "👎 Mala", "callback_data": f"fb_mala_{symbol}"}]]
                send_message(chat_id, f"📊 *{symbol}*\n💲 Precio: ${precio:,.2f}\n📈 24h: {cambio:.2f}%\n\n🤖 *Señal EVO V9:*\n{senal}\n\n_{razon}_\n\n¿Te sirvió? Toco 👍👎 y aprendo.", buttons)
            else:
                send_message(chat_id, f"❌ Error con {symbol}, probá de nuevo en 10 seg.")

        elif action.startswith("fb_"):
            _, tipo, symbol = action.split("_")
            if tipo == "buena":
                memoria["aciertos"] += 1
                send_message(chat_id, f"✅ Aprendido! {symbol} acierto guardado. Mejoro.")
            else:
                memoria["sensibilidad"] = max(0.5, memoria["sensibilidad"] - 0.05)
                send_message(chat_id, f"📝 Aprendido! Ajusté sensibilidad a {memoria['sensibilidad']:.2f} - seré más fino.")
            save_memoria(memoria)

        elif action == "estado":
            pct = (memoria["aciertos"]/memoria["senales_dadas"]*100) if memoria["senales_dadas"]>0 else 0
            send_message(chat_id, f"🧠 *ESTADO EVO V9*\n\n🟢 Online 24/7\n📊 Señales: {memoria['senales_dadas']}\n🎯 Aciertos: {memoria['aciertos']} ({pct:.1f}%)\n⚙️ Sens: {memoria['sensibilidad']:.2f}\n\nEvolucionando solo.")

        elif action == "senales_menu":
            buttons = [
                [{"text": "BTC", "callback_data": "senal_BTCUSDT"}, {"text": "ETH", "callback_data": "senal_ETHUSDT"}, {"text": "SOL", "callback_data": "senal_SOLUSDT"}],
                [{"text": "BNB", "callback_data": "senal_BNBUSDT"}, {"text": "XRP", "callback_data": "senal_XRPUSDT"}]
            ]
            send_message(chat_id, "📈 Elegí moneda (Precio real gratis - CoinGecko):", buttons)

        requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": cb["id"]})
        return "OK", 200

    if "message" in data and "message" in data:
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "").strip()
            name = data["message"]["from"].get("first_name", "Maestro")

            if text.startswith("/start"):
                buttons = [[{"text": "📈 SEÑALES EN VIVO", "callback_data": "senales_menu"}], [{"text": "🧠 ESTADO EVO", "callback_data": "estado"}]]
                send_message(chat_id, f"Hola {name}!\n\n*EVO V9 GOD V3.1 FIX* ✅\nAhora con CoinGecko (no se bloquea)\n\n¿Qué analizamos?", buttons)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
