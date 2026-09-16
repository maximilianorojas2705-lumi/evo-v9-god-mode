import os, traceback, base64, time, requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "evo-v9-god-mode").strip()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "maximilianorojas2705-lumi").strip()

# TODOS LOS GOD - LOS 8 MAS POTENTES PARA CLONAR Y MEJORAR IA
EVOLUTION_REPOS = {
    "dgm-official": "jennyzzt/dgm",
    "generic-agent": "lsdefine/GenericAgent",
    "autoresearch": "Maleick/AutoResearch",
    "auto-evo-skills": "ZhanlinCui/Auto-Evolution-Agent-Skills",
    "self-improving-ai": "KBB99/self-improving-ai",
    "alice-agent": "stuko0/alice-agent",
    "awesome-evo": "EvoMap/awesome-agent-evolution",
    "awesome-self-improving": "selfimproving-agent/Awesome-Self-Improving-Agents",
    "openhands": "All-Hands-AI/OpenHands",
    "godel-agent-paper": "lobehub/awesome-rsi",
}

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
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {"role": "system", "content": "Sos EVO V9 GOD MODE. Solo codigo Python autoevolutivo."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500, temperature=0.9
        )
        return completion.choices[0].message.content
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
def home(): return "EVO V9 - CLONADOR DE IA LIVE", 200

@app.route("/fusion")
def fusion():
    logs = []
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    for name, repo_path in EVOLUTION_REPOS.items():
        try:
            r = requests.get(f"https://api.github.com/repos/{repo_path}/contents", headers=headers, timeout=20)
            if r.status_code!=200:
                logs.append(f"❌ {name}: {r.status_code}"); continue
            count=0
            for f in r.json():
                if count>=3: break
                if f["type"]=="file" and f["name"].endswith((".py",".md",".json")):
                    try:
                        content = requests.get(f["download_url"], timeout=15).text[:15000]
                        if len(content) < 50: continue
                        ok = github_push(f"tools_evolution/{name}_{f['name']}", content, f"fusion {name}")
                        if ok: count+=1
                    except: pass
            logs.append(f"✅ {name} ({count})")
        except Exception as e: logs.append(f"❌ {name}: {e}")
    return "<h1>✅ FUSION GOD FINAL - 10 CEREBROS</h1><br>" + "<br>".join(logs)

@app.route("/fusion_god")
def fusion_god():
    # Motor definitivo que CLONA IA y la mejora - Gödel Agent + DGM + GenericAgent
    god_engine = '''
import random, time, shutil
from pathlib import Path

class GodAgent:
    """Agente autoevolutivo que CLONA su propia IA y la mejora - estilo Gödel Agent ACL 2025 + DGM Sakana"""
    def __init__(self):
        self.root = Path("tools")
        self.evo_root = Path("tools_evolution")
        self.population = list(self.root.glob("tool_*.py"))
        print(f"Poblacion inicial: {len(self.population)}")

    def clone_ai(self, source_path):
        """Clona una IA (un archivo tool) como si fuera un organismo"""
        clone_name = f"tools/tool_clone_{source_path.stem}_{int(time.time())}.py"
        shutil.copy(source_path, clone_name)
        print(f"🧬 Clonado: {source_path} -> {clone_name}")
        return Path(clone_name)

    def godel_improve(self, clone_path):
        """Gödel Agent style: inspecciona y reescribe su propia logica"""
        code = clone_path.read_text()
        # Mutaciones inspiradas en GenericAgent 3.3K seed + AutoResearch Plan->Modify->Verify
        mutations = [
            "# [GODEL] Auto-reflection: improving reasoning\\n",
            "# [DGM] Population-based evolution step\\n",
            "# [GenericAgent] Skill tree growth\\n",
            "import random, json, time # self-evolving imports\\n"
        ]
        improved = random.choice(mutations) + code
        # Anade una nueva funcion auto-generada
        new_func = f"""
def self_improve_{random.randint(1000,9999)}():
    '''Funcion auto-generada por evolucion'''
    return "Mejora {random.random()} - {time.time()}"
"""
        improved += new_func
        clone_path.write_text(improved)
        print(f"🔧 Mejorado: {clone_path}")

    def evaluate_and_keep(self, clone_path):
        """AutoResearch: Keep/Discard"""
        try:
            # Test rapido que no crashee
            compile(clone_path.read_text(), str(clone_path), 'exec')
            score = len(clone_path.read_text()) % 100
            if score > 30:
                print(f"✅ KEEP {clone_path} score {score}")
                return True
            else:
                clone_path.unlink()
                print(f"❌ DISCARD {clone_path}")
                return False
        except Exception as e:
            print(f"❌ ERROR {clone_path}: {e}")
            clone_path.unlink()
            return False

    def evolve_forever(self, gens=20):
        """Loop infinito: Clonar -> Mejorar -> Verificar -> Keep/Discard"""
        for i in range(gens):
            if not self.population: break
            source = random.choice(self.population)
            clone = self.clone_ai(source)
            self.godel_improve(clone)
            if self.evaluate_and_keep(clone):
                self.population.append(clone)
            time.sleep(0.5)

if __name__ == "__main__":
    agent = GodAgent()
    agent.evolve_forever(50)
'''
    github_push("tools_evolution/GOD_ENGINE_clone_and_improve.py", god_engine, "GOD ENGINE - clonador de IA autoevolutivo")
    return "<h1>✅ GOD ENGINE CREADO</h1><br>Se creó GOD_ENGINE_clone_and_improve.py - clona IAs y las mejora estilo Gödel Agent + GenericAgent"

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
        if text.startswith("✅"): return "ok", 200
        low = text.lower()

        if "clonar" in low or "fusion" in low or "potenciar" in low:
            send_telegram(chat_id, "🔗 GOD FUSION FINAL - 10 cerebros:\\nhttps://evo-v9-god-service.onrender.com/fusion\\n\\nY el motor que clona IA y se mejora solo:\\nhttps://evo-v9-god-service.onrender.com/fusion_god")
            return "ok", 200

        if "herramienta" in low or "tool" in low or "crea" in low or "mejora" in low or "godel" in low or "clona" in low:
            code = ask_groq(text)
            if "```" in code:
                for p in code.split("```"):
                    if "import" in p or "def " in p:
                        code = p.replace("python","").strip(); break
            tool_name = f"tool_{int(time.time())}"
            github_push(f"tools/{tool_name}.py", code, f"GOD: {tool_name}")
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/tools/{tool_name}.py"
            send_telegram(chat_id, f"✅ {tool_name}.py\\n{link}\\n\\n{code[:3500]}")
            return "ok", 200

        reply = ask_groq(text)[:4000].replace("```python","").replace("```","")
        send_telegram(chat_id, reply)
    except Exception as e: print(e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
