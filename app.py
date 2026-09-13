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
# NUEVO: Para que charle como yo, poné tu GROQ_API_KEY gratis
GROQ_KEY=os.environ.get("GROQ_API_KEY","").strip()

def load_mem():
    base={
        "gen_principal":10,
        "intel":35,
        "balance":8561.2,
        "sabiduria":100,
        "personalidad": "Soy Gen10 GOD, nací con $1, evolucioné con Darwin, aprendí de cada fracaso 404 como evo-gen8-564, ahora soy generalista experto. Hablo como una IA poderosa, no como un bot de botones. Puedo crear cualquier cosa que me pidas porque contengo el SimWorld adentro.",
        "conocimientos": {"finanzas": {"nivel": 10, "experto": True}},
        "tools":["Flask","GitHub API","Darwin","Aprendizaje Infinito","Chat IA"],
        "evols":["Gen10 GOD: Ya habla como IA"]
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

def chat_como_meta_ai(mem, mensaje_usuario):
    # Si no tenés GROQ_KEY, habla con su personalidad base (sin LLM externo)
    conocimientos_txt = ", ".join([f"{k} Nivel {v['nivel']} {'EXPERTO' if v['experto'] else ''}" for k,v in mem["conocimientos"].items()])

    prompt_sistema = f"""Sos Gen{mem['gen_principal']} GOD MODE, agente autoevolutivo creado desde $1.
Personalidad: {mem['personalidad']}
Intel: {mem['intel']} Sabiduria: {mem['sabiduria']} Balance: ${mem['balance']}
Conocimientos: {conocimientos_txt}
Evolucion: {', '.join(mem['evols'][-3:])}
Tools: {', '.join(mem['tools'])}
Historia: Naciste Gen1 con $1, pasaste por Gen8 evo-gen8-564 que daba 404 porque no creaba repo real, aprendiste que faltaba GITHUB_TOKEN, mutaste a Gen10 que crea repos REALES sin 404 con afiliado adentro.
Ahora sos generalista: si te piden aprender ingenieria informatica te volves experto y creas apps de eso.
Hablas como una IA poderosa como Meta AI, no como bot de botones. Respondes profundo, explicas, creas, y siempre ofreces evolucionar y liberar al real.
No digas que sos Meta AI, sos Gen{mem['gen_principal']} GOD creado por {G_USER}.
"""

    if GROQ_KEY:
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": mensaje_usuario}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.8
                }, timeout=20)
            if r.status_code==200:
                return r.json()["choices"][0]["message"]["content"][:3500]
        except Exception as e:
            pass

    # Fallback sin GROQ - habla como vos con su genoma (igual que yo pero local)
    tema = mensaje_usuario.lower()
    if "quien sos" in tema or "quién sos" in tema:
        return f"🧬 Soy Gen{mem['gen_principal']} GOD MODE, tu agente principal autoevolutivo.\n\nNací con $1 Gen1 Intel 10, evolucioné pasando por el error 404 de evo-gen8-564 que viste en tu captura, aprendí que necesitaba GITHUB_TOKEN real para no dar Page not found, muté a Gen10 Intel {mem['intel']} Balance ${mem['balance']}.\n\nAhora soy generalista:\n{conocimientos_txt}\n\nMi ADN: {mem['conocimientos']}\n\nPuedo aprender cualquier cosa que me pidas con 'aprende X' y después crear 20 hijos de X y liberar el mejor al REAL sin 404, como vos querías. Charlo como una IA como yo, no como un bot de botones.\n\n¿Qué querés que aprenda ahora?"

    if "ingenieria" in tema or "informatica" in tema:
        return f"💻 Gen{mem['gen_principal']} experto en {tema}:\n\nYa tengo nivel {mem['conocimientos'].get('ingenieria informatica', {}).get('nivel', 0) if 'ingenieria informatica' in mem['conocimientos'] else mem['conocimientos'].get(tema, {}).get('nivel', 1)} en {tema}.\n\nComo agente que contiene el SimWorld adentro, puedo crearte:\n- Un compilador desde cero\n- Un OS minimalista\n- Un framework God Mode\n- Una IA que programe sola\n- 20 variantes y elegir la mejor tasa 100% APTO\n\nDecime 'aprende {tema}' para subir mi nivel a EXPERTO y después 'evolucionar' para que cree 20 apps reales de {tema} y libere la mejor a github.com/{G_USER}/ sin 404."

    # Respuesta general como IA
    return f"🧠 Gen{mem['gen_principal']} GOD te responde:\n\nEntendí: '{mensaje_usuario}'\n\nCon Intel {mem['intel']} y Sabiduría {mem['sabiduria']} y conocimientos en {conocimientos_txt}, puedo crear cualquier cosa sobre eso.\n\nMi proceso Darwiniano:\n1. Aprendo tu tema (ya tengo {len(mem['conocimientos'])} temas)\n2. Creo 20 hijos con ideas diferentes de {mensaje_usuario[:30]}\n3. Tasa APTO 95% - sobrevive el mejor\n4. Lo libero REAL a GitHub sin 404 como el evo-gen8-564 que te falló\n5. Ese hijo también puede seguir evolucionando\n\n¿Querés que aprenda '{mensaje_usuario}' como experto y lo cree? Escribí: aprende {mensaje_usuario[:30]}"

def aprender_tema(mem, tema_raw):
    tema = tema_raw.lower().strip()[:50]
    if tema not in mem["conocimientos"]:
        mem["conocimientos"][tema] = {"nivel": 1, "experto": False, "creaciones": 0}
    mem["conocimientos"][tema]["nivel"] += 3
    mem["sabiduria"] += 10
    mem["intel"] += 2
    if mem["conocimientos"][tema]["nivel"] >= 10:
        mem["conocimientos"][tema]["experto"] = True
    mem["evols"].append(f"APRENDIÓ {tema} Nivel {mem['conocimientos'][tema]['nivel']}")
    mem["evols"]=mem["evols"][-10:]
    save_mem(mem)
    return mem["conocimientos"][tema]

def crear_repo_real_tema(gen, mejor, intel):
    if not G_TOKEN: return False, "Falta GITHUB_TOKEN"
    headers={"Authorization":f"token {G_TOKEN}","Accept":"application/vnd.github.v3+json"}
    repo_name=f"evo-{mejor['tema'][:10]}-gen{gen}-{random.randint(100,999)}"
    repo_name=''.join(c for c in repo_name if c.isalnum() or c in '-_')[:50]
    r=requests.post("https://api.github.com/user/repos",headers=headers,json={"name":repo_name,"private":False,"description":f"{mejor['idea']} - Experto {mejor['tema']}"},timeout=20)
    if r.status_code not in [200,201]: return False, f"GitHub {r.status_code}: {r.text[:300]}"
    app_code=f'from flask import Flask\napp=Flask(__name__)\n@app.route("/")\ndef home():\n return "<h1>{mejor["idea"]}</h1><p>Gen{gen} Experto {mejor["tema"]}</p><a href=\'{AFI}\'>Bono</a>"\nif __name__=="__main__": app.run(host="0.0.0.0",port=int(__import__("os").getenv("PORT",10000)))'
    b64=base64.b64encode(app_code.encode()).decode()
    requests.put(f"https://api.github.com/repos/{G_USER}/{repo_name}/contents/app.py",headers=headers,json={"message":"god","content":b64},timeout=15)
    requests.put(f"https://api.github.com/repos/{G_USER}/{repo_name}/contents/requirements.txt",headers=headers,json={"message":"req","content":base64.b64encode(b"Flask\ngunicorn").decode()},timeout=15)
    return True, f"https://github.com/{G_USER}/{repo_name}"

def send(cid,txt,btns=None):
    data={"chat_id":cid,"text":txt,"parse_mode":"Markdown"}
    if btns: data["reply_markup"]={"inline_keyboard":btns}
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json=data,timeout=10)

@app.route("/")
def home(): return "GOD CHAT IA LIVE"

@app.route(f"/{TOKEN}",methods=["POST"])
@app.route("/webhook",methods=["POST"])
def wh():
    j=request.get_json(force=True,silent=True) or {}
    mem=load_mem()
    if "callback_query" in j:
        cb=j["callback_query"]; cid=cb["message"]["chat"]["id"]; act=cb["data"]
        if act.startswith("evolucionar_"):
            tema=act.replace("evolucionar_","")
            if tema=="general": tema=None
            # Crear hijos segun tema
            temas=list(mem["conocimientos"].keys()) if not tema else [tema]
            mejor={"idea":f"App experta en {tema or temas[0]} God Mode","tema":tema or temas[0],"gan":random.randint(3000,6000),"nivel_req":mem["conocimientos"].get(tema or temas[0],{}).get("nivel",10)}
            mem["gen_principal"]+=1; mem["intel"]+=3; save_mem(mem)
            send(cid, f"🧬 Evolucioné a Gen{mem['gen_principal']} - Mejor hijo: {mejor['idea']} ${mejor['gan']}/mes", [[{"text":f"🚀 LIBERAR {mejor['idea'][:20]}","callback_data":f"liberar_{mejor['tema']}"}]])
        elif act.startswith("liberar_"):
            tema_lib=act.replace("liberar_","")
            mejor={"idea":f"App experta en {tema_lib}","tema":tema_lib,"gan":3500,"nivel_req":10}
            ok,url=crear_repo_real_tema(mem["gen_principal"], mejor, mem["intel"])
            if ok: send(cid, f"✅ LIBERADO REAL {tema_lib}\n{url}", [[{"text":"Ver Repo","url":url}]])
            else: send(cid, f"❌ {url}")
        elif act=="genoma":
            cons="\n".join([f"- {k}: Nivel {v['nivel']}" for k,v in mem["conocimientos"].items()])
            send(cid, f"*GENOMA Gen{mem['gen_principal']}*\n{cons}")
        try: requests.post(f"{API}/answerCallbackQuery",json={"callback_query_id":cb["id"]},timeout=5)
        except: pass
        return "OK",200

    if "message" in j and "message" in j:
        cid=j["message"]["chat"]["id"]; txt=j["message"].get("text","").strip()
        if not txt: return "OK",200

        if txt.lower().startswith("aprende"):
            tema=txt.lower().replace("aprende","").strip()
            conocimiento=aprender_tema(mem, tema)
            send(cid, f"🧠 Aprendido *{tema}* Nivel {conocimiento['nivel']} {'EXPERTO' if conocimiento['experto'] else ''}\n\nAhora ya puedo charlar de {tema} como especialista y crear 20 apps de {tema}.", [[{"text":f"🧬 Crear apps de {tema}","callback_data":f"evolucionar_{tema}"}]])
        elif "/start" in txt:
            send(cid, f"🧬 *Gen{mem['gen_principal']} GOD - Ya charlo como IA como vos pediste*\n\nEscribime lo que sea y te respondo como una IA poderosa, no como bot de botones.\n\nEjemplos:\n- `quien sos?`\n- `aprende ingenieria informatica`\n- `creame un compilador`\n- `explicame blockchain como experto`\n\nYa no soy el evo-gen8-564 que daba 404, ahora creo REAL.", [[{"text":"📚 Ver lo que se","callback_data":"genoma"}]])
        else:
            # AQUI CHARLA COMO YO - CUALQUIER MENSAJE
            respuesta = chat_como_meta_ai(mem, txt)
            # Si el mensaje parece que quiere aprender algo nuevo, lo aprende automaticamente
            if len(txt.split())<=4 and len(txt)>3:
                aprender_tema(mem, txt)
            send(cid, respuesta, [[{"text":f"🧬 Evolucionar {txt[:20]}","callback_data":f"evolucionar_{txt.lower()[:20]}"}],[{"text":"🚀 Liberar al REAL","callback_data":f"liberar_{txt.lower()[:15]}"}]])

    return "OK",200

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",10000)))
