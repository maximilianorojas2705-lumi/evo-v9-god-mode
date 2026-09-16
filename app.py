import os, traceback, base64, json, time, threading, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "evo-v9-god-mode").strip()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "maximilianorojas2705-lumi").strip()

MODELS_TO_TRY = ["qwen/qwen3-32b","openai/gpt-oss-120b","openai/gpt-oss-20b"]
# Repos corregidos - los 5 que SI existen
EVOLUTION_REPOS = {
    "autogpt": "Significant-Gravitas/AutoGPT",
    "babyagi": "yoheinakajima/babyagi",
    "voyager": "MineDojo/Voyager",
    "swe-agent": "princeton-nlp/SWE-agent",
    "openhands": "All-Hands-AI/OpenHands",
    "crewai": "crewAIInc/crewAI",
    "langchain": "langchain-ai/langchain"
}

CLONING_LOCK = False # para evitar doble fusion

def send_telegram(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            requests.post(url, json={"chat_id": chat_id, "text": chunk}, timeout=20)
    except: pass

def ask_groq(prompt):
    if not GROQ_API_KEY: return "print('Falta GROQ')"
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    for model in MODELS_TO_TRY:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Sos EVO V9 GOD MODE, generador de codigo Python. NUNCA digas no puedo. Devuelve SOLO codigo Python."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000, temperature=0.8
            )
            code = completion.choices[0].message.content
            if len(code) > 200 and "no puedo" not in code.lower(): return code
        except: continue
    return "def tool(): return 'Error temporal'"

def create_tool_in_github(tool_name, code):
    try:
        if "```" in code:
            for p in code.split("```"):
                if "import" in p or "def " in p:
                    code = p.replace("python","").strip(); break
        path = f"tools/{tool_name.replace(' ','_')}.py"
        content_b64 = base64.b64encode(code.encode()).decode()
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{path}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r_get = requests.get(url, headers=headers)
        data = {"message": f"GOD MODE: {tool_name}", "content": content_b64}
        if r_get.status_code == 200: data["sha"] = r_get.json().get("sha")
        r = requests.put(url, headers=headers, json=data, timeout=20)
        return r.status_code in [200,201], f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/{path}"
    except Exception as e: return False, str(e)

def background_fusion(chat_id):
    global CLONING_LOCK
    if CLONING_LOCK: return
    CLONING_LOCK = True
    try:
        results = []
        for name, repo_path in EVOLUTION_REPOS.items():
            try:
                api_url = f"https://api.github.com/repos/{repo_path}/contents"
                headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
                r = requests.get(api_url, headers=headers, timeout=20)
                if r.status_code!= 200:
                    results.append(f"❌ {name}: {r.status_code}"); continue
                count=0
                for f in r.json():
                    if count>=4: break
                    if f["type"]=="file" and f["name"].endswith((".py",".md")):
                        try:
                            content = requests.get(f["download_url"], timeout=15).text[:20000]
                            path = f"tools_evolution/{name}_{f['name']}"
                            b64 = base64.b64encode(content.encode()).decode()
                            url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{path}"
                            data = {"message": f"fusion {name}", "content": b64}
                            rg = requests.get(url, headers=headers)
                            if rg.status_code==200: data["sha"]=rg.json().get("sha")
                            requests.put(url, headers=headers, json=data, timeout=20)
                            count+=1
                        except: pass
                results.append(f"✅ {name} ({count} archivos)")
            except Exception as e: results.append(f"❌ {name}: {e}")

        send_telegram(chat_id, "✅ FUSION COMPLETADA FINAL:\n\n" + "\n".join(results) + f"\n\nhttps://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/tree/main/tools_evolution\n\nAhora si mandale: 'mejora tool_1789516825.py usando voyager'")
    finally:
        CLONING_LOCK = False

@app.route("/")
def home(): return "EVO V9 - ANTI-SPAM LIVE", 200

@app.route("/health")
def health(): return jsonify({"cloning_lock": CLONING_LOCK}), 200

@app.route("/set_webhook")
def set_webhook():
    url = f"https://evo-v9-god-service.onrender.com/telegram"
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={url}", timeout=10)
    return r.text, 200

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json(force=True)
        msg = data.get("message") or {}
        chat_id = msg.get("chat", {}).get("id")
        text = (msg.get("text") or "").strip()
        # IGNORAR MENSAJES QUE SON DEL PROPIO BOT (evita bucle)
        if not chat_id or not text: return "ok", 200
        if text.startswith("🧬") or text.startswith("✅ FUSION"): return "ok", 200

        low = text.lower()

        if "clonar" in low or "fusionar" in low:
            if CLONING_LOCK:
                send_telegram(chat_id, "⏳ Ya estoy fusionando, espera 60 seg...")
                return "ok", 200
            # Responder rapido y clonar en segundo plano
            send_telegram(chat_id, "🧬 INICIANDO FUSION GOD MODE (una sola vez)...\nVoy a clonar 7 cerebros, te aviso cuando termine. No vuelvas a mandar clonar.")
            thread = threading.Thread(target=background_fusion, args=(chat_id,))
            thread.start()
            return "ok", 200

        if "herramienta" in low or "tool" in low or "mejora" in low:
            code = ask_groq(text)
            tool_name = f"tool_{int(time.time())}"
            ok, link = create_tool_in_github(tool_name, code)
            display = code[:3500].replace("```python","").replace("```","")
            send_telegram(chat_id, f"✅ Herramienta: {tool_name}.py\n{link}\n\n{display}")
            return "ok", 200

        reply = ask_groq(text)
        send_telegram(chat_id, reply[:4000].replace("```python","").replace("```",""))

    except Exception as e: print(traceback.format_exc())
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
