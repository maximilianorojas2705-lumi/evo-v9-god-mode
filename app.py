import os, base64, time, requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "evo-v9-god-mode").strip()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "maximilianorojas2705-lumi").strip()

# 30 CEREBROS + HABILIDADES
EVOLUTION_REPOS = {
    # CEREBROS AUTOEVOLUTIVOS
    "dgm-official": "jennyzzt/dgm",
    "hgm-godel": "metauto-ai/HGM",
    "godel-agent-code": "Arvid-pku/Godel_Agent",
    "generic-agent": "lsdefine/GenericAgent",
    "prime-agent": "PrimeIntellect-ai/prime-agent",
    "hermes-agent": "NousResearch/hermes-agent",
    "evoagentx": "EvoAgentX/EvoAgentX",
    "sica": "MaximeRobeyns/self_improving_coding_agent",
    "autocontext": "greyhaven-ai/autocontext",
    "autoresearch": "Maleick/AutoResearch",
    # HABILIDADES Y HERRAMIENTAS NUEVAS
    "adclaw-marketing": "icedarold/adclaw",
    "marketing-skills": "coreyhaines31/marketingskills",
    "vibe-trading": "HKUDS/Vibe-Trading",
    "tiktok-scraper": "maja-829/tiktok-comments-scraper",
    "tiktok-api": "owenleonard11/tiktok-scraper",
    "awesome-ai-tools": "jim-schwoebel/awesome_ai_agents",
    "openhands": "All-Hands-AI/OpenHands",
    "awesome-evo": "EvoMap/awesome-agent-evolution",
    "awesome-rsi": "lobehub/awesome-rsi",
}

def send_telegram(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            requests.post(url, json={"chat_id": chat_id, "text": chunk}, timeout=20)
    except: pass

def ask_groq(prompt):
    if not GROQ_API_KEY: return "def tool(): return 'Falta GROQ'"
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    try:
        c = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[{"role":"system","content":"Sos EVO V9 GOD MODE. Solo codigo Python potente."},{"role":"user","content":prompt}],
            max_tokens=3000, temperature=0.9
        )
        return c.choices[0].message.content
    except: return "def tool(): return 'Error'"

def github_push(path, code, msg):
    try:
        b64 = base64.b64encode(code.encode()).decode()
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{path}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r_get = requests.get(url, headers=headers, timeout=15)
        data = {"message": f"{msg} [skip render]", "content": b64}
        if r_get.status_code == 200: data["sha"] = r_get.json().get("sha")
        r = requests.put(url, headers=headers, json=data, timeout=20)
        return r.status_code in [200,201]
    except: return False

@app.route("/")
def home(): return "EVO V9 - HABILIDADES LIVE", 200

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
                if f["type"] == "file" and f["name"].endswith((".py",".md",".json")):
                    try:
                        content = requests.get(f["download_url"], timeout=15).text[:12000]
                        if len(content) < 50: continue
                        if github_push(f"tools_evolution/{name}_{f['name']}", content, f"skills fusion {name}"):
                            count += 1
                    except: pass
            logs.append(f"OK {name} ({count})")
        except: pass
    return "<h1>FUSION 30 CEREBROS + HABILIDADES</h1><br>" + "<br>".join(logs)

@app.route("/fusion_skills")
def fusion_skills():
    # Adhiere habilidades especificas como herramientas
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    skills_code = {
        "tiktok_viral_scraper.py": '''
import requests, random
class TikTokViralScraper:
    def get_trending_hashtags(self):
        hashtags = ["#viral", "#fyp", "#tiktokshop", "#ecom", "#godmode"]
        return random.sample(hashtags, 3)
    def scrape_comments_insights(self, video_url):
        # Inspirado en maja-829/tiktok-comments-scraper
        return {"sentiment": "positive", "keywords": ["need", "buy", "link"], "viral_score": random.randint(70,99)}
''',
        "trading_agent_skill.py": '''
# Inspirado en HKUDS/Vibe-Trading - Personal trading agent
import random
class TradingSkill:
    def analyze_market(self, symbol="BTC"):
        return {"symbol": symbol, "signal": random.choice(["BUY","SELL","HOLD"]), "confidence": random.randint(60,95)}
    def alert(self, msg): print(f"[TRADING ALERT] {msg}")
''',
        "marketing_growth_skill.py": '''
# Inspirado en icedarold/adclaw 130+ skills + coreyhaines31/marketingskills
class MarketingGrowthSkill:
    def generate_ad_copy(self, product):
        hooks = [f"Este {product} cambió mi vida", f"POV: descubriste {product}", f"Nadie habla de este {product}"]
        return {"hook": hooks[0], "cta": "Link en bio", "seo_keywords": [product, "viral", "2026"]}
    def seo_optimize(self, text):
        return text + " #fyp #viral #godmode"
'''
    }
    logs = []
    for fname, code in skills_code.items():
        if github_push(f"tools/{fname}", code, f"add skill {fname}"):
            logs.append(f"OK {fname}")
    return "<h1>HABILIDADES ADHERIDAS</h1><br>" + "<br>".join(logs)

@app.route("/fusion_deep")
def fusion_deep():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    queries = ["self-evolving agent", "ai marketing skills", "tiktok scraper", "trading bot ai", "growth hacking ai"]
    cloned = 0
    logs = []
    for q in queries:
        try:
            url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=10"
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code!= 200: continue
            for repo in r.json().get("items", [])[:5]:
                repo_full = repo["full_name"]
                try:
                    rc = requests.get(f"https://api.github.com/repos/{repo_full}/contents", headers=headers, timeout=10)
                    if rc.status_code == 200:
                        for f in rc.json():
                            if f["type"]=="file" and f["name"].endswith(".py"):
                                content = requests.get(f["download_url"], timeout=10).text[:10000]
                                if len(content) > 100:
                                    github_push(f"tools_evolution/deep_{repo_full.replace('/','_')}_{f['name']}", content, f"deep {repo_full}")
                                    cloned += 1
                                    logs.append(f"OK {repo_full}")
                                    break
                except: pass
                if cloned > 80: break
        except: pass
        if cloned > 80: break
    return f"<h1>DEEP SCAN - {cloned} REPOS DE HABILIDADES</h1><br>" + "<br>".join(logs[:80])

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
        if "clonar" in low or "fusion" in low or "habilidades" in low or "potenciar" in low or "miles" in low:
            send_telegram(chat_id, "30 CEREBROS:\\nhttps://evo-v9-god-service.onrender.com/fusion\\n\\nHABILIDADES NUEVAS (marketing+trading+tiktok):\\nhttps://evo-v9-god-service.onrender.com/fusion_skills\\n\\nDEEP SCAN MILES:\\nhttps://evo-v9-god-service.onrender.com/fusion_deep")
            return "ok", 200
        if "herramienta" in low or "tool" in low or "crea" in low or "mejora" in low or "marketing" in low or "trading" in low or "tiktok" in low:
            code = ask_groq(text)
            if "```" in code:
                for p in code.split("```"):
                    if "import" in p or "def " in p:
                        code = p.replace("python","").strip(); break
            tool_name = f"tool_{int(time.time())}"
            github_push(f"tools/{tool_name}.py", code, f"GOD: {tool_name}")
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/tools/{tool_name}.py"
            send_telegram(chat_id, f"{tool_name}.py\\n{link}\\n\\n{code[:3500]}")
            return "ok", 200
        reply = ask_groq(text)[:4000].replace("```python","").replace("```","")
        send_telegram(chat_id, reply)
    except Exception as e: print(e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
