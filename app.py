import os, base64, time, glob, importlib.util, subprocess, sys, threading, requests
from flask import Flask, request, abort

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "evo-v9-god-mode").strip()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "maximilianorojas2705-lumi").strip()
ADMIN_KEY = os.getenv("ADMIN_KEY", "").strip()
SERVICE_URL = os.getenv("SERVICE_URL", "https://evo-v9-god-service.onrender.com").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
AFILIADO_LINK = os.getenv("AFILIADO_LINK", "").strip()

# Cerebros evolutivos más poderosos de GitHub (sept 2026)
EVOLUTION_REPOS = {
    "openevolve": "algorithmicsuperintelligence/openevolve",
    "agents2-symbolic": "aiwaves-cn/agents",
    "evoagentx": "EvoAgentX/EvoAgentX",
    "dgm": "jennyzzt/dgm",
    "adas": "ShengranHu/ADAS",
    "agentevolver": "modelscope/AgentEvolver",
    "prime-agent": "PrimeIntellect-ai/prime-agent",
    "freebuff": "CodebuffAI/freebuff",
    "hgm-godel": "metauto-ai/HGM",
    "awesome-evolution": "EvoMap/awesome-agent-evolution",
    "self-evolving-survey": "XMUDeepLIT/Awesome-Self-Evolving-Agents",
    "openhands": "All-Hands-AI/OpenHands",
}

# ---------- Skills y contexto ----------
def load_skills():
    skills = {}
    for path in glob.glob("tools/*_skill.py"):
        name = os.path.basename(path)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            skills[name] = mod
        except Exception as e:
            print(f"[skills] error cargando {name}: {e}")
    return skills

def build_brain_context():
    chunks, total = [], 0
    for path in sorted(glob.glob("tools_evolution/*.md")):
        try:
            txt = open(path, "r", errors="ignore").read()[:500]
            chunks.append(f"--- {os.path.basename(path)} ---\n{txt}")
            total += len(txt)
            if total > 6000: break
        except Exception:
            pass
    return "\n".join(chunks)

SKILLS = load_skills()
BRAIN_CONTEXT = build_brain_context()
LAST_CODE = {}
print(f"[evo] skills: {list(SKILLS.keys())} | context: {len(BRAIN_CONTEXT)} chars")

# ---------- Supabase ----------
def sb_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json", "Prefer": "return=minimal"}

def save_memory(chat_id, role, content):
    if not SUPABASE_URL or not SUPABASE_KEY: return
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/memory", headers=sb_headers(),
                      json={"chat_id": chat_id, "role": role, "content": (content or "")[:2000]}, timeout=10)
    except Exception as e:
        print("[sb] save error:", e)

def load_memory(chat_id):
    if not SUPABASE_URL or not SUPABASE_KEY: return []
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/memory", headers=sb_headers(),
                         params={"chat_id": f"eq.{chat_id}", "order": "created_at.desc", "limit": "8"}, timeout=10)
        if r.status_code == 200:
            return list(reversed(r.json()))
    except Exception as e:
        print("[sb] load error:", e)
    return []

# ---------- Sandbox ----------
def run_sandbox(code):
    try:
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=10)
        out = (p.stdout or p.stderr)[:3000]
        return out or "(corrió sin imprimir nada)"
    except subprocess.TimeoutExpired:
        return "Timeout: tardó más de 10 segundos"
    except Exception as e:
        return f"Error de ejecución: {e}"

def fitness(out):
    if out.startswith(("Error", "Timeout")) or "Traceback" in out:
        return 0.0
    return 1.0 + min(len(out), 200) / 200.0

# ---------- Motor evolutivo (estilo OpenEvolve/AlphaEvolve) ----------
def clean_code(raw):
    code = raw
    if "```" in code:
        for p in code.split("```"):
            if "import" in p or "def " in p:
                code = p.replace("python", "").strip()
                break
    return code

def evolve_program(task, generations=3, pop=3):
    population = []
    for i in range(pop):
        raw = ask_groq(f"Escribí un programa Python distinto y creativo que: {task}. Solo código.")
        population.append(clean_code(raw))
    best_code, best_score = None, -1.0
    for gen in range(generations):
        scored = []
        for code in population:
            out = run_sandbox(code)
            scored.append((fitness(out), code, out))
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_code, best_out = scored[0]
        print(f"[evolve] gen {gen+1} mejor score: {best_score:.2f}")
        new_pop = [best_code]
        for sc, code, out in scored[:2]:
            mut = ask_groq(
                f"Task: {task}\nCódigo actual:\n{code[:2000]}\nSalida actual:\n{out[:500]}\n"
                f"Mutá/mejorá este código para cumplir mejor la task. Devolvé SOLO código Python.")
            new_pop.append(clean_code(mut))
        population = new_pop
    return best_code, best_score

def start_evolution(chat_id, task):
    def worker():
        try:
            code, score = evolve_program(task)
            name = f"evolved_{int(time.time())}.py"
            github_push(f"evolution/{name}", code, f"evolve: {task[:40]}")
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/evolution/{name}"
            save_memory(chat_id, "assistant", f"[evolución] {task[:100]} score {score:.2f}")
            send_telegram(chat_id, f"🧬 EVOLUCIÓN COMPLETA\nScore: {score:.2f}\n{link}\n\nMejor individuo:\n{code[:2500]}")
        except Exception as e:
            send_telegram(chat_id, f"Error en evolución: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Seguridad ----------
def admin_only():
    if not ADMIN_KEY or request.args.get("key") != ADMIN_KEY:
        abort(404)

# ---------- Helpers ----------
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
        return r.status_code in [200, 201]
    except Exception:
        return False

def send_telegram(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            requests.post(url, json={"chat_id": chat_id, "text": chunk}, timeout=15)
    except Exception:
        pass

def ask_groq(prompt, history=None):
    if not GROQ_API_KEY:
        return "Falta GROQ_API_KEY"
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    system = ("Sos EVO V9 GOD MODE, un asistente experto con conocimiento de muchos frameworks de agentes. "
              "Si el usuario pide código o una tool, respondé ÚNICAMENTE código Python sin explicaciones. "
              "Si es conversación normal, respondé como texto natural en español, breve y directo.")
    if BRAIN_CONTEXT:
        system += f"\nConocimiento de tus cerebros fusionados:\n{BRAIN_CONTEXT}"
    messages = [{"role": "system", "content": system}]
    for m in (history or []):
        role = m.get("role")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": (m.get("content") or "")[:1500]})
    messages.append({"role": "user", "content": prompt})
    models = [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "openai/gpt-oss-120b",
        "qwen/qwen3-32b",
        "moonshotai/kimi-k2-instruct",
    ]
    for model in models:
        try:
            c = client.chat.completions.create(model=model, messages=messages,
                                               max_tokens=2500, temperature=0.9)
            print(f"[groq] OK con {model}")
            return c.choices[0].message.content
        except Exception as e:
            print(f"[groq] FALLÓ {model}: {str(e)[:150]}")
            if "rate limit" in str(e).lower():
                time.sleep(5)
            continue
    return "def tool(): return 'Todos los modelos fallaron - ver logs'"

def set_commands():
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands", json={"commands": [
            {"command": "start", "description": "Iniciar EVO V9"},
            {"command": "tool", "description": "Crear una tool nueva"},
            {"command": "evolucionar", "description": "Evolucionar un programa (3 generaciones)"},
            {"command": "ejecutar", "description": "Ejecutar la última tool creada"},
            {"command": "skills", "description": "Ver skills cargados"},
            {"command": "memoria", "description": "Ver últimos recuerdos"},
        ]}, timeout=10)
    except Exception as e:
        print("[tg] commands:", e)

set_commands()

# ---------- Rutas ----------
@app.route("/")
def home():
    return f"EVO V9 NIVEL 3 - skills: {len(SKILLS)} - context: {len(BRAIN_CONTEXT)} chars - memoria: {'ON' if SUPABASE_KEY else 'OFF'} - motor evolutivo: ON", 200

@app.route("/fusion")
def fusion():
    admin_only()
    logs = []
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    for name, repo_path in EVOLUTION_REPOS.items():
        try:
            r = requests.get(f"https://api.github.com/repos/{repo_path}/contents", headers=headers, timeout=20)
            if r.status_code != 200: continue
            count = 0
            for f in r.json():
                if count >= 2: break
                if f["type"] == "file" and f["name"].endswith((".py", ".md", ".json", ".ts")):
                    try:
                        content = requests.get(f["download_url"], timeout=10).text[:12000]
                        if len(content) < 80: continue
                        if github_push(f"tools_evolution/{name}_{f['name']}", content, f"fusion {name}"):
                            count += 1
                    except Exception:
                        pass
            logs.append(f"OK {name} ({count})")
        except Exception:
            pass
    return "<h1>FUSION CEREBROS EVOLUTIVOS</h1><br>" + "<br>".join(logs)

@app.route("/set_webhook")
def set_webhook():
    admin_only()
    url = f"{SERVICE_URL}/telegram"
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
        low = text.lower()

        if low.startswith("/start") or low == "hola":
            send_telegram(chat_id, "🧠 EVO V9 NIVEL 3 activo.\nComandos: /tool /evolucionar /ejecutar /skills /memoria")
            return "ok", 200

        if low.startswith("evoluciona") or low.startswith("/evolucionar") or low.startswith("evolve"):
            task = text.split(" ", 1)[1] if " " in text else "optimizar una función matemática"
            start_evolution(chat_id, task)
            send_telegram(chat_id, f"🧬 Evolución iniciada: {task}\n3 generaciones x 3 individuos. Te aviso al terminar (~1-2 min).")
            return "ok", 200

        if "fusion" in low or "clonar" in low:
            k = f"?key={ADMIN_KEY}" if ADMIN_KEY else ""
            send_telegram(chat_id, f"FUSION CEREBROS:\n{SERVICE_URL}/fusion{k}")
            return "ok", 200

        if "freebuff" in low:
            mod = SKILLS.get("freebuff_agent_skill")
            if mod and hasattr(mod, "FreebuffAgent"):
                agente = mod.FreebuffAgent()
                send_telegram(chat_id, agente.run_agent(text) + f"\nModelo: {agente.choose_model()}")
            else:
                send_telegram(chat_id, "Skill freebuff no cargado en este deploy.")
            return "ok", 200

        if "skills" in low:
            send_telegram(chat_id, "Skills cargados: " + (", ".join(SKILLS.keys()) or "ninguno"))
            return "ok", 200

        if "memoria" in low:
            mem = load_memory(chat_id)
            if not mem:
                send_telegram(chat_id, "Memoria vacía o Supabase sin conectar.")
            else:
                resumen = "\n".join(f"• {m.get('role')}: {(m.get('content') or '')[:80]}" for m in mem[-6:])
                send_telegram(chat_id, f"Últimos recuerdos:\n{resumen}")
            return "ok", 200

        if low.startswith("ejecuta") or low.startswith("corre") or low.startswith("/ejecutar"):
            code = LAST_CODE.get(chat_id)
            if not code:
                send_telegram(chat_id, "No hay tool reciente. Primero pedime: crea una tool que...")
                return "ok", 200
            salida = run_sandbox(code)
            send_telegram(chat_id, f"▶️ Resultado:\n{salida}")
            save_memory(chat_id, "assistant", f"[ejecución] {salida[:500]}")
            return "ok", 200

        if "tool" in low or "crea" in low or "codigo" in low:
            history = load_memory(chat_id)
            code = ask_groq(text, history)
            code = clean_code(code)
            LAST_CODE[chat_id] = code
            tool_name = f"tool_{int(time.time())}"
            github_push(f"tools/{tool_name}.py", code, f"GOD {tool_name}")
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/tools/{tool_name}.py"
            save_memory(chat_id, "user", text)
            save_memory(chat_id, "assistant", f"[tool creada] {tool_name}")
            send_telegram(chat_id, f"{tool_name}.py\n{link}\n\n{code[:3000]}\n\n▶️ Escribí 'ejecutar' para probarla.")
            return "ok", 200

        history = load_memory(chat_id)
        reply = ask_groq(text, history)
        if AFILIADO_LINK and any(w in low for w in ["plata", "ganar", "vender", "marketing", "afiliado"]):
            reply += f"\n\n💸 Resource: {AFILIADO_LINK}"
        reply = reply[:3500].replace("```python", "").replace("```", "")
        save_memory(chat_id, "user", text)
        save_memory(chat_id, "assistant", reply)
        send_telegram(chat_id, reply)
    except Exception as e:
        print("[telegram] error:", e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
