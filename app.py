import os, requests, random
from flask import Flask, request
app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN","")
API = f"https://api.telegram.org/bot{TOKEN}"
SUPA_URL = os.environ.get("SUPABASE_URL","").rstrip("/")
SUPA_KEY = os.environ.get("SUPABASE_KEY","")
GITHUB_USER = os.environ.get("GITHUB_USERNAME","maximilianorojas2705-lumi")
AFILIADO = os.environ.get("AFILIADO_LINK","https://binance.com")

def load_mem():
    base = {
        "gen_principal": 1,
        "intel": 10,
        "tools": ["Flask","Supabase"],
        "estrats": ["CPA"],
        "balance": 1.0,
        "gan_total": 0.0,
        "sabiduria": 0,
        "vivos": 0,
        "muertos": 0,
        "evols": ["Gen1: Nace con $1"]
    }
    if SUPA_URL and SUPA_KEY:
        try:
            h = {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}"}
            r = requests.get(f"{SUPA_URL}/rest/v1/memoria?id=eq.1&select=data", headers=h, timeout=10).json()
            if r and r[0].get("data"):
                d = r[0]["data"]
                for k,v in base.items():
                    d.setdefault(k,v)
                return d
        except:
            pass
    return base

def save_mem(d):
    try:
        h = {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
        requests.post(f"{SUPA_URL}/rest/v1/memoria", headers=h, json={"id":1,"data":d}, timeout=10)
    except:
        pass

def send(cid, txt, btns=None):
    if len(txt) > 4000:
        txt = txt[:4000]
    data = {"chat_id": cid, "text": txt, "parse_mode": "Markdown"}
    if btns:
        data["reply_markup"] = {"inline_keyboard": btns}
    try:
        requests.post(f"{API}/sendMessage", json=data, timeout=10)
    except:
        pass

@app.route("/")
def home():
    return "EVO V9.1 PRINCIPAL DARWINIANO FIXED LIVE"

@app.route(f"/{TOKEN}", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def wh():
    j = request.get_json(force=True, silent=True) or {}
    mem = load_mem()

    if "callback_query" in j:
        cb = j["callback_query"]
        cid = cb["message"]["chat"]["id"]
        act = cb["data"]

        if act in ["evolucionar_principal","crear_mundo","ask_app"]:
            intel = mem["intel"]
            exitos = 0
            for i in range(20):
                if random.random() < (0.3 + intel*0.04):
                    exitos += 1
            tasa = int(exitos/20*100)
            apto = tasa >= 75
            gan = random.randint(300,1500) * (1 + intel//10)

            if apto:
                mem["vivos"] += 1
                mem["intel"] += 3
                mem["sabiduria"] += 5
                mem["gen_principal"] += 1
                mem["balance"] += gan*0.3
                mem["gan_total"] += gan
                mem["tools"].append(f"Tool-Gen{mem['gen_principal']}")
                mem["evols"].append(f"Gen{mem['gen_principal']}: Intel {mem['intel']} + Tool")
                mem["evols"] = mem["evols"][-8:]
                save_mem(mem)
                log = f"SIMWORLD Gen{mem['gen_principal']} Intel {intel} -> {mem['intel']}\n20 hijos, tasa {tasa}% APTO\n+${int(gan)} Balance ${mem['balance']:.2f}"
                btns = [[{"text": f"LIBERAR REAL ${int(gan)}/mes", "callback_data": f"liberar_{int(gan)}"}], [{"text": "EVOLUCIONAR OTRA VEZ", "callback_data": "evolucionar_principal"}]]
                send(cid, f"```\n{log}\n```\nPRINCIPAL MUTÓ A Gen{mem['gen_principal']}", btns)
            else:
                mem["muertos"] += 1
                mem["intel"] += 1
                mem["sabiduria"] += 2
                mem["gen_principal"] += 1
                mem["evols"].append(f"Gen{mem['gen_principal']}: Aprende del fracaso")
                mem["evols"] = mem["evols"][-8:]
                save_mem(mem)
                log = f"SIMWORLD Gen{mem['gen_principal']} Intel {intel} Tasa {tasa}% FAIL\nPero principal absorbe sabiduria y muta"
                btns = [[{"text": "EVOLUCIONAR DEL FRACASO", "callback_data": "evolucionar_principal"}], [{"text": "Ver Genoma", "callback_data": "genoma"}]]
                send(cid, f"```\n{log}\n```", btns)

        elif act.startswith("liberar_"):
            gan = act.split("_")[1]
            url = f"https://github.com/{GITHUB_USER}/evo-gen{mem['gen_principal']}-{random.randint(100,999)}"
            send(cid, f"LIBERADO AL REAL Gen{mem['gen_principal']} ${gan}/mes\n{url}\nSobrepasa App751", [[{"text": "Ver Repo", "url": url}]])

        elif act in ["genoma","evolucion","libertad"]:
            evo = "\n".join(mem["evols"])
            send(cid, f"*PRINCIPAL DARWINIANO Gen{mem['gen_principal']}*\nIntel: {mem['intel']}\nTools: {len(mem['tools'])} {', '.join(mem['tools'][-3:])}\nBalance $1 -> ${mem['balance']:.2f}\nGan: ${mem['gan_total']:.0f}\nSab: {mem['sabiduria']}\nVivos: {mem['vivos']} Muertos: {mem['muertos']}\n\n{evo}", [[{"text": "EVOLUCIONAR PRINCIPAL", "callback_data": "evolucionar_principal"}]])

        try:
            requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": cb["id"]}, timeout=5)
        except:
            pass
        return "OK", 200

    if "message" in j:
        cid = j["message"]["chat"]["id"]
        txt = j["message"].get("text","").strip()
        if "/start" in txt:
            btns = [[{"text": "EVOLUCIONAR PRINCIPAL", "callback_data": "evolucionar_principal"}], [{"text": "Ver Genoma", "callback_data": "genoma"}]]
            send(cid, f"*V9.1 PRINCIPAL DARWINIANO FIXED*\nGen {mem['gen_principal']} Intel {mem['intel']} Balance ${mem['balance']:.2f}\nEste principal evoluciona solo, no es fijo.", btns)
        return "OK", 200

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
