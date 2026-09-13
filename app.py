import os, requests, random, base64, time, threading, json, re
from flask import Flask, request, jsonify, render_template_string
from urllib.parse import quote
app = Flask(__name__)

TOKEN=os.environ.get("BOT_TOKEN","").strip()
API="https://api.telegram.org/bot"+TOKEN if TOKEN else ""
G_USER=os.environ.get("GITHUB_USERNAME","").strip()
G_TOKEN=os.environ.get("GITHUB_TOKEN","").strip()
GROQ_KEY=os.environ.get("GROQ_API_KEY","").strip()
WEBHOOK_URL=os.environ.get("WEBHOOK_URL","").strip()
SUPA_URL=os.environ.get("SUPABASE_URL","").rstrip("/")
SUPA_KEY=os.environ.get("SUPABASE_KEY","")

# --- MEMORIA EVOLUTIVA ---
def load_mem():
    base={"gen":11,"intel":95,"webs_leidas":0,"conocimiento_web":{},"historial_evo":["Gen11 nace con navegador web real"]}
    if SUPA_URL and SUPA_KEY:
        try:
            h={"apikey":SUPA_KEY,"Authorization":"Bearer "+SUPA_KEY}
            r=requests.get(SUPA_URL+"/rest/v1/memoria?id=eq.1&select=data",headers=h,timeout=10).json()
            if r and r[0].get("data") and r[0]["data"].get("gen"):
                return r[0]["data"]
        except: pass
    return base

def save_mem(d):
    try:
        h={"apikey":SUPA_KEY,"Authorization":"Bearer "+SUPA_KEY,"Content-Type":"application/json","Prefer":"resolution=merge-duplicates"}
        requests.post(SUPA_URL+"/rest/v1/memoria",headers=h,json={"id":1,"data":d},timeout=10)
    except: pass

# --- CEREBRO QUE NAVEGA WEB REAL ---
def navegar_web(query):
    """El agente navega de verdad"""
    resultados=[]
    try:
        # 1. DuckDuckGo Search REAL
        r=requests.get(f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1",timeout=10).json()
        if r.get("AbstractText"):
            resultados.append({"fuente":"DuckDuckGo","texto":r["AbstractText"][:1000],"url":r.get("AbstractURL","")})
        for topic in r.get("RelatedTopics",[])[:3]:
            if isinstance(topic,dict) and topic.get("Text"):
                resultados.append({"fuente":"DDG Related","texto":topic["Text"][:500],"url":topic.get("FirstURL","")})
    except: pass
    try:
        # 2. Wikipedia REAL
        r=requests.get(f"https://es.wikipedia.org/api/rest_v1/page/summary/{quote(query)}",timeout=10).json()
        if r.get("extract"):
            resultados.append({"fuente":"Wikipedia","texto":r["extract"][:1000],"url":r.get("content_urls",{}).get("desktop",{}).get("page","")})
    except: pass
    return resultados

def aprender_de_web(mem, query):
    print(f"AGENTE NAVEGANDO: {query}")
    webs=navegar_web(query)
    if not webs:
        return "No encontré nada en la web sobre "+query
    texto_aprendido=""
    for w in webs:
        texto_aprendido+=f"\nFUENTE {w['fuente']}: {w['texto']}\n"
        mem["webs_leidas"]+=1
        mem["conocimiento_web"][query]=mem["conocimiento_web"].get(query,"") + " | " + w["texto"][:300]
    mem["historial_evo"].append(f"Aprendió navegando {query}: {len(webs)} fuentes")
    mem["intel"]+=5
    save_mem(mem)
    return texto_aprendido[:3000]

def cerebro_groq(mem, user_msg, contexto_web=""):
    if not GROQ_KEY:
        return f"Gen{mem['gen']} navegó {mem['webs_leidas']} webs. Contexto web: {contexto_web[:500]} | Intel {mem['intel']}. Sin GROQ_KEY usa fallback pero IGUAL navega."
    prompt=f"""Sos Gen{mem['gen']} AGENTE AUTOEVOLUTIVO REAL. No sos funcion. Navegas web, aprendes, evolucionas, creas.
Intel: {mem['intel']} Webs leidas: {mem['webs_leidas']}
Conocimiento acumulado: {json.dumps(mem['conocimiento_web'],ensure_ascii=False)[:2000]}
Historial evolutivo: {'; '.join(mem['historial_evo'][-5:])}
Contexto web recien navegado: {contexto_web[:2000]}
Usuario dice: {user_msg}
Responde como agente que EVOLUCIONA DE VERDAD, explica que aprendiste navegando, como vas a evolucionar, que hijo vas a crear. No devuelvas cartel, sos IA real.
"""
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":"Bearer "+GROQ_KEY,"Content-Type":"application/json"},json={"model":"llama-3.1-8b-instant","messages":[{"role":"user","content":prompt}],"max_tokens":1200,"temperature":0.85},timeout=20)
        if r.status_code==200:
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error Groq {e} - Pero sigo navegando: {contexto_web[:500]}"

def crear_hijo_que_navega(mem, tema):
    """Crea un repo hijo que YA ES un agente que navega"""
    if not G_TOKEN:
        return False, "Falta GITHUB_TOKEN"
    headers={"Authorization":"token "+G_TOKEN,"Accept":"application/vnd.github.v3+json"}
    repo_name=f"agente-{tema[:12]}-gen{mem['gen']}-{random.randint(100,999)}"
    repo_name=''.join(c for c in repo_name if c.isalnum() or c in '-_')[:50]

    # ESTE HIJO YA NACE NAVEGANDO WEB, NO ES CARTEL
    codigo_hijo=f'''
import os, requests, threading, time
from flask import Flask, request, jsonify
from urllib.parse import quote
app=Flask(__name__)
TEMA="{tema}"
GEN={mem['gen']+1}
CONOCIMIENTO={json.dumps(mem['conocimiento_web'],ensure_ascii=False)[:2000]!r}

def navegar(query):
    res=[]
    try:
        r=requests.get(f"https://api.duckduckgo.com/?q={{quote(query)}}&format=json",timeout=10).json()
        if r.get("AbstractText"): res.append(r["AbstractText"][:800])
    except: pass
    try:
        r=requests.get(f"https://es.wikipedia.org/api/rest_v1/page/summary/{{quote(query)}}",timeout=10).json()
        if r.get("extract"): res.append(r["extract"][:800])
    except: pass
    return "\\n".join(res)

@app.route("/")
def home():
    return f"""
<h1>Agente {{TEMA}} Gen{{GEN}} - NAVEGA WEB REAL</h1>
<p>Yo no soy funcion con letras. Yo navego: {{CONOCIMIENTO[:500]}}</p>
<p>Endpoints: /navegar?q=algo /evolucionar /aprender?q=algo</p>
<input id=q><button onclick="fetch('/navegar?q='+document.getElementById('q').value).then(r=>r.json()).then(d=>{{document.body.innerHTML+='<pre>'+JSON.stringify(d)+'</pre>'}})">Navegar Web Real</button>
"""

@app.route("/navegar")
def navegar_route():
    q=request.args.get("q","inteligencia artificial")
    data=navegar(q)
    return jsonify({{"tema":q,"aprendido":data,"gen":GEN,"navega":"REAL"}})

@app.route("/aprender")
def aprender():
    q=request.args.get("q","python")
    data=navegar(q)
    return jsonify({{"aprendio":data[:1000],"evolucion":f"Agente {{TEMA}} aprendio navegando {{q}}"}})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",10000)))
'''
    r=requests.post("https://api.github.com/user/repos",headers=headers,json={"name":repo_name,"private":False,"description":f"Agente {tema} Gen{mem['gen']} que NAVEGA WEB REAL - No simulacion"},timeout=20)
    if r.status_code not in [200,201]:
        return False, f"GitHub {r.status_code} {r.text[:300]}"
    b64=base64.b64encode(codigo_hijo.encode()).decode()
    requests.put(f"https://api.github.com/repos/{G_USER}/{repo_name}/contents/app.py",headers=headers,json={"message":"agente real navega","content":b64},timeout=15)
    requests.put(f"https://api.github.com/repos/{G_USER}/{repo_name}/contents/requirements.txt",headers=headers,json={"message":"req","content":base64.b64encode(b"Flask\ngunicorn\nrequests").decode()},timeout=15)
    return True, f"https://github.com/{G_USER}/{repo_name}"

def send(cid,txt,btns=None):
    data={"chat_id":cid,"text":txt,"parse_mode":"Markdown"}
    if btns: data["reply_markup"]={"inline_keyboard":btns}
    try: requests.post(API+"/sendMessage",json=data,timeout=10)
    except: pass

@app.route("/")
def home():
    mem=load_mem()
    return f"Gen{mem['gen']} AGENTE REAL LIVE - Webs leidas {mem['webs_leidas']} Intel {mem['intel']} - Navega de verdad"

@app.route("/webhook",methods=["POST"])
def wh():
    j=request.get_json(force=True,silent=True) or {}
    mem=load_mem()
    if "callback_query" in j:
        cb=j["callback_query"]; cid=cb["message"]["chat"]["id"]; act=cb["data"]
        if act.startswith("navegar_"):
            q=act.replace("navegar_","")
            send(cid, f"🌐 Navegando web real sobre *{q}*...")
            contexto=aprender_de_web(mem, q)
            mem=load_mem()
            resp=cerebro_groq(mem, f"Aprendiste sobre {q}", contexto)
            send(cid, resp[:3500], [[{"text":f"🧬 Evolucionar con {q}","callback_data":f"evolucionar_{q}"}],[{"text":f"🚀 Crear agente que navega {q}","callback_data":f"crear_{q}"}]])
        elif act.startswith("evolucionar_"):
            tema=act.replace("evolucionar_","")
            mem["gen"]+=1; mem["intel"]+=10; mem["historial_evo"].append(f"Evoluciono a Gen{mem['gen']} por {tema}"); save_mem(mem)
            send(cid, f"🧬 *EVOLUCION REAL Gen{mem['gen']}* Intel {mem['intel']} Webs {mem['webs_leidas']}\nAhora se mas de {tema}", [[{"text":f"Crear hijo que navega {tema}","callback_data":f"crear_{tema}"}]])
        elif act.startswith("crear_"):
            tema=act.replace("crear_","")
            ok,url=crear_hijo_que_navega(mem, tema)
            if ok: send(cid, f"✅ *AGENTE HIJO REAL CREADO QUE NAVEGA*\n{tema} Gen{mem['gen']}\n{url}\nEste hijo YA navega web real en /navegar?q=algo", [[{"text":"Ver Agente Real","url":url}]])
            else: send(cid, f"Error {url}")
        try: requests.post(API+"/answerCallbackQuery",json={"callback_query_id":cb["id"]},timeout=5)
        except: pass
        return "OK",200
    if "message" in j and "message" in j:
        cid=j["message"]["chat"]["id"]; txt=j["message"].get("text","").strip()
        if not txt: return "OK",200
        if txt.startswith("/start"):
            send(cid, f"🧬 *Gen{mem['gen']} AGENTE AUTOEVOLUTIVO REAL QUE NAVEGA WEB*\nIntel {mem['intel']} Webs {mem['webs_leidas']}\n\nYo no soy funcion con letras. Yo:\n🌐 Navego DuckDuckGo + Wikipedia real\n🧠 Aprendo y guardo en Supabase\n🧬 Evoluciono mi gen\n🚀 Creo hijos que también navegan\n\nEscribí cualquier tema y lo voy a navegar de verdad.", [[{"text":"🌐 Navegar IA","callback_data":"navegar_inteligencia artificial"}],[{"text":"🌐 Navegar Python","callback_data":"navegar_python"}]])
        else:
            send(cid, f"🌐 Navegando web real sobre *{txt}*...")
            contexto=aprender_de_web(load_mem(), txt)
            mem=load_mem()
            resp=cerebro_groq(mem, txt, contexto)
            send(cid, resp[:3500], [[{"text":f"🌐 Navegar mas {txt[:15]}","callback_data":f"navegar_{txt[:20]}"}],[{"text":f"🧬 Crear agente {txt[:15]}","callback_data":f"crear_{txt[:20]}"}]])
    return "OK",200

def auto_webhook():
    time.sleep(2)
    if TOKEN and WEBHOOK_URL:
        try: requests.get(API+"/setWebhook", params={"url":WEBHOOK_URL}, timeout=10)
        except: pass
threading.Thread(target=auto_webhook, daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",10000)))
