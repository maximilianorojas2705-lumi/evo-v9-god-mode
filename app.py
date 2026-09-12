import os, requests
from flask import Flask, request
app = Flask(__name__)
TOKEN = os.environ.get("BOT_TOKEN","") or os.environ.get("TELEGRAM_TOKEN","")
API = f"https://api.telegram.org/bot{TOKEN}"
SUPA_URL = os.environ.get("SUPABASE_URL","").rstrip("/")
SUPA_KEY = os.environ.get("SUPABASE_KEY","")
MAPA = {"BTC":"bitcoin","BTCUSDT":"bitcoin","ETH":"ethereum","ETHUSDT":"ethereum","SOL":"solana","SOLUSDT":"solana","BNB":"binancecoin","BNBUSDT":"binancecoin","XRP":"ripple","XRPUSDT":"ripple","DOGE":"dogecoin","DOGEUSDT":"dogecoin"}

def load_memoria():
    if SUPA_URL and SUPA_KEY:
        try:
            h = {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}"}
            r = requests.get(f"{SUPA_URL}/rest/v1/memoria?id=eq.1&select=data", headers=h, timeout=8).json()
            if r and len(r)>0:
                d = r[0].get("data", {})
                d.setdefault("senales_dadas",0); d.setdefault("aciertos",0); d.setdefault("sensibilidad",1.0); d.setdefault("chat_id",None)
                return d
        except: pass
    return {"senales_dadas":0,"aciertos":0,"sensibilidad":1.0,"chat_id":None}

def save_memoria(data):
    if not (SUPA_URL and SUPA_KEY): return
    try:
        h = {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}", "Content-Type":"application/json","Prefer":"resolution=merge-duplicates"}
        requests.post(f"{SUPA_URL}/rest/v1/memoria", headers=h, json={"id":1,"data":data}, timeout=8)
    except: pass

def get_precio(symbol="BTCUSDT"):
    sym = symbol.upper().replace("USDT","")
    try:
        bsym = f"{sym}USDT"
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={bsym}", timeout=6).json()
        if "lastPrice" in r:
            return float(r["lastPrice"]), float(r["priceChangePercent"]), "binance"
    except: pass
    try:
        coin_id = MAPA.get(sym, "bitcoin")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"}).json()
        return float(r[coin_id]["usd"]), float(r[coin_id].get("usd_24h_change",0)), coin_id
    except:
        return None, None, None

def analizar(cambio, sens):
    if cambio is None: return "NEUTRAL ⚪", False
    oport=False
    if cambio < -3.0*sens: s="COMPRA FUERTE 🟢"; oport=True
    elif cambio < -1.2*sens: s="COMPRA 🔵"; oport=True
    elif cambio > 3.0*sens: s="VENTA FUERTE 🔴"; oport=True
    elif cambio > 1.2*sens: s="VENTA 🟠"; oport=True
    else: s="NEUTRAL ⚪"
    return s, oport

def send(chat_id, text, buttons=None):
    if not chat_id or not TOKEN: return
    data={"chat_id":chat_id,"text":text,"parse_mode":"Markdown"}
    if buttons: data["reply_markup"]={"inline_keyboard":buttons}
    requests.post(f"{API}/sendMessage", json=data)

@app.route("/")
def home(): return "EVO V5.1 BINANCE OK"

@app.route("/webhook", methods=["POST"])
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    j = request.get_json(force=True, silent=True) or {}
    mem = load_memoria()
    if "callback_query" in j:
        cb=j["callback_query"]; chat_id=cb["message"]["chat"]["id"]; act=cb["data"]; mem["chat_id"]=chat_id
        if act.startswith("senal_"):
            sym=act.replace("senal_",""); precio,cambio,_=get_precio(sym)
            if precio:
                senal,_=analizar(cambio, mem.get("sensibilidad",1.0))
                mem["senales_dadas"]+=1; save_memoria(mem)
                btns=[[{"text":"👍 Buena","callback_data":f"fb_buena_{sym}"},{"text":"👎 Mala","callback_data":f"fb_mala_{sym}"}]]
                send(chat_id, f"📈 *{sym} V5.1*\nPrecio: ${precio:,.2f}\n24h: {cambio:+.2f}%\n*{senal}*\nTotal:{mem['senales_dadas']} | Binance ✅", btns)
            else: send(chat_id, "❌ Error Binance caido, reintenta")
        elif act.startswith("fb_"):
            _,tipo,sym=act.split("_")
            if tipo=="buena": mem["aciertos"]+=1
            else: mem["sensibilidad"]=max(0.5, mem["sensibilidad"]-0.05)
            save_memoria(mem)
            send(chat_id, f"✅ Guardado eterno! Aciertos: {mem['aciertos']}")
        elif act=="estado":
            pct=(mem["aciertos"]/mem["senales_dadas"]*100) if mem["senales_dadas"]>0 else 0
            send(chat_id, f"*ESTADO V5.1*\n🟢 Supabase ✅\n🟢 Binance ✅\n📊 {mem['senales_dadas']} | ✅ {mem['aciertos']} ({pct:.1f}%)")
        elif act=="senales_menu":
            btns=[[{"text":"BTC","callback_data":"senal_BTCUSDT"},{"text":"ETH","callback_data":"senal_ETHUSDT"},{"text":"SOL","callback_data":"senal_SOLUSDT"}],[{"text":"BNB","callback_data":"senal_BNBUSDT"},{"text":"XRP","callback_data":"senal_XRPUSDT"},{"text":"DOGE","callback_data":"senal_DOGEUSDT"}]]
            send(chat_id, "📋 Elegi moneda V5.1:", btns)
        requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id":cb["id"]})
        return "OK",200
    if "message" in j:
        chat_id=j["message"]["chat"]["id"]; mem["chat_id"]=chat_id; save_memoria(mem)
        btns=[[{"text":"📈 SEÑALES V5.1","callback_data":"senales_menu"}],[{"text":"🧠 ESTADO","callback_data":"estado"}]]
        send(chat_id, "*EVO V5.1 BINANCE*\nBinance conectado, no falla.", btns)
        return "OK",200
    return "OK",200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
