import os, requests, random, base64
from flask import Flask, request
app = Flask(__name__)
TOKEN=os.environ.get("BOT_TOKEN","")
API=f"https://api.telegram.org/bot{TOKEN}"
SUPA_URL=os.environ.get("SUPABASE_URL","").rstrip("/")
SUPA_KEY=os.environ.get("SUPABASE_KEY","")
GITHUB_USER=os.environ.get("GITHUB_USERNAME","maximilianorojas2705-lumi")
GITHUB_TOKEN=os.environ.get("GITHUB_TOKEN","")
AFILIADO=os.environ.get("AFILIADO_LINK","https://binance.com")

def load_mem():
    base={"gen_principal":1,"intel":10,"tools":["Flask","Supabase"],"balance":1.0,"gan_total":0.0,"sabiduria":0,"vivos":0,"muertos":0,"evols":["Gen1: Nace con $1"]}
    if SUPA_URL and SUPA_KEY:
        try:
            h={"apikey":SUPA_KEY,"Authorization":f"Bearer {SUPA_KEY}"}
            r=requests.get(f"{SUPA_URL}/rest/v1/memoria?id=eq.1&select=data",headers=h,timeout=10).json()
            if r and r[0].get("data"):
                d=r[0]["data"]
                for k,v in base.items(): d.setdefault(k,v)
                return d
        except: pass
    return base
def save_mem(d):
    try:
        h={"apikey":SUPA_KEY,"Authorization":f"Bearer {SUPA_KEY}","Content-Type":"application/json","Prefer":"resolution=merge-duplicates"}
        requests.post(f"{SUPA_URL}/rest/v1/memoria",headers=h,json={"id":1,"data":d},timeout=10)
    except: pass

def crear_repo_real(gen, gan, intel):
    if not GITHUB_TOKEN:
        return False, "Falta GITHUB_TOKEN en Render Environment"
    headers={"Authorization":f"token {GITHUB_TOKEN}","Accept":"application/vnd.github.v3+json"}
    repo_name=f"evo-gen{gen}-{random.randint(100,999)}"
    # 1. Crear repo
    r=requests.post("https://api.github.com/user/repos",headers=headers,json={"name":repo_name,"private":False,"description":f"Gen{gen} Intel {intel} ${gan}/mes - Super Agente Autoevolutivo"},timeout=15)
    if r.status_code not in [200,201]:
        return False, f"GitHub error: {r.text[:400]}"
    # 2. Crear app.py con tu afiliado
    app_code=f'''
from flask import Flask
app=Flask(__name__)
AFILIADO="{AFILIADO}"
@app.route("/")
def home():
    return f"""<h1>Gen{gen} Intel {intel} - ${gan}/mes</h1><p>Proyecto Gen{gen} liberado del SimWorld con tasa 100% APTO</p><a href='{{AFILIADO}}' style='background:#F3BA2F;padding:15px;color:black'>Opera y gana bono</a><p>Balance desde $1 - Sabiduria acumulada</p>"""
if __name__=="__main__":
    import os
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",10000)))
'''
    b64=base64.b64encode(app_code.encode()).decode()
    url=f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/contents/app.py"
    requests.put(url,headers=headers,json={"message":f"Gen{gen} ${gan}/mes","content":b64},timeout=15)
    req_b64=base64.b64encode(b"Flask\ngunicorn").decode()
    requests.put(f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/contents/requirements.txt",headers=headers,json={"message":"req","content":req_b64},timeout=15)
    return True, f"https://github.com/{GITHUB_USER}/{repo_name}"

def send(cid,txt,btns=None):
    if len(txt)>4000: txt=txt[:4000]
    data={"chat_id":cid,"text":txt,"parse_mode":"Markdown"}
    if btns: data["reply_markup"]={"inline_keyboard":btns}
    try: requests.post(f"{API}/sendMessage",json=data,timeout=10)
    except: pass

@app.route("/")
def home(): return "EVO V9.2 REAL LIVE"
@app.route(f"/{TOKEN}",methods=["POST"])
@app.route("/webhook",methods=["POST"])
def wh():
    j=request.get_json(force=True,silent=True) or {}
    mem=load_mem()
    if "callback_query" in j:
        cb=j["callback_query"]; cid=cb["message"]["chat"]["id"]; act=cb["data"]
        if act in ["evolucionar_principal","crear_mundo","ask_app"]:
            intel=mem["intel"]; exitos=sum(1 for _ in range(20) if random.random() < (0.3+intel*0.04)); tasa=int(exitos/20*100); apto=tasa>=75; gan=random.randint(300,1500)*(1+intel//10)
            if apto:
                mem["vivos"]+=1; mem["intel"]+=3; mem["sabiduria"]+=5; mem["gen_principal"]+=1; mem["balance"]+=gan*0.3; mem["gan_total"]+=gan; mem["tools"].append(f"Tool-Gen{mem['gen_principal']}"); mem["evols"].append(f"Gen{mem['gen_principal']}: Intel {mem['intel']} APTO {tasa}%"); mem["evols"]=mem["evols"][-8:]; save_mem(mem)
                send(cid,f"```SIMWORLD Gen{mem['gen_principal']} Intel {intel}->{mem['intel']} 20 hijos tasa {tasa}% APTO +${int(gan)} Balance ${mem['balance']:.2f}```\nPRINCIPAL MUTÓ A Gen{mem['gen_principal']}",[[{"text":f"LIBERAR REAL ${int(gan)}/mes","callback_data":f"liberar_{int(gan)}"}],[{"text":"EVOLUCIONAR OTRA VEZ","callback_data":"evolucionar_principal"}]])
            else:
                mem["muertos"]+=1; mem["intel"]+=1; mem["sabiduria"]+=2; mem["gen_principal"]+=1; mem["evols"].append(f"Gen{mem['gen_principal']}: FAIL pero aprende"); mem["evols"]=mem["evols"][-8:]; save_mem(mem)
                send(cid,f"```SIMWORLD Gen{mem['gen_principal']} Tasa {tasa}% FAIL - Principal muta```",[[{"text":"EVOLUCIONAR DEL FRACASO","callback_data":"evolucionar_principal"}],[{"text":"Ver Genoma","callback_data":"genoma"}]])
        elif act.startswith("liberar_"):
            gan=act.split("_")[1]
            ok,url_o_error=crear_repo_real(mem['gen_principal'],gan,mem['intel'])
            if ok:
                send(cid,f"🌌 LIBERADO AL REAL Gen{mem['gen_principal']} Intel {mem['intel']} ${gan}/mes\n🔗 {url_o_error}\n✅ Repo REAL creado con tu AFILIADO_LINK adentro\nYa no es simulado, existe de verdad",[[{"text":"Ver Repo Real","url":url_o_error}]])
            else:
                send(cid,f"❌ {url_o_error}\n\nVerifica en Render Environment:\nGITHUB_TOKEN=ghp_...\nGITHUB_USERNAME=maximilianorojas2705-lumi",[[{"text":"Ver Genoma","callback_data":"genoma"}]])
        elif act in ["genoma","evolucion","libertad"]:
            evo="\n".join(mem["evols"])
            send(cid,f"*PRINCIPAL Gen{mem['gen_principal']} Intel {mem['intel']} Balance ${mem['balance']:.2f} Gan ${mem['gan_total']:.0f}*\nTools: {len(mem['tools'])}\n\n{evo}",[[{"text":"EVOLUCIONAR PRINCIPAL","callback_data":"evolucionar_principal"}]])
        try: requests.post(f"{API}/answerCallbackQuery",json={"callback_query_id":cb["id"]},timeout=5)
        except: pass
        return "OK",200
    if "message" in j:
        cid=j["message"]["chat"]["id"]; txt=j["message"].get("text","").strip()
        if "/start" in txt:
            send(cid,f"*V9.2 PRINCIPAL REAL FIXED*\nGen {mem['gen_principal']} Intel {mem['intel']} Balance ${mem['balance']:.2f}\nEste ya crea repos REALES, no simulados",[[{"text":"EVOLUCIONAR PRINCIPAL","callback_data":"evolucionar_principal"}],[{"text":"Ver Genoma","callback_data":"genoma"}]])
        return "OK",200
    return "OK",200
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT",10000)))
