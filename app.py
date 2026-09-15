import os, traceback, base64, json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "evo-v9-god-mode").strip() # solo nombre del repo
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "").strip()

# Modelos que SI funcionan con plan gratis en 2026
MODELS_TO_TRY = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "qwen/qwen3-32b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]

print(f"BOT_TOKEN ok: {bool(BOT_TOKEN)} len={len(BOT_TOKEN)}")
print(f"GROQ ok: {bool(GROQ_API_KEY)}")

def send_telegram(chat_id, text):
    if not BOT_TOKEN or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        # Telegram max 4096 chars
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            r = requests.post(url, json={"chat_id": chat_id, "text": chunk}, timeout=15)
            print(f"send_telegram {r.status_code}: {r.text[:200]}")
        return True
    except Exception as e:
        print(f"send_telegram ERROR: {e} {traceback.format_exc()}")
        return False

def ask_groq(prompt):
    if not GROQ_API_KEY:
        return "⚠️ Falta GROQ_API_KEY en Render Environment"
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        last_error = ""
        for model in MODELS_TO_TRY:
            try:
                print(f"Intentando modelo: {model}")
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Sos EVO V9 GOD MODE, un agente autoevolutivo. Respondé corto, en español, y si te piden crear herramienta, crea código python."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1024,
                    temperature=0.7
                )
                return completion.choices[0].message.content
            except Exception as me:
                last_error = str(me)
                print(f"Modelo {model} falló: {me}")
                continue
        return f"❌ Todos los modelos fallaron. Último error: {last_error}"
    except Exception as e:
        print(f"ask_groq ERROR: {e} {traceback.format_exc()}")
        return f"Error Groq: {e}"

def create_tool_in_github(tool_name, code):
    """Crea archivo en tools/ y lo sube a GitHub - GOD MODE"""
    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        return False, "Falta GITHUB_TOKEN o GITHUB_USERNAME en Environment"
    try:
        # Limpiar nombre
        tool_name = tool_name.replace(" ", "_").replace(".py","") + ".py"
        path = f"tools/{tool_name}"
        content_b64 = base64.b64encode(code.encode()).decode()

        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{path}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        # Ver si existe para sacar sha
        r_get = requests.get(url, headers=headers)
        sha = r_get.json().get("sha") if r_get.status_code == 200 else None

        data = {
            "message": f"GOD MODE: crear herramienta {tool_name}",
            "content": content_b64
        }
        if sha:
            data["sha"] = sha

        r = requests.put(url, headers=headers, json=data, timeout=15)
        if r.status_code in [200,201]:
            return True, f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/{path}"
        else:
            return False, f"GitHub error {r.status_code}: {r.text[:500]}"
    except Exception as e:
        return False, f"Excepcion GitHub: {e} {traceback.format_exc()}"

@app.route("/")
def home():
    return "EVO V9 GOD MODE - LIVE", 200

@app.route("/health")
def health():
    return jsonify({
        "bot_token": bool(BOT_TOKEN),
        "groq": bool(GROQ_API_KEY),
        "github": bool(GITHUB_TOKEN),
        "models_try": MODELS_TO_TRY
    }), 200

@app.route("/set_webhook")
def set_webhook():
    if not BOT_TOKEN:
        return "Falta BOT_TOKEN", 500
    url = f"https://evo-v9-god-service.onrender.com/telegram"
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={url}", timeout=10)
    return r.text, 200

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json(force=True)
        print(f"=== TELEGRAM DATA: {json.dumps(data)[:1000]}")
        msg = data.get("message") or data.get("edited_message") or {}
        chat_id = msg.get("chat", {}).get("id")
        text = (msg.get("text") or "").strip()

        if not chat_id:
            return "ok", 200
        if not text:
            send_telegram(chat_id, "👋 Mandame texto, EVO V9 está vivo.")
            return "ok", 200

        # COMANDO GOD MODE: crear herramienta
        low = text.lower()
        if low.startswith("crea una herramienta") or low.startswith("crear herramienta") or low.startswith("/tool"):
            prompt_code = f"Crea código python completo para: {text}. Solo devuelve código python listo para usar, sin explicaciones extra."
            code = ask_groq(prompt_code)
            # Limpiar markdown ```python
            if "```" in code:
                code = code.split("```")[1]
                if code.startswith("python"): code = code[6:]
                code = code.strip()

            tool_name = f"tool_{int(__import__('time').time())}"
            ok, link = create_tool_in_github(tool_name, code)
            if ok:
                send_telegram(chat_id, f"✅ Herramienta creada: {tool_name}.py\n\n{link}\n\nCódigo:\n{code[:3000]}")
            else:
                send_telegram(chat_id, f"⚠️ Código generado pero falló GitHub:\n{link}\n\nCódigo:\n{code[:3000]}")
            return "ok", 200

        # Chat normal
        reply = ask_groq(text)
        send_telegram(chat_id, reply)

    except Exception as e:
        print(f"ERROR /telegram: {e} {traceback.format_exc()}")
        try:
            chat_id = request.get_json().get("message",{}).get("chat",{}).get("id")
            if chat_id: send_telegram(chat_id, f"Error interno pero sigo vivo: {e}")
        except: pass

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
