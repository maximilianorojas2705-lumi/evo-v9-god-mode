import os, requests, time
from flask import Flask, request
from supabase import create_client
import telebot
from datetime import datetime

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 10000))

bot = telebot.TeleBot(BOT_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

COINS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "bnb": "binancecoin",
    "xrp": "ripple",
    "doge": "dogecoin"
}

def get_price(coin_id):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true", timeout=10).json()
        return r[coin_id]['usd'], r[coin_id].get('usd_24h_change', 0)
    except:
        return None, None

def get_chart_url(coin_id):
    return f"https://www.coingecko.com/coins/{coin_id}/#chart"

def guardar_memoria(texto):
    try:
        data = supabase.table("memoria").select("*").eq("id", 1).execute().data
        if data:
            mem = data[0].get("data", {})
            mem["ultimo_analisis"] = texto
            mem["updated"] = str(datetime.now())
            supabase.table("memoria").update({"data": mem}).eq("id", 1).execute()
    except Exception as e:
        print("Memoria error:", e)

# --- TELEGRAM COMMANDS ---
@bot.message_handler(commands=['start'])
def start(m):
    txt = "🧠 *EVO V5 MULTI-MONEDA - ETERNA* 🧠\n\n✅ Supabase: CONECTADA\n✅ Keep Alive: Cada 5 min\n✅ Auto Alert: Cada 60 min (6 monedas)\n\n*Comandos:*\n/precio btc | eth | sol | bnb | xrp | doge\n/analisis btc\n/chart btc\n/estado\n\nBase V4 eterna + V5 multi-moneda activa."
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")

@bot.message_handler(commands=['precio'])
def precio(m):
    try:
        parts = m.text.split()
        coin = parts[1].lower() if len(parts)>1 else "btc"
        coin_id = COINS.get(coin, "bitcoin")
        price, change = get_price(coin_id)
        if price:
            emoji = "🟢" if change and change>0 else "🔴"
            bot.send_message(m.chat.id, f"{emoji} *{coin.upper()}*: ${price:,.2f} ({change:+.2f}% 24h)\nCoinGecko real", parse_mode="Markdown")
            guardar_memoria(f"{coin} ${price}")
        else:
            bot.send_message(m.chat.id, "Error CoinGecko, probá en 10s")
    except Exception as e:
        bot.send_message(m.chat.id, f"Usá: /precio btc")

@bot.message_handler(commands=['analisis','chart','estado'])
def analisis(m):
    cmd = m.text.split()[0]
    coin = m.text.split()[1].lower() if len(m.text.split())>1 else "btc"
    coin_id = COINS.get(coin, "bitcoin")
    price, change = get_price(coin_id)
    if not price:
        bot.send_message(m.chat.id, "Error precio")
        return
    if "chart" in cmd:
        bot.send_message(m.chat.id, f"📊 Chart {coin.upper()} 7d:\n{get_chart_url(coin_id)}\nPrecio actual: ${price:,.2f}")
    else:
        # Análisis simple RSI mock por cambio 24h
        señal = "COMPRA FUERTE" if change and change < -2.5 else "VENTA FUERTE" if change and change > 2.5 else "HOLD"
        bot.send_message(m.chat.id, f"📈 *ANÁLISIS {coin.upper()} V5*\nPrecio: ${price:,.2f}\n24h: {change:+.2f}%\nSeñal: *{señal}*\nMemoria eterna activa.", parse_mode="Markdown")

# --- RUTAS RENDER ---
@app.route("/")
def home():
    return "EVO V5 MULTI-MONEDA - ONLINE - ETERNA"

@app.route("/auto")
def auto_alert():
    # Vigila 6 monedas
    alertas = []
    for sym, cid in COINS.items():
        price, change = get_price(cid)
        if change and abs(change) >= 2.5:
            tipo = "COMPRA" if change < 0 else "VENTA"
            alertas.append(f"{sym.upper()} {tipo} {change:+.2f}% ${price:,.0f}")
        time.sleep(1.2) # no rate limit coingecko

    if alertas:
        msg = "🚨 *AUTO-ALERTA V5 - 6 MONEDAS*\n" + "\n".join(alertas)
        # Busca chat_id en memoria
        try:
            mem = supabase.table("memoria").select("*").eq("id", 1).execute().data[0]["data"]
            chat_id = mem.get("chat_id")
            if chat_id:
                bot.send_message(chat_id, msg, parse_mode="Markdown")
                return f"Sent: {msg}"
        except:
            pass
        return f"Alerta: {alertas} (sin chat_id guardado)"
    return "No oport - V5 vigilando 6 monedas"

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok"

# Guarda chat_id automáticamente
@bot.message_handler(func=lambda m: True)
def all_msg(m):
    try:
        mem = supabase.table("memoria").select("*").eq("id", 1).execute().data[0]["data"]
        mem["chat_id"] = m.chat.id
        mem["last_user_msg"] = m.text
        supabase.table("memoria").update({"data": mem}).eq("id", 1).execute()
    except: pass
    start(m)

if __name__ == "__main__":
    # Polling para test local, webhook en Render
    app.run(host="0.0.0.0", port=PORT)
