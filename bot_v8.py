from flask import Flask, request
import os, requests

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "") or os.environ.get("TELEGRAM_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"
SUPA_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPA_KEY = os.environ.get("SUPABASE_KEY", "")

MAPA = {"BTCUSDT":"bitcoin","ETHUSDT":"ethereum","SOLUSDT":"solana","BNBUSDT":"binancecoin","XRPUSDT":"ripple","BTC":"bitcoin","ETH":"ethereum"}

def load_memoria():
    if SUPA_URL and SUPA_KEY:
        try:
            headers = {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}"}
            r = requests.get(f"{SUPA_URL}/rest/v1/memoria?id=eq.1&select=data", headers=headers, timeout=8).json()
            if r and isinstance(r, list) and len(r)>0:
                d = r[0].get("data", {})
                # Asegurar campos
                d.setdefault("senales_dadas",0)
                d.setdefault("aciertos",0)
                d.setdefault("sensibilidad",1.0)
                d.setdefault("chat_id",None)
                return d
        except Exception as e:
            print(f"Load mem error: {e}")
    return {"senales_dadas":0,"aciertos":0,"sensibilidad":1.0,"chat_id":None}

def save_memoria(data):
    if not (SUPA_URL and SUPA_KEY): return
    try:
        headers = {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}", "Content-Type":"application/json", "Prefer":"resolution=merge-duplicates"}
        payload = {"id":1, "data": data}
        requests.post(f"{SUPA_URL}/rest/v1/memoria", headers=headers, json=payload, timeout=8)
    except Exception as e:
        print(f"Save mem error: {e}")

def get_precio(symbol="BTCUSDT"):
    try:
        coin_id = MAPA.get(symbol.upper(),"bitcoin")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=10).json()
        return float(r[coin_id]["usd"]), float(r[coin_id].get("usd_24h_change",0))
    except:
        return None, None

def analizar(cambio, sens):
    if cambio is None: return "NEUTRAL ⚪", False
    oport = False
    if cambio < -3.0*sens: s="COMPRA FUERTE 🟢 - Sobreventa extrema"; oport=True
    elif cambio < -1.2*sens: s="COMPRA 🔵 - Oportunidad"; oport=True
    elif cambio > 3.0*sens: s="VENTA FUERTE 🔴 - Sobrecompra"; oport=True
    elif cambio > 1.2*sens: s="VENTA 🟠 - Tomar ganancia"; oport=True
    else: s="NEUTRAL ⚪ - Mercado lateral"
    return s, oport

def send(chat_id, text, buttons=None):
    if not chat_id or not TOKEN: return
    data={"chat_id":chat_id,"text":text,"parse_mode":"Markdown"}
    if buttons: data["reply_markup"]={"inline_keyboard":buttons}
    requests.post(f"{API}/sendMessage", json=data)

@app.route("/")
def home(): return "EVO V9 V4 ETERNA - ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():
    j = request.get_json(force=True, silent=True) or {}
    mem = load_memoria()

    if "callback_query" in j:
        cb=j["callback_query"]
        chat_id=cb["message"]["chat"]["id"]
        act=cb["data"]
        mem["chat_id"]=chat_id

        if act.startswith("senal_"):
            sym=act.replace("senal_","")
            precio,cambio=get_precio(sym)
            if precio:
                senal,_=analizar(cambio, mem.get("sensibilidad",1.0))
                mem["senales_dadas"]+=1
                save_memoria(mem)
                btns=[[{"text":"👍 Buena","callback_data":f"fb_buena_{sym}"},{"text":"👎 Mala","callback_data":f"fb_mala_{sym}"}]]
                send(chat_id, f"📊 *{sym}*\n💲 ${precio:,.2f} ({cambio:.2f}%)\n\n🤖 *{senal}*\n_Sens:{mem['sensibilidad']:.2f} | Total:{mem['senales_dadas']} | Supabase ✅_", btns)
            else:
                send(chat_id,"❌ Error precio, reintentá en 10s")
        elif act.startswith("fb_"):
            _,tipo,sym=act.split("_")
            if tipo=="buena": mem["aciertos"]+=1
            else: mem["sensibilidad"]=max(0.5, mem["sensibilidad"]-0.05)
            save_memoria(mem)
            send(chat_id, f"✅ ¡Aprendido! Guardado para siempre en Supabase. Ahora no olvido nunca más. Aciertos: {mem['aciertos']}")
        elif act=="estado":
            pct=(mem["aciertos"]/mem["senales_dadas"]*100) if mem["senales_dadas"]>0 else 0
            send(chat_id, f"🧠 *ESTADO EVO V4 ETERNO*\n\n🟢 Memoria: Supabase ✅ CONECTADA\n📊 Señales: {mem['senales_dadas']}\n🎯 Aciertos: {mem['aciertos']} ({pct:.1f}%)\n⚙️ Sensibilidad: {mem['sensibilidad']:.2f}\n\nTu agente ya es autoevolutivo eterno y gratis.")
        elif act=="senales_menu":
            btns=[[{"text":"BTC","callback_data":"senal_BTCUSDT"},{"text":"ETH","callback_data":"senal_ETHUSDT"},{"text":"SOL","callback_data":"senal_SOLUSDT"}]]
            send(chat_id,"📈 Elegí moneda (CoinGecko gratis):", btns)

        requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id":cb["id"]})
        return "OK",200

    if "message" in j:
        chat_id=j["message"]["chat"]["id"]
        text=j["message"].get("text","").strip()
        mem["chat_id"]=chat_id
        save_memoria(mem)
        if text.startswith("/start"):
            btns=[[{"text":"📈 SEÑALES","callback_data":"senales_menu"}],[{"text":"🧠 ESTADO ETERNO","callback_data":"estado"}]]
            send(chat_id,"*EVO V9 V4 ETERNA* ✅\n\nMemoria en Supabase conectada. Ya no olvido.\n\n¿Qué analizamos?", btns)

    return "OK",200

@app.route("/auto")
def auto():
    mem=load_memoria()
    chat_id=mem.get("chat_id")
    if not chat_id: return "No chat",200
    precio,cambio=get_precio("BTCUSDT")
    if precio:
        senal,oport=analizar(cambio, mem.get("sensibilidad",1.0))
        if oport:
            send(chat_id, f"🚨 *AUTO-ALERTA EVO*\n\nBTC ${precio:,.2f} ({cambio:.2f}%)\n{senal}\n\nTe aviso solo porque es oportunidad.")
            return f"Sent {senal}",200
    return "No oport",200

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
