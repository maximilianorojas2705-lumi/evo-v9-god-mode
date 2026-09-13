import threading

# ---- Config Telegram ----
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else None

def enviar_telegram(chat_id, texto):
    if not TELEGRAM_API: return
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage",
                      json={"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"},
                      timeout=10)
    except Exception as e:
        print(f"[TG ERROR] {e}")

def procesar_mensaje(chat_id, texto):
    """Ejecuta el flujo completo según la intención del usuario"""
    t = texto.strip().lower()
    
    if t in ("/start", "/ayuda", "hola", "inicio"):
        enviar_telegram(chat_id, 
            "🤖 *Lumi Gen15*\n\n"
            "Comandos:\n"
            "• `aprender <tema>` - Navego y guardo en memoria\n"
            "• `crear <tema>` - Fabrico app y la subo a GitHub\n"
            "• `evolucion` - Veo mi progreso Gen14→Gen15\n"
            "• `salud` - Estado de mis tokens")
    
    elif t.startswith("aprender "):
        tema = texto.strip()[9:].strip()
        enviar_telegram(chat_id, f"🔍 Navegando web sobre *{tema}*...")
        fuentes = navegar_web_real(tema)
        mem = guardar_conocimiento(tema, f"Resumen Gen15 de {tema}")
        pensamiento = pensar_como_lumi(tema)
        enviar_telegram(chat_id,
            f"✅ *Aprendido: {tema}*\n\n"
            f"💭 {pensamiento}\n\n"
            f"📚 Fuentes:\n" + "\n".join(fuentes[:3]) +
            f"\n\n💾 Memoria: `{mem['status']}`")
    
    elif t.startswith("crear "):
        tema = texto.strip()[6:].strip()
        nombre = re.sub(r"[^a-z0-9-]", "-", tema.lower())[:20]
        enviar_telegram(chat_id, 
            f"⚙️ *Fabricando laboratorio* `{tema}`...\n"
            f"(Esto tarda 30-60 segundos, te aviso cuando esté listo 🚀)")
        
        # Ejecutar en hilo separado (Groq tarda ~20s)
        def trabajo():
            try:
                codigo = fabricar_app_con_ia(tema)
                res = liberar_en_github(nombre, codigo)
                enviar_telegram(chat_id,
                    f"🚀 *Laboratorio Listo*\n\n"
                    f"📦 Repo: [GitHub]({res['repo']})\n"
                    f"🌐 Deploy: [{res['deploy'].replace('https://','')}]({res['deploy']})\n\n"
                    f"📝 Código: {len(codigo.splitlines())} líneas\n"
                    f"✨ Status: `{res['status']}`")
            except Exception as e:
                enviar_telegram(chat_id, f"❌ Error fabricando:\n`{str(e)[:200]}`")
        
        threading.Thread(target=trabajo, daemon=True).start()
    
    elif t in ("evolucion", "evolución", "gen"):
        enviar_telegram(chat_id, "📊 Midiendo evolución Gen14→Gen15...")
        datos = evolucionar()
        enviar_telegram(chat_id,
            f"🧬 *Evolución*\n\n"
            f"Gen: `{datos['gen']}`\n"
            f"Inteligencia: *{datos['inteligencia']}*\n"
            f"Repos Gen15: {datos['repos_gen15']}")
    
    elif t in ("salud", "status", "estado"):
        enviar_telegram(chat_id,
            f"🩺 *Estado del sistema*\n\n"
            f"Groq: {'✅' if GROQ_API_KEY else '❌'}\n"
            f"GitHub: {'✅' if GITHUB_TOKEN else '❌'}\n"
            f"Supabase: {'✅' if SUPABASE_URL else '❌'}\n"
            f"Telegram: ✅")
    
    else:
        enviar_telegram(chat_id, 
            f"🤔 No entendí. Usa:\n"
            f"`aprender <tema>` o `crear <tema>`\n"
            f"Ej: `crear ingenieria informatica`")

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.get_json(silent=True) or {}
    msg = data.get("message") or data.get("edited_message") or {}
    texto = (msg.get("text") or "").strip()
    chat_id = msg.get("chat", {}).get("id")
    
    if texto and chat_id:
        threading.Thread(target=procesar_mensaje, args=(chat_id, texto), daemon=True).start()
    
    return "ok", 200

@app.route("/telegram/set_webhook")
def set_webhook():
    """Llama a este endpoint UNA VEZ para conectar Telegram"""
    if not TELEGRAM_API:
        return "ERROR: TELEGRAM_BOT_TOKEN no configurado", 500
    url = f"https://evo-v9-god-service.onrender.com/telegram"
    r = requests.post(f"{TELEGRAM_API}/setWebhook", json={"url": url}, timeout=10)
    return jsonify(r.json())
