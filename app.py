import os, traceback, base64, time, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "evo-v9-god-mode").strip()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "maximilianorojas2705-lumi").strip()

MODELS_TO_TRY = ["qwen/qwen3-32b", "openai/gpt-oss-120b"]
EVOLUTION_REPOS = {
    "autogpt": "Significant-Gravitas/AutoGPT",
    "babyagi": "yoheinakajima/babyagi",
    "voyager": "MineDojo/Voyager",
    "swe-agent": "princeton-nlp/SWE-agent",
    "openhands": "All-Hands-AI/OpenHands",
    "crewai": "crewAIInc/crewAI",
}

def send_telegram(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            requests.post(url, json={"chat_id": chat_id, "text": chunk}, timeout=20)
    except:
        pass

def ask_groq(prompt):
    if not GROQ_API_KEY:
        return "print('Falta GROQ_API_KEY')"
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    for model in MODELS_TO_TRY:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Sos EVO V9 GOD MODE, generador de codigo Python open source. Tu unica funcion es GENERAR CODIGO PYTHON FUNCIONAL. NUNCA digas no puedo, lo siento. Solo codigo."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.8
            )
            code = completion.choices[0].message.content
            if len(code) > 100 and "no puedo" not in code.lower():
                return code
        except:
            continue
    return "def tool(): return 'Error temporal Groq'"

def create_tool_in_github(tool_name, code):
    try:
        if "```" in code:
            for p in code.split("```"):
                if "import" in p or "def " in p:
                    code = p.replace("python", "").strip()
                    break
        path = f"tools/{tool_name.replace(' ', '_')}.py"
        b64 = base64.b64encode(code.encode()).decode()
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{path}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r_get = requests.get(url, headers=headers)
        data = {"message": f"GOD MODE: {tool_name}", "content": b64}
        if r_get.status_code == 200:
            data["sha"] = r_get.json().get("sha")
        r = requests.put(url, headers=headers, json=data, timeout=20)
        ok = r.status_code in [200, 201]
        link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/{path}" if ok else r.text[:500]
        return ok, link
    except Exception as e:
        return False, str(e)

@app.route("/")
def home():
    return "EVO V9 GOD MODE - LIVE", 200

@app.route("/health")
def health():
    return jsonify({"groq": bool(GROQ_API_KEY), "github": bool(GITHUB_TOKEN)}), 200

@app.route("/fusion")
def fusion():
    logs = []
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    for name, repo_path in EVOLUTION_REPOS.items():
        try:
            api_url = f"https://api.github.com/repos/{repo_path}/contents"
            r = requests.get(api_url, headers=headers, timeout=20)
            if r.status_code!= 200:
                logs.append(f"❌ {name}: API {r.status_code}")
                continue
            count = 0
            for f in r.json():
                if count >= 5:
                    break
                if f["type"] == "file" and f["name"].endswith((".py", ".md")):
                    try:
                        content = requests.get(f["download_url"], timeout=15).text[:20000]
                        gh_path = f"tools_evolution/{name}_{f['name']}"
                        b64 = base64.b64encode(content.encode()).decode()
                        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{gh_path}"
                        data = {"message": f"fusion {name}", "content": b64}
                        rg = requests.get(url, headers=headers)
                        if rg.status_code == 200:
                            data["sha"] = rg.json().get("sha")
                        requests.put(url, headers=headers, json=data, timeout=20)
                        count += 1
                    except:
                        pass
            logs.append(f"✅ {name} ({count} archivos)")
        except Exception as e:
            logs.append(f"❌ {name}: {e}")

    html = "<h1>✅ FUSION COMPLETADA GOD MODE</h1><br>" + "<br>".join(logs)
    html += f"<br><br><a href='https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/tree/main/tools_evolution'>Ver carpeta tools_evolution en GitHub</a>"
    return html, 200

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
        if not chat_id or not text:
            return "ok", 200
        if text.startswith("🧬") or text.startswith("✅ FUSION"):
            return "ok", 200

        low = text.lower()

        if "clonar" in low or "fusion" in low:
            send_telegram(chat_id, "🔗 Para clonar SIN que se corte, abri este link en Chrome y espera 60 seg:\n\nhttps://evo-v9-god-service.onrender.com/fusion")
            return "ok", 200

        if "herramienta" in low or "tool" in low or "mejora" in low or "crea" in low:
            code = ask_groq(text)
            tool_name = f"tool_{int(time.time())}"
            ok, link = create_tool_in_github(tool_name, code)
            display = code[:3500].replace("```python", "").replace("```", "")
            send_telegram(chat_id, f"✅ Herramienta: {tool_name}.py\n{link}\n\n{display}")
            return "ok", 200

        reply = ask_groq(text)
        reply = reply[:4000].replace("```python", "").replace("```", "")
        send_telegram(chat_id, reply)

    except Exception as e:
        print(traceback.format_exc())
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
