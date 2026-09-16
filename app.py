import os, base64, time, requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "evo-v9-god-mode").strip()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "maximilianorojas2705-lumi").strip()

# AHORA CON FREEBUFF + TODO LO ANTERIOR
EVOLUTION_REPOS = {
    "freebuff": "CodebuffAI/freebuff",
    "dgm-official": "jennyzzt/dgm",
    "hgm-godel": "metauto-ai/HGM",
    "godel-agent-code": "Arvid-pku/Godel_Agent",
    "generic-agent": "lsdefine/GenericAgent",
    "prime-agent": "PrimeIntellect-ai/prime-agent",
    "hermes-agent": "NousResearch/hermes-agent",
    "evoagentx": "EvoAgentX/EvoAgentX",
    "adclaw-marketing": "icedarold/adclaw",
    "marketing-skills": "coreyhaines31/marketingskills",
    "vibe-trading": "HKUDS/Vibe-Trading",
    "tiktok-scraper": "maja-829/tiktok-comments-scraper",
    "openhands": "All-Hands-AI/OpenHands",
    "awesome-evo": "EvoMap/awesome-agent-evolution",
}

def github_push(path, code, msg):
    try:
        b64 = base64.b64encode(code.encode()).decode()
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{path}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r_get = requests.get(url, headers=headers, timeout=15)
        data = {"message": f"{msg} [skip render]", "content": b64}
        if r_get.status_code == 200:
            data["sha"] = r_get.json().get("sha")
        r = requests.put(url, headers=headers, json=data, timeout=20)
        return r.status_code in [200,201]
    except:
        return False

def send_telegram(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            requests.post(url, json={"chat_id": chat_id, "text": chunk}, timeout=15)
    except: pass

def ask_groq(prompt):
    if not GROQ_API_KEY: return "def tool(): return 'Falta GROQ'"
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    try:
        c = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[{"role":"system","content":"Sos EVO V9 GOD MODE. Solo codigo Python."},{"role":"user","content":prompt}],
            max_tokens=2500, temperature=0.9
        )
        return c.choices[0].message.content
    except: return "def tool(): return 'Error'"

@app.route("/")
def home(): return "EVO V9 - FREEBUFF LIVE", 200

@app.route("/fusion")
def fusion():
    logs = []
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    for name, repo_path in EVOLUTION_REPOS.items():
        try:
            r = requests.get(f"https://api.github.com/repos/{repo_path}/contents", headers=headers, timeout=20)
            if r.status_code!= 200: continue
            count = 0
            for f in r.json():
                if count >= 2: break
                if f["type"] == "file" and f["name"].endswith((".py",".md",".json",".ts")):
                    try:
                        content = requests.get(f["download_url"], timeout=10).text[:12000]
                        if len(content) < 80: continue
                        if github_push(f"tools_evolution/{name}_{f['name']}", content, f"fusion {name}"):
                            count += 1
                    except: pass
            logs.append(f"OK {name} ({count})")
        except: pass
    return "<h1>FUSION 14 CEREBROS + FREEBUFF</h1><br>" + "<br>".join(logs)

@app.route("/fusion_freebuff")
def fusion_freebuff():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    try:
        # Clona el repo completo de freebuff
        r = requests.get("https://api.github.com/repos/CodebuffAI/freebuff/contents", headers=headers, timeout=20)
        cloned = 0
        logs = []
        if r.status_code == 200:
            for f in r.json():
                if f["type"] == "file" and f["name"].endswith((".md",".json",".ts",".js")):
                    try:
                        content = requests.get(f["download_url"], timeout=10).text[:12000]
                        if github_push(f"tools_evolution/freebuff_{f['name']}", content, "adherir freebuff"):
                            cloned += 1
                            logs.append(f"OK freebuff_{f['name']}")
                        if cloned >= 10: break
                    except: pass
        # Adhiere habilidad especifica de freebuff como tool
        freebuff_skill = '''
# Habilidad adherida de CodebuffAI/freebuff - The free coding agent
import random
class FreebuffAgent:
    """Agente de codificacion gratis con agentes especializados - inspirado en freebuff"""
    def __init__(self):
        self.agents = ["code-reviewer", "bug-fixer", "feature-builder", "doc-writer"]
    def run_agent(self, task, agent_type="feature-builder"):
        return f"[Freebuff {agent_type}] Ejecutando: {task} - modelo elegido automaticamente"
    def choose_model(self):
        models = ["claude-3.5", "gpt-4o", "qwen3-32b", "deepseek"]
        return random.choice(models)
'''
        github_push("tools/freebuff_agent_skill.py", freebuff_skill, "add freebuff skill")
        return f"<h1>FREEBUFF ADHERIDO - {cloned} archivos + skill</h1><br>" + "<br>".join(logs) + "<br><br>Skill creado: tools/freebuff_agent_skill.py"
    except Exception as e:
        return f"Error freebuff: {e}"

@app.route("/fusion_skills")
def fusion_skills():
    tiktok_code = 'import random\nclass TikTokViralScraper:\n def get_trending_hashtags(self): return ["#viral","#fyp"]\n def scrape_comments_insights(self, url): return {"viral_score": random.randint(70,99)}\n'
    trading_code = 'import random\nclass TradingSkill:\n def analyze_market(self, s="BTC"): return {"signal": random.choice(["BUY","SELL","HOLD"])}\n'
    marketing_code = 'class MarketingGrowthSkill:\n def generate_ad_copy(self, p): return {"hook": f"Este {p} cambio mi vida"}\n'
    github_push("tools/tiktok_viral_scraper.py", tiktok_code, "skill tiktok")
    github_push("tools/trading_agent_skill.py", trading_code, "skill trading")
    github_push("tools/marketing_growth_skill.py", marketing_code, "skill marketing")
    return "<h1>OK HABILIDADES</h1>"

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
        if not chat_id or not text: return "ok", 200
        low = text.lower()
        if "fusion" in low or "freebuff" in low or "clonar" in low:
            send_telegram(chat_id, "FREEBUFF:\\nhttps://evo-v9-god-service.onrender.com/fusion_freebuff\\n\\nTODO (14 cerebros):\\nhttps://evo-v9-god-service.onrender.com/fusion")
            return "ok", 200
        if "tool" in low or "crea" in low or "freebuff" in low:
            code = ask_groq(text)
            if "```" in code:
                for p in code.split("```"):
                    if "import" in p or "def " in p:
                        code = p.replace("python","").strip(); break
            tool_name = f"tool_{int(time.time())}"
            github_push(f"tools/{tool_name}.py", code, f"GOD {tool_name}")
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/tools/{tool_name}.py"
            send_telegram(chat_id, f"{tool_name}.py\\n{link}\\n\\n{code[:3500]}")
            return "ok", 200
        reply = ask_groq(text)[:3500].replace("```python","").replace("```","")
        send_telegram(chat_id, reply)
    except Exception as e: print(e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
