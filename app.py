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

# ---------- Skills, contexto y BIBLIOTECA de código propio ----------
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

def scan_library():
    lib = {}
    for pattern in ["tools/*.py", "evolution/*.py", "agents/*.py"]:
        for path in glob.glob(pattern):
            name = os.path.basename(path)[:-3]
            try:
                lib[name] = open(path, "r", errors="ignore").read()
            except Exception:
                pass
    return lib

SKILLS = load_skills()
BRAIN_CONTEXT = build_brain_context()
CODE_LIBRARY = scan_library()
LAST_CODE = {}
print(f"[evo] skills: {len(SKILLS)} | biblioteca: {len(CODE_LIBRARY)} programas | context: {len(BRAIN_CONTEXT)} chars")

# ---------- Supabase: memoria + conocimiento global ----------
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

def load_knowledge(limit=6):
    if not SUPABASE_URL or not SUPABASE_KEY: return ""
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/global_knowledge", headers=sb_headers(),
                         params={"order": "created_at.desc", "limit": str(limit)}, timeout=10)
        if r.status_code == 200:
            return "\n".join(f"- {k.get('content')}" for k in r.json())
    except Exception as e:
        print("[kb] load error:", e)
    return ""

GLOBAL_KB = load_knowledge()

def save_knowledge(topic, result):
    global GLOBAL_KB
    if not SUPABASE_URL or not SUPABASE_KEY: return
    try:
        insight = ask_groq(f"En UNA sola línea: ¿qué se aprendió de esto? Objetivo: {topic} | Resultado: {result[:300]}")
        insight = (insight or "").replace("\n", " ")[:500]
        requests.post(f"{SUPABASE_URL}/rest/v1/global_knowledge", headers=sb_headers(),
                      json={"topic": topic[:200], "content": insight}, timeout=10)
        GLOBAL_KB = (GLOBAL_KB + f"\n- {insight}")[-3000:]
    except Exception as e:
        print("[kb] save error:", e)

# ---------- Sandbox y fitness ----------
def run_sandbox(code):
    try:
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=10)
        out = (p.stdout or p.stderr)[:3000]
        return out or "(corrió sin imprimir nada)"
    except subprocess.TimeoutExpired:
        return "Timeout: tardó más de 10 segundos"
    except Exception as e:
        return f"Error de ejecución: {e}"

def clean_code(raw):
    code = raw
    if "```" in code:
        for p in code.split("```"):
            if "import" in p or "def " in p:
                code = p.replace("python", "").strip()
                break
    return code

# ---------- Groq ----------
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
    if GLOBAL_KB:
        system += f"\nCosas que YA aprendiste en evoluciones anteriores (usalas):\n{GLOBAL_KB}"
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

# ---------- Motor evolutivo con auto-evaluación ----------
def evolve_program(task, generations=3, pop=3):
    expected = (ask_groq(f"Para esta task: {task} — respondé ÚNICAMENTE el output exacto que imprimiría un programa correcto, sin explicaciones.") or "").strip()
    def fitness(out):
        if out.startswith(("Error", "Timeout")) or "Traceback" in out:
            return 0.0
        s = 1.0
        if expected and expected[:60] in out:
            s += 2.0
        return s
    population = [clean_code(ask_groq(f"Escribí un programa Python distinto y creativo que: {task}. Solo código.")) for _ in range(pop)]
    best_code, best_score, best_out = None, -1.0, ""
    for gen in range(generations):
        scored = []
        for code in population:
            out = run_sandbox(code)
            scored.append((fitness(out), code, out))
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_code, best_out = scored[0]
        print(f"[evolve] gen {gen+1} score: {best_score:.2f}")
        new_pop = [best_code]
        for sc, code, out in scored[:2]:
            mut = ask_groq(f"Task: {task}\nCódigo:\n{code[:2000]}\nSalida:\n{out[:500]}\nOutput esperado: {expected[:200]}\nMutá/mejorá el código para que cumpla la task. Devolvé SOLO código Python.")
            new_pop.append(clean_code(mut))
        population = new_pop
    ok = bool(expected and expected[:60] in best_out)
    return best_code, best_score, ok

def start_evolution(chat_id, task):
    def worker():
        try:
            code, score, ok = evolve_program(task)
            name = f"evolved_{int(time.time())}.py"
            github_push(f"evolution/{name}", code, f"evolve: {task[:40]}")
            CODE_LIBRARY[name[:-3]] = code
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/evolution/{name}"
            save_memory(chat_id, "assistant", f"[evolución] {task[:100]} score {score:.2f}")
            if ok or score >= 2.0:
                save_knowledge(task, code[:200])
            send_telegram(chat_id, f"🧬 EVOLUCIÓN COMPLETA\nScore: {score:.2f} | output correcto: {'SÍ ✅' if ok else 'NO ❌'}\n{link}\n\nMejor individuo:\n{code[:2200]}\n\nUsalo con: usar {name[:-3]}")
        except Exception as e:
            send_telegram(chat_id, f"Error en evolución: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Agentes multi-paso ----------
def start_agent(chat_id, goal):
    def worker():
        try:
            plan_raw = ask_groq(f"Dividí este objetivo en 3 pasos secuenciales cortos. Respondé solo 3 líneas, una por paso, sin numerar:\n{goal}")
            steps = [l.strip(" -•123.") for l in plan_raw.splitlines() if l.strip()][:3] or [goal]
            prev_out, report, parts = "", [], ["# Agente multi-paso generado por EVO V9", f"# Objetivo: {goal}", ""]
            for i, step in enumerate(steps, 1):
                code = clean_code(ask_groq(
                    f"Paso {i} de un agente: {step}\nOutput del paso anterior:\n{prev_out[:800]}\nEscribí SOLO código Python que ejecute este paso y printee el resultado."))
                out = run_sandbox(code)
                prev_out = out
                report.append(f"🔹 Paso {i}: {step}\n→ {out[:400]}")
                parts += [f"# --- Paso {i}: {step} ---", code, ""]
            name = f"agent_{int(time.time())}.py"
            full = "\n".join(parts)
            github_push(f"agents/{name}", full, f"agent: {goal[:40]}")
            CODE_LIBRARY[name[:-3]] = full
            save_knowledge(goal, prev_out)
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/agents/{name}"
            send_telegram(chat_id, "🤖 AGENTE COMPLETADO\n\n" + "\n\n".join(report) + f"\n\nCódigo completo: {link}\nUsalo con: usar {name[:-3]}")
        except Exception as e:
            send_telegram(chat_id, f"Error agente: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Seguridad y helpers ----------
def admin_only():
    if not ADMIN_KEY or request.args.get("key") != ADMIN_KEY:
        abort(404)

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

def set_commands():
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands", json={"commands": [
            {"command": "start", "description": "Iniciar EVO V9"},
            {"command": "tool", "description": "Crear una tool nueva"},
            {"command": "evolucionar", "description": "Evolucionar un programa con auto-evaluación"},
            {"command": "agente", "description": "Crear y ejecutar un agente multi-paso"},
            {"command": "biblioteca", "description": "Ver todo el código que aprendí"},
            {"command": "ejecutar", "description": "Ejecutar la última tool creada"},
            {"command": "memoria", "description": "Ver últimos recuerdos"},
            {"command": "sabiduria", "description": "Ver lo aprendido globalmente"},
        ]}, timeout=10)
    except Exception as e:
        print("[tg] commands:", e)

set_commands()

# ---------- Rutas ----------
@app.route("/")
def home():
    return f"EVO V9 NIVEL 4 - skills: {len(SKILLS)} - biblioteca: {len(CODE_LIBRARY)} - sabiduria: {len(GLOBAL_KB)} chars - memoria: {'ON' if SUPABASE_KEY else 'OFF'}", 200

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
            send_telegram(chat_id, "🧠 EVO V9 NIVEL 4 activo.\n/evolucionar <task> | /agente <objetivo> | /biblioteca | /ejecutar | /memoria | /sabiduria")
            return "ok", 200

        if low.startswith("evoluciona") or low.startswith("/evolucionar") or low.startswith("evolve"):
            task = text.split(" ", 1)[1] if " " in text else "optimizar una función matemática"
            start_evolution(chat_id, task)
            send_telegram(chat_id, f"🧬 Evolución iniciada: {task}\n3 gen x 3 individuos + auto-evaluación. Te aviso en ~1-2 min.")
            return "ok", 200

        if low.startswith("agente ") or low.startswith("/agente"):
            goal = text.split(" ", 1)[1] if " " in text else ""
            if not goal:
                send_telegram(chat_id, "Uso: agente <objetivo>. Ej: agente que calcule el promedio de una lista y diga si es alto o bajo")
                return "ok", 200
            start_agent(chat_id, goal)
            send_telegram(chat_id, f"🤖 Agente iniciado: {goal}\n3 pasos encadenados. Te mando el reporte al terminar.")
            return "ok", 200

        if "biblioteca" in low or low == "/tools":
            names = sorted(CODE_LIBRARY.keys())
            send_telegram(chat_id, f"📚 Biblioteca ({len(names)} programas):\n" + ", ".join(names[:40]) + "\n\nUsá: usar <nombre>")
            return "ok", 200

        if low.startswith("usar "):
            name = text.split(" ", 1)[1].strip()
            code = CODE_LIBRARY.get(name)
            if not code:
                send_telegram(chat_id, f"No tengo '{name}'. Pedí /biblioteca para ver la lista.")
                return "ok", 200
            out = run_sandbox(code)
            send_telegram(chat_id, f"▶️ {name}:\n{out[:3000]}")
            return "ok", 200

        if "sabiduria" in low or "sabiduría" in low:
            send_telegram(chat_id, "🧠 Lo que aprendí globalmente:\n" + (GLOBAL_KB or "(todavía nada)"))
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
            code = clean_code(ask_groq(text, history))
            LAST_CODE[chat_id] = code
            tool_name = f"tool_{int(time.time())}"
            github_push(f"tools/{tool_name}.py", code, f"GOD {tool_name}")
            CODE_LIBRARY[tool_name] = code
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/tools/{tool_name}.py"
            save_memory(chat_id, "user", text)
            save_memory(chat_id, "assistant", f"[tool creada] {tool_name}")
            send_telegram(chat_id, f"{tool_name}.py\n{link}\n\n{code[:2800]}\n\n▶️ 'ejecutar' para probarla | 'usar {tool_name}' siempre.")
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
