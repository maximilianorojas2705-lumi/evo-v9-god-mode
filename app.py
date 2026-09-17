import os, base64, time, glob, importlib.util, subprocess, sys, threading, secrets, requests
from flask import Flask, request, abort, jsonify

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

OWNER_CHAT = [None]

# ---------- Skills, contexto y biblioteca ----------
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
API_USAGE = {}
print(f"[evo] skills: {len(SKILLS)} | biblioteca: {len(CODE_LIBRARY)} | context: {len(BRAIN_CONTEXT)} chars")

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
    if not result or "fallaron" in result or result.startswith(("Error", "Timeout", "Traceback", "def tool")):
        return
    try:
        insight = ask_groq(
            f"Resumí en UNA sola línea de texto plano, sin código, sin backticks y sin markdown, "
            f"qué se aprendió de esto. Objetivo: {topic} | Resultado: {result[:300]}")
        insight = (insight or "").replace("```python", "").replace("```", "").replace("`", "")
        insight = " ".join(insight.split())[:500]
        if len(insight) < 15 or "fallaron" in insight or insight.startswith(("def ", "import ", "Error", "Timeout")):
            return
        requests.post(f"{SUPABASE_URL}/rest/v1/global_knowledge", headers=sb_headers(),
                      json={"topic": topic[:200], "content": insight}, timeout=10)
        GLOBAL_KB = (GLOBAL_KB + f"\n- {insight}")[-3000:]
    except Exception as e:
        print("[kb] save error:", e)

def save_reflection(topic, error):
    global GLOBAL_KB
    if not SUPABASE_URL or not SUPABASE_KEY: return
    line = f"Reflexión: en '{topic[:80]}' falló por {str(error)[:120]}; la próxima verificar eso primero."
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/global_knowledge", headers=sb_headers(),
                      json={"topic": f"reflexion: {topic[:150]}", "content": line[:500]}, timeout=10)
        GLOBAL_KB = (GLOBAL_KB + f"\n- {line}")[-3000:]
    except Exception:
        pass

# ---------- Claves y datos de apps ----------
def app_key_valid(key):
    if not SUPABASE_URL or not SUPABASE_KEY: return False
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/app_keys", headers=sb_headers(),
                         params={"api_key": f"eq.{key}", "select": "id"}, timeout=8)
        return r.status_code == 200 and len(r.json()) > 0
    except Exception:
        return False

def issue_app_key(app_name):
    key = secrets.token_hex(16)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/app_keys", headers=sb_headers(),
                      json={"app": app_name, "api_key": key}, timeout=8)
    except Exception as e:
        print("[apps] key error:", e)
    return key

# ---------- Sandbox, limpieza y auto-reparación (Reflexion) ----------
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
    if not raw:
        return ""
    code = raw.strip()
    if code.startswith("```"):
        lines = code.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        while lines and lines[-1].strip() in ("```", ""):
            if lines[-1].strip() == "```":
                lines = lines[:-1]
                break
            lines = lines[:-1]
        code = "\n".join(lines)
    code = code.replace("```python", "").replace("```py", "").replace("```", "")
    return code.strip()

def run_and_fix(code, task, attempts=2):
    out = run_sandbox(code)
    for _ in range(attempts):
        if out.startswith(("Error", "Timeout")) or "Traceback" in out or "SyntaxError" in out:
            fixed = clean_code(ask_groq(
                f"Este código Python falla. Task: {task}\nCódigo:\n{code[:2500]}\nError:\n{out[:800]}\nDevolvé SOLO el código corregido, plano, sin markdown."))
            if not fixed or fixed == code:
                break
            code = fixed
            out = run_sandbox(code)
        else:
            break
    return code, out

# ---------- GitHub ----------
def gh_headers():
    return {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}

def github_push(path, code, msg):
    return github_push_to(GITHUB_REPO, path, code, msg)

def github_push_to(repo, path, content, msg):
    try:
        b64 = base64.b64encode(content.encode()).decode()
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/{path}"
        r_get = requests.get(url, headers=gh_headers(), timeout=15)
        data = {"message": msg, "content": b64}
        if r_get.status_code == 200:
            data["sha"] = r_get.json().get("sha")
        r = requests.put(url, headers=gh_headers(), json=data, timeout=20)
        return r.status_code in (200, 201)
    except Exception:
        return False

def github_create_repo(name):
    try:
        r = requests.post("https://api.github.com/user/repos", headers=gh_headers(),
                          json={"name": name, "public": True, "auto_init": False}, timeout=20)
        return r.status_code in (201, 422)
    except Exception:
        return False

def github_fork(full_repo):
    try:
        r = requests.post(f"https://api.github.com/repos/{full_repo}/forks", headers=gh_headers(), timeout=40)
        return r.status_code in (200, 201, 202)
    except Exception:
        return False

def enable_pages(repo):
    try:
        r = requests.post(f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/pages",
                          headers=gh_headers(),
                          json={"build_type": "legacy", "source": {"branch": "main", "path": "/"}}, timeout=20)
        return r.status_code in (200, 201, 409)
    except Exception:
        return False

# ---------- Groq ----------
def ask_groq(prompt, history=None):
    if not GROQ_API_KEY:
        return "Falta GROQ_API_KEY"
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    system = ("Sos EVO V9 GOD MODE, un asistente experto con conocimiento de muchos frameworks de agentes. "
              "Si el usuario pide código o una tool, respondé ÚNICAMENTE código Python sin explicaciones. "
              "NO uses markdown, NO envuelvas el código en backticks. Solo código plano. "
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

# ---------- Evolución ----------
def evolve_program(task, generations=3, pop=3):
    expected = (ask_groq(f"Para esta task: {task} — respondé ÚNICAMENTE el output exacto que imprimiría un programa correcto, sin explicaciones ni código.") or "").strip()
    def fitness(out):
        if out.startswith(("Error", "Timeout")) or "Traceback" in out:
            return 0.0
        s = 1.0
        if expected and expected[:60] in out:
            s += 2.0
        return s
    population = [clean_code(ask_groq(f"Escribí un programa Python distinto y creativo que: {task}. Solo código plano, sin markdown.")) for _ in range(pop)]
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
            mut = ask_groq(f"Task: {task}\nCódigo:\n{code[:2000]}\nSalida:\n{out[:500]}\nOutput esperado: {expected[:200]}\nMutá/mejorá el código para que cumpla la task. Devolvé SOLO código Python plano, sin markdown.")
            new_pop.append(clean_code(mut))
        population = new_pop
    ok = bool(expected and expected[:60] in best_out)
    return best_code, best_score, ok

def start_evolution(chat_id, task):
    def worker():
        try:
            code, score, ok = evolve_program(task)
            code, out = run_and_fix(code, task)
            name = f"evolved_{int(time.time())}.py"
            github_push(f"evolution/{name}", code, f"evolve: {task[:40]} [skip render]")
            CODE_LIBRARY[name[:-3]] = code
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/evolution/{name}"
            save_memory(chat_id, "assistant", f"[evolución] {task[:100]} score {score:.2f}")
            if ok or score >= 2.0:
                save_knowledge(task, code[:200])
            send_telegram(chat_id, f"🧬 EVOLUCIÓN COMPLETA\nScore: {score:.2f} | output correcto: {'SÍ ✅' if ok else 'NO ❌'}\n▶️ Test: {out[:200]}\n{link}\n\nMejor individuo:\n{code[:2000]}\n\nUsalo con: usar {name[:-3]}")
        except Exception as e:
            save_reflection(f"evolución {task[:60]}", e)
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
                    f"Paso {i} de un agente: {step}\nOutput del paso anterior:\n{prev_out[:800]}\nEscribí SOLO código Python plano (sin markdown) que ejecute este paso y printee el resultado."))
                code, out = run_and_fix(code, step, attempts=1)
                prev_out = out
                report.append(f"🔹 Paso {i}: {step}\n→ {out[:400]}")
                parts += [f"# --- Paso {i}: {step} ---", code, ""]
            name = f"agent_{int(time.time())}.py"
            full = "\n".join(parts)
            github_push(f"agents/{name}", full, f"agent: {goal[:40]} [skip render]")
            CODE_LIBRARY[name[:-3]] = full
            save_knowledge(goal, prev_out)
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/agents/{name}"
            send_telegram(chat_id, "🤖 AGENTE COMPLETADO\n\n" + "\n\n".join(report) + f"\n\nCódigo: {link}\nUsalo con: usar {name[:-3]}")
        except Exception as e:
            save_reflection(f"agente {goal[:60]}", e)
            send_telegram(chat_id, f"Error agente: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- MODO PC: app rápida ----------
def start_app_build(chat_id, desc):
    def worker():
        try:
            name = f"app-{int(time.time())}"
            github_create_repo(name)
            appkey = issue_app_key(name)
            html = clean_code(ask_groq(f"Generá UN index.html completo y moderno para: {desc}. Debe linkear style.css y script.js. Solo el HTML, sin markdown."))
            css = clean_code(ask_groq(f"Generá UN style.css completo, moderno y oscuro para: {desc}. Solo CSS, sin markdown."))
            js = clean_code(ask_groq(
                f"Generá UN script.js para: {desc}. JavaScript plano, sin markdown.\n"
                f"Para guardar/leer datos usá fetch a {SERVICE_URL}/api/data con key '{appkey}' y app '{name}'.\n"
                f"Para usar IA usá fetch POST a {SERVICE_URL}/api/groq con JSON {{key:'{appkey}', prompt: texto}} y leé .reply.\n"))
            github_push_to(name, "index.html", html, f"app: {desc[:40]}")
            github_push_to(name, "style.css", css, "style")
            github_push_to(name, "script.js", js, "script")
            enable_pages(name)
            url = f"https://{GITHUB_USERNAME}.github.io/{name}/"
            save_knowledge(f"web app creada: {desc}", url)
            send_telegram(chat_id, f"🌐 APP CONSTRUIDA Y PUBLICADA\nRepo: https://github.com/{GITHUB_USERNAME}/{name}\n🔴 EN VIVO (1-2 min): {url}")
        except Exception as e:
            save_reflection(f"app {desc[:60]}", e)
            send_telegram(chat_id, f"Error creando app: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- MODO PC: proyecto completo (MetaGPT: PM+Arq+Ing+QA) ----------
def start_project(chat_id, desc):
    def worker():
        try:
            spec = ask_groq(f"Como Product Manager: escribí 5 bullets de especificación para esta app web: {desc}. Solo bullets, sin markdown.")
            plan = ask_groq(f"Como Arquitecto: listá uno por línea los archivos de una web app estática para: {desc}. Incluí siempre index.html, style.css, script.js. Máximo 5 líneas, solo nombres.")
            names = [l.strip() for l in (plan or "").splitlines() if "." in l.strip()][:5]
            if not names or "index.html" not in names:
                names = ["index.html", "style.css", "script.js"]
            repo = f"app-{int(time.time())}"
            github_create_repo(repo)
            appkey = issue_app_key(repo)
            ctx = (f"Spec PM:\n{spec[:800]}\nApp: {desc}\n"
                   f"Datos/IA: fetch a {SERVICE_URL}/api/data y /api/groq con key '{appkey}' y app '{repo}'.")
            for fname in names:
                content = clean_code(ask_groq(f"Como Ingeniero: generá el contenido COMPLETO y funcional del archivo {fname}. {ctx} Solo el contenido, sin markdown."))
                github_push_to(repo, fname, content, f"proyecto: {fname}")
            if "script.js" in names:
                r = requests.get(f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/script.js", headers=gh_headers(), timeout=15)
                if r.status_code == 200:
                    js = base64.b64decode(r.json()["content"]).decode(errors="ignore")
                    fixed = clean_code(ask_groq(f"Como QA: corregí bugs de sintaxis, de fetch y de eventos en este script.js ({desc}). Devolvé SOLO el JS corregido:\n{js[:6000]}"))
                    if fixed:
                        github_push_to(repo, "script.js", fixed, "qa: fix script")
            enable_pages(repo)
            url = f"https://{GITHUB_USERNAME}.github.io/{repo}/"
            save_knowledge(f"proyecto web: {desc}", url)
            send_telegram(chat_id, f"🏗️ PROYECTO PM+ARQ+ING+QA LISTO\nSpec:\n{spec[:500]}\n\nArchivos: {', '.join(names)}\nRepo: https://github.com/{GITHUB_USERNAME}/{repo}\n🔴 EN VIVO: {url}")
        except Exception as e:
            save_reflection(f"proyecto {desc[:60]}", e)
            send_telegram(chat_id, f"Error proyecto: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- MODO PC: clonar y mejorar ----------
def start_clone(chat_id, full_repo):
    def worker():
        try:
            github_fork(full_repo)
            short = full_repo.split("/")[-1]
            send_telegram(chat_id, f"🐒 CLONADO: https://github.com/{GITHUB_USERNAME}/{short}\nAhora: mejorar {short} <ruta/archivo>")
        except Exception as e:
            send_telegram(chat_id, f"Error clonando: {e}")
    threading.Thread(target=worker, daemon=True).start()

def start_improve(chat_id, repo, path):
    def worker():
        try:
            r = requests.get(f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/{path}", headers=gh_headers(), timeout=20)
            if r.status_code != 200:
                send_telegram(chat_id, f"No encontré {path} en {repo}")
                return
            original = base64.b64decode(r.json()["content"]).decode(errors="ignore")
            improved = clean_code(ask_groq(f"Mejorá este código sin romper su función: más eficiente, con docstrings y manejo de errores. Devolvé SOLO el código mejorado:\n{original[:6000]}"))
            msg = f"improve {path}" + (" [skip render]" if repo == GITHUB_REPO else "")
            ok = github_push_to(repo, path, improved, msg)
            send_telegram(chat_id, f"🔧 MEJORADO: {repo}/{path}\n{'Commit OK ✅' if ok else 'Falló el commit ❌'}\n\nAntes:\n{original[:300]}\n\nAhora:\n{improved[:600]}")
        except Exception as e:
            save_reflection(f"mejora {repo}/{path}", e)
            send_telegram(chat_id, f"Error mejorando: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- AUTONOMÍA (AutoGPT-lite): turno con meta auto-elegida ----------
CRON_TASKS = [
    "un programa que detecte si un texto es palíndromo",
    "una función que convierta Celsius a Fahrenheit y muestre una tabla",
    "un programa que calcule Fibonacci de forma eficiente",
    "un script que genere contraseñas seguras aleatorias",
]
LAST_CRON = [0.0]

def autonomous_shift():
    chat_id = OWNER_CHAT[0]
    try:
        state = f"Biblioteca propia: {', '.join(sorted(CODE_LIBRARY.keys())[:12])}\nSabiduría reciente: {GLOBAL_KB[-600:]}"
        decision = (ask_groq(
            "Sos un agente autónomo en tu turno de trabajo. Estado actual:\n" + state +
            "\nElegí UNA acción que más aumente tu capacidad y respondé EXACTAMENTE con uno de estos formatos:\n"
            "EVOLUCIONAR: <task de Python concreta y testeable>\n"
            "APP: <descripción breve de una app web útil>\n"
            "MEJORAR: <repo tuyo> <ruta de archivo>") or "").strip()
        up = decision.upper()
        if up.startswith("APP:") and chat_id:
            desc = decision.split(":", 1)[1].strip()
            send_telegram(chat_id, f"🌙 Turno autónomo: decidí construir la app '{desc}'")
            start_project(chat_id, desc)
            return
        if up.startswith("MEJORAR:") and chat_id:
            parts = decision.split(":", 1)[1].strip().split(" ", 1)
            if len(parts) == 2:
                send_telegram(chat_id, f"🌙 Turno autónomo: voy a mejorar {parts[1]} en {parts[0]}")
                start_improve(chat_id, parts[0].strip(), parts[1].strip())
                return
        task = decision.split(":", 1)[1].strip() if ":" in decision else CRON_TASKS[int(time.time()) % len(CRON_TASKS)]
        code, score, ok = evolve_program(task)
        code, out = run_and_fix(code, task)
        name = f"evolved_{int(time.time())}.py"
        github_push(f"evolution/{name}", code, f"[auto] evolve: {task[:40]} [skip render]")
        CODE_LIBRARY[name[:-3]] = code
        if ok or score >= 2.0:
            save_knowledge(f"[auto] {task}", code[:200])
        if chat_id:
            send_telegram(chat_id, f"🌙 Turno autónomo: evolucioné '{task}'\nScore: {score:.2f} | ▶️ test: {out[:150]}\nUsalo: usar {name[:-3]}")
    except Exception as e:
        print("[auto] error:", e)
        save_reflection("turno autónomo", e)

# ---------- Seguridad y helpers ----------
def admin_only():
    if not ADMIN_KEY or request.args.get("key") != ADMIN_KEY:
        abort(404)

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
            {"command": "tool", "description": "Crear una tool (con auto-debug)"},
            {"command": "evolucionar", "description": "Evolucionar un programa"},
            {"command": "agente", "description": "Agente multi-paso"},
            {"command": "app", "description": "App web rápida"},
            {"command": "proyecto", "description": "Proyecto completo PM+Arq+Ing+QA"},
            {"command": "clonar", "description": "Clonar un repo/IA"},
            {"command": "mejorar", "description": "Mejorar archivo clonado"},
            {"command": "biblioteca", "description": "Código aprendido"},
            {"command": "sabiduria", "description": "Aprendizaje global"},
        ]}, timeout=10)
    except Exception as e:
        print("[tg] commands:", e)

set_commands()

# ---------- Rutas ----------
@app.route("/")
def home():
    return f"EVO V9 V6 AUTONOMO - skills: {len(SKILLS)} - biblioteca: {len(CODE_LIBRARY)} - sabiduria: {len(GLOBAL_KB)} chars - memoria: {'ON' if SUPABASE_KEY else 'OFF'}", 200

@app.route("/cron")
def cron():
    admin_only()
    if time.time() - LAST_CRON[0] < 6 * 3600:
        return "cron: ya trabajé hace menos de 6h", 200
    LAST_CRON[0] = time.time()
    threading.Thread(target=autonomous_shift, daemon=True).start()
    return "cron: turno autónomo lanzado", 200

@app.route("/api/groq", methods=["POST"])
def api_groq():
    try:
        d = request.get_json(force=True) or {}
        key = (d.get("key") or "").strip()
        prompt = (d.get("prompt") or "")[:4000]
        if not key or not app_key_valid(key):
            return jsonify({"error": "invalid key"}), 403
        now = time.time()
        use = [t for t in API_USAGE.get(key, []) if now - t < 3600]
        if len(use) >= 30:
            return jsonify({"error": "rate limit"}), 429
        use.append(now)
        API_USAGE[key] = use
        return jsonify({"reply": ask_groq(prompt)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/data", methods=["GET", "POST"])
def api_data():
    try:
        if request.method == "POST":
            d = request.get_json(force=True) or {}
            key = (d.get("key") or "").strip()
            appname = (d.get("app") or "").strip()
            if not key or not app_key_valid(key):
                return jsonify({"error": "invalid key"}), 403
            requests.post(f"{SUPABASE_URL}/rest/v1/app_data", headers=sb_headers(),
                          json={"app": appname, "data": d.get("data")}, timeout=8)
            return jsonify({"ok": True})
        key = (request.args.get("key") or "").strip()
        appname = (request.args.get("app") or "").strip()
        if not key or not app_key_valid(key):
            return jsonify({"error": "invalid key"}), 403
        r = requests.get(f"{SUPABASE_URL}/rest/v1/app_data", headers=sb_headers(),
                         params={"app": f"eq.{appname}", "order": "created_at.desc", "limit": "50"}, timeout=8)
        return jsonify(r.json() if r.status_code == 200 else [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/fusion")
def fusion():
    admin_only()
    logs = []
    headers = gh_headers()
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
                        if github_push(f"tools_evolution/{name}_{f['name']}", content, f"fusion {name} [skip render]"):
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
        OWNER_CHAT[0] = chat_id
        low = text.lower()

        if low.startswith("/start") or low == "hola":
            send_telegram(chat_id, "🧠 EVO V9 V6 AUTÓNOMO activo.\n/proyecto <desc> | /app <desc> | /clonar user/repo | /mejorar repo ruta | /evolucionar | /agente | /biblioteca | /sabiduria")
            return "ok", 200

        if low.startswith("proyecto ") or low == "/proyecto":
            desc = text.split(" ", 1)[1] if " " in text else ""
            if not desc:
                send_telegram(chat_id, "Uso: proyecto <descripción>. Ej: proyecto una calculadora con historial guardado")
                return "ok", 200
            start_project(chat_id, desc)
            send_telegram(chat_id, f"🏗️ Proyecto iniciado: {desc}\nPM → Arquitecto → Ingeniero → QA. ~2-4 min.")
            return "ok", 200

        if low.startswith("app ") or low == "/app":
            desc = text.split(" ", 1)[1] if " " in text else ""
            if not desc:
                send_telegram(chat_id, "Uso: app <descripción>")
                return "ok", 200
            start_app_build(chat_id, desc)
            send_telegram(chat_id, f"🌐 Construyendo app: {desc} (~1-2 min)")
            return "ok", 200

        if low.startswith("clonar "):
            full = text.split(" ", 1)[1].strip()
            if "/" not in full:
                send_telegram(chat_id, "Uso: clonar usuario/repo")
                return "ok", 200
            start_clone(chat_id, full)
            send_telegram(chat_id, f"🐒 Clonando {full}...")
            return "ok", 200

        if low.startswith("mejorar "):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                send_telegram(chat_id, "Uso: mejorar <repo> <ruta/archivo.py>")
                return "ok", 200
            start_improve(chat_id, parts[1].strip(), parts[2].strip())
            send_telegram(chat_id, f"🔧 Mejorando {parts[2]} en {parts[1]}...")
            return "ok", 200

        if low.startswith("ver "):
            name = text.split(" ", 1)[1].strip()
            code = CODE_LIBRARY.get(name)
            send_telegram(chat_id, f"📄 {name}:\n{code[:3500]}" if code else f"No tengo '{name}'.")
            return "ok", 200

        if low.startswith("evoluciona") or low.startswith("/evolucionar") or low.startswith("evolve"):
            task = text.split(" ", 1)[1] if " " in text else "optimizar una función matemática"
            start_evolution(chat_id, task)
            send_telegram(chat_id, f"🧬 Evolución iniciada: {task}\nTe aviso en ~1-2 min.")
            return "ok", 200

        if low.startswith("agente ") or low.startswith("/agente"):
            goal = text.split(" ", 1)[1] if " " in text else ""
            if not goal:
                send_telegram(chat_id, "Uso: agente <objetivo>")
                return "ok", 200
            start_agent(chat_id, goal)
            send_telegram(chat_id, f"🤖 Agente iniciado: {goal}")
            return "ok", 200

        if "biblioteca" in low or low == "/tools":
            names = sorted(CODE_LIBRARY.keys())
            send_telegram(chat_id, f"📚 Biblioteca ({len(names)} programas):\n" + ", ".join(names[:40]) + "\n\nUsá: usar <nombre> | ver <nombre>")
            return "ok", 200

        if low.startswith("usar "):
            name = text.split(" ", 1)[1].strip()
            code = CODE_LIBRARY.get(name)
            if not code:
                send_telegram(chat_id, f"No tengo '{name}'.")
                return "ok", 200
            out = run_sandbox(code)
            send_telegram(chat_id, f"▶️ {name}:\n{out[:3000]}")
            return "ok", 200

        if "sabiduria" in low or "sabiduría" in low:
            send_telegram(chat_id, "🧠 Lo que aprendí globalmente:\n" + (GLOBAL_KB or "(todavía nada)"))
            return "ok", 200

        if "fusion" in low:
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
                send_telegram(chat_id, "No hay tool reciente. Primero: crea una tool que...")
                return "ok", 200
            salida = run_sandbox(code)
            send_telegram(chat_id, f"▶️ Resultado:\n{salida}")
            return "ok", 200

        if "tool" in low or "crea" in low or "codigo" in low:
            history = load_memory(chat_id)
            code = clean_code(ask_groq(text, history))
            code, out = run_and_fix(code, text)
            LAST_CODE[chat_id] = code
            tool_name = f"tool_{int(time.time())}"
            github_push(f"tools/{tool_name}.py", code, f"GOD {tool_name} [skip render]")
            CODE_LIBRARY[tool_name] = code
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/tools/{tool_name}.py"
            save_memory(chat_id, "user", text)
            save_memory(chat_id, "assistant", f"[tool creada] {tool_name}")
            send_telegram(chat_id, f"{tool_name}.py\n{link}\n\n{code[:2500]}\n\n▶️ Probada: {out[:300]}\n'usar {tool_name}' cuando quieras.")
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
