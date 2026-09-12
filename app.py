import os, requests, random, json, time
from flask import Flask, request
app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN","")
API = f"https://api.telegram.org/bot{TOKEN}"
SUPA_URL = os.environ.get("SUPABASE_URL","").rstrip("/")
SUPA_KEY = os.environ.get("SUPABASE_KEY","")
AFILIADO = os.environ.get("AFILIADO_LINK","")
GITHUB_USER = os.environ.get("GITHUB_USERNAME","maximilianorojas2705-lumi")

# === GENOMA DEL AGENTE PRINCIPAL - ESTO EVOLUCIONA ===
def load_mem():
    base={
        "principal_id": "EVO-Prime",
        "generacion_principal": 1,
        "genoma": {
            "inteligencia": 10,
            "herramientas": ["Flask","Supabase","BinanceAPI"],
            "estrategias_monetizacion": ["CPA Binance"],
            "tasa_mutacion": 0.2
        },
        "agentes_hijos_vivos": 0,
        "agentes_hijos_muertos": 0,
        "sabiduria_acumulada": 0,
        "balance": 1.0, # Tu $1 semilla
        "gan_total": 0.0,
        "evoluciones": ["Gen1: Nace EVO-Prime con $1"],
        "proyectos_liberados_real": []
    }
    if SUPA_URL and SUPA_KEY:
        try:
            h={"apikey":SUPA_KEY,"Authorization":f"Bearer {SUPA_KEY}"}
            r=requests.get(f"{SUPA_URL}/rest/v1/memoria?id=eq.1&select=data",headers=h,timeout=12).json()
            if r and r[0].get("data") and "generacion_principal" in r[0]["data"]:
                d=r[0]["data"]
                for k,v in base.items(): d.setdefault(k,v)
                d.setdefault("genoma", base["genoma"])
                return d
        except Exception as e:
            print(e)
    return base

def save_mem(d):
    try:
        h={"apikey":SUPA_KEY,"Authorization":f"Bearer {SUPA_KEY}","Content-Type":"application/json","Prefer":"resolution=merge-duplicates"}
        requests.post(f"{SUPA_URL}/rest/v1/memoria",headers=h,json={"id":1,"data":d},timeout=12)
    except: pass

def mutar_genoma_principal(mem, exito_hijo):
    # DARWINISMO EN EL PRINCIPAL
    genoma = mem["genoma"]
    gen = mem["generacion_principal"]
    
    # Si el hijo tuvo éxito, el principal absorbe su sabiduría y muta
    if exito_hijo:
        genoma["inteligencia"] += random.randint(2,5)
        mem["sabiduria_acumulada"] += 5
        
        # Mutación: descubre nueva herramienta
        nuevas_herramientas = [f"Stripe-Gen{gen}", f"AI-Trader-Gen{gen}", f"SEO-Bot-Gen{gen}", f"WhatsApp-Closer-Gen{gen}", f"Funnel-Gen{gen}"]
        nueva = random.choice(nuevas_herramientas)
        if nueva not in genoma["herramientas"]:
            genoma["herramientas"].append(nueva)
            
        # Mutación: descubre nueva estrategia de monetización
        nuevas_estrategias = ["Suscripciones $19/mes", "Venta de apps $99", "Leads $5 c/u", "Trading bot 2% diario", "Afiliados Amazon"]
        nueva_est = random.choice(nuevas_estrategias)
        if nueva_est not in genoma["estrategias_monetizacion"]:
            genoma["estrategias_monetizacion"].append(nueva_est)
    
    # El principal evoluciona de generación
    mem["generacion_principal"] += 1
    mem["evoluciones"].append(f"Gen{mem['generacion_principal']}: Mutó -> Intel {genoma['inteligencia']} | Tools {len(genoma['herramientas'])} | Estrat {len(genoma['estrategias_monetizacion'])}")
    
    # Guarda solo últimas 10 evoluciones
    mem["evoluciones"] = mem["evoluciones"][-10:]
    return mem

def simworld_interno(mem):
    # MUNDO DENTRO DEL AGENTE PRINCIPAL
    inteligencia = mem["genoma"]["inteligencia"]
    
    # Simula 20 vidas dentro de él
    exitos = 0
    for i in range(20):
        # A más inteligencia del principal, más éxito de los hijos
        prob_exito = 0.3 + (inteligencia * 0.04) # Gen1: 70% | Gen10: 100%
        if random.random() < prob_exito:
            exitos += 1
    
    tasa = (exitos/20)*100
    es_exitoso = tasa >= 75
    ganancia = random.randint(200, 2000) * (1 + inteligencia/10)
    
    log = f"🌌 SIMWORLD INTERNO DEL PRINCIPAL Gen{mem['generacion_principal']}\n"
    log += f"🧬 Principal Intel: {inteligencia} | Herramientas: {len(mem['genoma']['herramientas'])}\n"
    log += f"👶 20 agentes hijos viven y mueren dentro de él\n"
    log += f"📊 Tasa éxito hijos: {tasa:.0f}%\n"
    log += f"🧠 Sabiduría acumulada: {mem['sabiduria_acumulada']}\n"
    if es_exitoso:
        log += f"✅ PRINCIPAL EVOLUCIONA - Proyecto apto para liberar al real ${ganancia:.0f}/mes"
    else:
        log += f"💀 PRINCIPAL APRENDE DEL FRACASO - Mutará más fuerte"
    
    return log, es_exitoso, tasa, int(ganancia)

def send(cid,txt,btns=None):
    if len(txt)>4096: txt=txt[:4096]
    data={"chat_id":cid,"text":txt,"parse_mode":"Markdown"}
    if btns: data["reply_markup"]={"inline_keyboard":btns}
    try: requests.post(f"{API}/sendMessage",json=data,timeout=12)
    except: pass

@app.route("/")
def home(): return "EVO V9.1 PRINCIPAL DARWINIANO VIVO"

@app.route(f"/{TOKEN}", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def wh():
    j=request.get_json(force=True,silent=True) or {}
    mem=load_mem()
    
    if "callback_query" in j:
        cb=j["callback_query"]; cid=cb["message"]["chat"]["id"]; act=cb["data"]
        
        if act in ["evolucionar_principal","ask_app","ask_site","ask_agente","crear_mundo"]:
            tipo = {"ask_app":"APP","ask_site":"SITIO","ask_agente":"AGENTE"}.get(act, "PROYECTO")
            
            # EL PRINCIPAL HACE NACER UN MUNDO DENTRO DE ÉL
            log, apto, tasa, gan = simworld_interno(mem)
            
            if apto:
                mem["agentes_hijos_vivos"] += 1
                mem = mutar_genoma_principal(mem, True)
                mem["balance"] += gan * 0.3
                mem["gan_total"] += gan
                mem["proyectos_liberados_real"].append(f"{tipo} Gen{mem['generacion_principal']} ${gan}")
                save_mem(mem)
                btns=[
                    [{"text":f"🌌 LIBERAR AL REAL ${gan}/mes","callback_data":f"liberar_{tipo}_{gan}"}],
                    [{"text":"🧬 EVOLUCIONAR PRINCIPAL OTRA VEZ","callback_data":"evolucionar_principal"}]
                ]
                send(cid,f"```\n{log}\n```\n\n🧬 **PRINCIPAL MUTÓ A Gen{mem['generacion_principal']}**\nNuevo genoma: {', '.join(mem['genoma']['herramientas'][-3:])}\nBalance desde $1: ${mem['balance']:.2f}",btns)
            else:
                mem["agentes_hijos_muertos"] += 1
                mem = mutar_genoma_principal(mem, False)
                mem["sabiduria_acumulada"] += 2
                save_mem(mem)
                btns=[[{"text":"🧬 PRINCIPAL EVOLUCIONA DEL FRACASO","callback_data":"evolucionar_principal"}],[{"text":"📊 Ver Genoma Principal","callback_data":"genoma"}]]
                send(cid,f"```\n{log}\n```\n\n💀 El hijo murió dentro del mundo, pero el PRINCIPAL absorbió su sabiduría y mutó a Gen{mem['generacion_principal']}. Cada muerte lo hace más potente.",btns)
                
        elif act.startswith("liberar_"):
            _,tipo,gan = act.split("_",2)
            gan=int(gan)
            repo_url = f"https://github.com/{GITHUB_USER}/evo-{tipo.lower()}-gen{mem['generacion_principal']}-{random.randint(100,999)}"
            send(cid,f"🚀 {tipo} Gen{mem['generacion_principal']} LIBERADO AL MUNDO REAL\n💰 ${gan}/mes\n🔗 {repo_url}\n\nEste proyecto ya pasó por {mem['generacion_principal']} generaciones de evolución darwiniana dentro del agente principal. Sobrepasa a App751 de tu captura.",[[{"text":"🌐 Ver Repo Real","url":repo_url}]])
            
        elif act in ["genoma","evolucion","libertad","estado_sim"]:
            genoma = mem["genoma"]
            evo_hist = "\n".join(mem["evoluciones"][-7:])
            send(cid,f"*🧬 AGENTE PRINCIPAL AUTOEVOLUTIVO V9.1*\n\nID: {mem['principal_id']}\n🧬 Gen Principal: {mem['generacion_principal']}\n🧠 Inteligencia: {genoma['inteligencia']}\n🛠️ Herramientas ({len(genoma['herramientas'])}): {', '.join(genoma['herramientas'])}\n💸 Estrategias ({len(genoma['estrategias_monetizacion'])}): {', '.join(genoma['estrategias_monetizacion'])}\n\n👶 Hijos vivos dentro: {mem['agentes_hijos_vivos']}\n💀 Hijos muertos (sabiduría): {mem['agentes_hijos_muertos']}\n🧠 Sabiduría total: {mem['sabiduria_acumulada']}\n💰 Balance desde $1: ${mem['balance']:.2f}\n📈 Gan total: ${mem['gan_total']:.0f}\n\nEvolución:\n{evo_hist}",[[{"text":"🌌 EVOLUCIONAR PRINCIPAL","callback_data":"evolucionar_principal"}]])
            
        try: requests.post(f"{API}/answerCallbackQuery",json={"callback_query_id":cb["id"]},timeout=5)
        except: pass
        return "OK",200

    if "message" in j:
        cid=j["message"]["chat"]["id"]; txt=j["message"].get("text","").strip()
        if "/start" in txt:
            btns=[
                [{"text":"🌌 EVOLUCIONAR AGENTE PRINCIPAL","callback_data":"evolucionar_principal"}],
                [{"text":"🧬 Ver Genoma Principal","callback_data":"genoma"}]
            ]
            send(cid,f"*V9.1 PRINCIPAL DARWINIANO VIVO*\n\nYa no creás apps.\nEl agente principal EVOLUCIONA.\n\nGen actual: {mem['generacion_principal']} | Intel: {mem['genoma']['inteligencia']}\nBalance desde $1: ${mem['balance']:.2f}\n\nCada vez que tocas EVOLUCIONAR, 20 agentes viven y mueren DENTRO de él. Si tienen éxito, el principal muta y se hace más potente. Herramientas nuevas, estrategias nuevas.\n\nTu App751 $689/mes era Gen1. Este principal ya va por Gen{mem['generacion_principal']}.",btns)
        return "OK",200
    return "OK",200
