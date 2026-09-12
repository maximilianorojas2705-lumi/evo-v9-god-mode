import os, requests, random, base64
from flask import Flask, request
app = Flask(__name__)

TOKEN=os.environ.get("BOT_TOKEN","").strip()
API=f"https://api.telegram.org/bot{TOKEN}"
SUPA_URL=os.environ.get("SUPABASE_URL","").rstrip("/")
SUPA_KEY=os.environ.get("SUPABASE_KEY","")
G_USER=os.environ.get("GITHUB_USERNAME","maximilianorojas2705-lumi").strip()
G_TOKEN=os.environ.get("GITHUB_TOKEN","").strip()
AFI=os.environ.get("AFILIADO_LINK","").strip()

def load_mem():
    base={
        "gen_principal":10,
        "intel":35,
        "balance":8561.2,
        "sabiduria":100,
        "conocimientos": {
            "finanzas": {"nivel": 10, "experto": True, "creaciones": 5}
        },
        "tools":["Flask","GitHub API","Darwin Engine","Aprendizaje Generalista"],
        "evols":["Gen10 GOD: Listo para aprender cualquier tema"]
    }
    if SUPA_URL and SUPA_KEY:
        try:
            h={"apikey":SUPA_KEY,"Authorization":f"Bearer {SUPA_KEY}"}
            r=requests.get(f"{SUPA_URL}/rest/v1/memoria?id=eq.1&select=data",headers=h,timeout=10).json()
            if r and r[0].get("data"): return r[0]["data"]
        except: pass
    return base

def save_mem(d):
    try:
        h={"apikey":SUPA_KEY,"Authorization":f"Bearer {SUPA_KEY}","Content-Type":"application/json","Prefer":"resolution=merge-duplicates"}
        requests.post(f"{SUPA_URL}/rest/v1/memoria",headers=h,json={"id":1,"data":d},timeout=10)
    except: pass

def aprender_tema(mem, tema_raw):
    tema = tema_raw.lower().strip()
    # Si pide "ingenieria informatica" lo vuelve experto
    if tema not in mem["conocimientos"]:
        mem["conocimientos"][tema] = {"nivel": 1, "experto": False, "creaciones": 0}

    mem["conocimientos"][tema]["nivel"] += 3
    mem["sabiduria"] += 10
    mem["intel"] += 2

    if mem["conocimientos"][tema]["nivel"] >= 10:
        mem["conocimientos"][tema]["experto"] = True

    mem["evols"].append(f"APRENDIÓ: {tema} -> Nivel {mem['conocimientos'][tema]['nivel']} {'EXPERTO' if mem['conocimientos'][tema]['experto'] else ''}")
    mem["evols"] = mem["evols"][-12:]
    save_mem(mem)
    return mem["conocimientos"][tema]

def crear_hijos_del_tema(mem, tema_focus=None):
    # Si no le decis tema, usa todos los que aprendio
    conocimientos = mem["conocimientos"]
    if tema_focus and tema_focus.lower() in conocimientos:
        temas_a_usar = [tema_focus.lower()]
    else:
        temas_a_usar = list(conocimientos.keys())

    hijos = []
    for i in range(20):
        tema = random.choice(temas_a_usar)
        nivel = conocimientos[tema]["nivel"]
        # Ideas segun el tema que aprendio
        if "informatica" in tema or "software" in tema or "programacion" in tema:
            ideas = [f"Sistema {tema} con IA", f"App de {tema} autoevolutiva", f"Framework {tema} God Mode", f"OS en {tema}", f"Compilador {tema}"]
        elif "medicina" in tema:
            ideas = [f"Diagnostico IA {tema}", f"App {tema} que cura", f"Base de datos {tema}"]
        elif "ingenieria" in tema:
            ideas = [f"Diseño {tema} automatizado", f"Calculadora {tema} GOD", f"Simulador {tema}"]
        else:
            ideas = [f"App experta en {tema}", f"Sistema {tema} con IA", f"Plataforma {tema} God Mode", f"Asistente {tema}"]

        idea = random.choice(ideas)
        prob = 0.3 + (nivel*0.06) + (mem["intel"]*0.01)
        exito = random.random() < prob
        hijos.append({"idea": idea, "tema": tema, "exito": exito, "gan": random.randint(1000,6000)*(nivel//3+1), "nivel_req": nivel})

    aptos = [h for h in hijos if h["exito"]]
    tasa = int(len(aptos)/20*100)
    mejor = max(aptos, key=lambda x: x["gan"]) if aptos else None
    return hijos, aptos, tasa, mejor

def crear_repo_real_tema(gen, mejor, intel):
    if not G_TOKEN: return False, "Falta GITHUB_TOKEN en Render"
    headers={"Authorization":f"token {G_TOKEN}","Accept":"application/vnd.github.v3+json"}
    repo_name=f"evo-{mejor['tema'][:10]}-gen{gen}-{random.randint(100,999)}"
    repo_name=''.join(c for c in repo_name if c.isalnum() or c in '-_')[:50]

    r=requests.post("https://api.github.com/user/repos",headers=headers,json={"name":repo_name,"private":False,"description":f"{mejor['idea']} - Gen{gen} Experto en {mejor['tema']} Intel {intel}"},timeout=20)
    if r.status_code not in [200,201]: return False, f"GitHub {r.status_code}: {r.text[:400]}"

    app_code=f'''
from flask import Flask
app=Flask(__name__)
TEMA="{mejor['tema']}"
IDEA="{mejor['idea']}"
GEN={gen}
@app.route("/")
def home():
    return f"<h1>{{IDEA}}</h1><h2>Experto en {{TEMA}} - Gen{{GEN}} Intel {intel}</h2><p>Creado por agente principal que APRENDIO {mejor['tema']} y se volvio experto Nivel {mejor['nivel_req']}</p><a href='{AFI}'>Link</a>"
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(__import__("os").getenv("PORT",10000)))
'''
    b64=base64.b64encode(app_code.encode()).decode()
    requests.put(f"https://api.github.com/repos/{G_USER}/{repo_name}/contents/app.py",headers=headers,json={"message":f"{mejor['idea']}","content":b64},timeout=15)
    requests.put(f"https://api.github.com/repos/{G_USER}/{repo_name}/contents/requirements.txt",headers=headers,json={"message":"req","content":base64.b64encode(b"Flask\ngunicorn").decode()},timeout=15)
    return True, f"https://github.com/{G_USER}/{repo_name}"

def send(cid,txt,btns=None):
    data={"chat_id":cid,"text":txt,"parse_mode":"Markdown"}
    if btns: data["reply_markup"]={"inline_keyboard":btns}
    requests.post(f"{API}/sendMessage",json=data,timeout=10)

@app.route("/")
def home(): return "GOD GENERALISTA - Aprende cualquier tema"

@app.route(f"/{TOKEN}",methods=["POST"])
@app.route("/webhook",methods=["POST"])
def wh():
    j=request.get_json(force=True,silent=True) or {}
    mem=load_mem()
    if "callback_query" in j:
        cb=j["callback_query"]; cid=cb["message"]["chat"]["id"]; act=cb["data"]
        if act.startswith("evolucionar_"):
            tema = act.replace("evolucionar_","") if "_" in act else None
            if tema=="general": tema=None
            hijos, aptos, tasa, mejor = crear_hijos_del_tema(mem, tema)
            mem["gen_principal"]+=1; mem["intel"]+=3; save_mem(mem)
            if mejor:
                send(cid, f"🧬 *SIMWORLD {tema or 'GENERAL'}* Gen{mem['gen_principal']} Tasa {tasa}% APTO\nMejor: *{mejor['idea']}* ${mejor['gan']}/mes\nTema: {mejor['tema']} Nivel {mejor['nivel_req']}\n\n20 hijos creados, {len(aptos)} sobrevivieron", [[{"text":f"🚀 LIBERAR {mejor['idea'][:25]}","callback_data":f"liberar_{mejor['tema']}"}],[{"text":"🧬 Evolucionar otra vez","callback_data":f"evolucionar_{tema or 'general'}"}]])
            else:
                send(cid, f"FAIL tasa {tasa}% pero aprende + sabiduria", [[{"text":"Evolucionar del fracaso","callback_data":f"evolucionar_{tema or 'general'}"}]])
        elif act.startswith("liberar_"):
            tema_lib=act.replace("liberar_","")
            hijos, aptos, tasa, mejor = crear_hijos_del_tema(mem, tema_lib)
            if not mejor: mejor={"idea":f"App experta en {tema_lib}","tema":tema_lib,"gan":3500,"nivel_req":10}
            ok,url=crear_repo_real_tema(mem["gen_principal"], mejor, mem["intel"])
            if ok: send(cid, f"✅ *LIBERADO REAL Experto en {tema_lib}*\n{mejor['idea']}\n{url}", [[{"text":"Ver Repo Real","url":url}]])
            else: send(cid, f"❌ {url}")
        elif act=="genoma":
            cons="\n".join([f"- {k}: Nivel {v['nivel']} {'EXPERTO' if v['experto'] else ''}" for k,v in mem["conocimientos"].items()])
            send(cid, f"*GENOMA GENERALISTA Gen{mem['gen_principal']}*\nIntel {mem['intel']} Sabiduria {mem['sabiduria']}\n\n*Conocimientos:*\n{cons}\n\nYa no solo finanzas, aprende cualquier cosa", [[{"text":"Evolucionar General","callback_data":"evolucionar_general"}]])
        try: requests.post(f"{API}/answerCallbackQuery",json={"callback_query_id":cb["id"]},timeout=5)
        except: pass
        return "OK",200

    if "message" in j and "message" in j:
        cid=j["message"]["chat"]["id"]; txt=j["message"].get("text","").strip()
        if not txt: return "OK",200
        # COMANDO APRENDE CUALQUIER COSA
        if txt.lower().startswith("aprende") or txt.lower().startswith("aprender"):
            tema = txt.lower().replace("aprende","").replace("aprender","").replace("de","").strip()
            if not tema: tema="tema general"
            conocimiento = aprender_tema(mem, tema)
            mem=load_mem()
            send(cid, f"🧠 *APRENDIENDO: {tema.upper()}*\n\nNivel: {conocimiento['nivel']} {'🔥 EXPERTO' if conocimiento['experto'] else 'Aprendiendo...'}\nIntel: {mem['intel']} Sabiduria: {mem['sabiduria']}\n\nAhora soy {'experto' if conocimiento['experto'] else 'aprendiz'} en {tema}. Si me pedis evolucionar, voy a crear 20 apps de {tema}.", [[{"text":f"🧬 Crear 20 apps de {tema}","callback_data":f"evolucionar_{tema}"}],[{"text":"📚 Ver todo lo que se","callback_data":"genoma"}]])
        elif "/start" in txt:
            cons="\n".join([f"- {k}: Nivel {v['nivel']}" for k,v in mem["conocimientos"].items()])
            send(cid, f"🧬 *AGENTE GENERALISTA GOD Gen{mem['gen_principal']}*\nIntel {mem['intel']}\n\n*Se lo que se:*\n{cons}\n\nEscribime:\n`aprende ingenieria informatica`\n`aprende medicina`\n`aprende arquitectura`\n`aprende lo que quieras`\n\nY despues toco evolucionar y te creo 20 apps de ese tema.", [[{"text":"📚 Ver conocimientos","callback_data":"genoma"}]])
        else:
            # Si escribe cualquier cosa, lo toma como tema a aprender
            if len(txt)>3 and "gen" not in txt.lower():
                conocimiento = aprender_tema(mem, txt)
                send(cid, f"Entendido, aprendiendo *{txt}* Nivel {conocimiento['nivel']}", [[{"text":f"Crear apps de {txt}","callback_data":f"evolucionar_{txt.lower()}"}]])
    return "OK",200

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",10000)))
