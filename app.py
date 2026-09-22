import os, base64, time, glob, importlib.util, subprocess, sys, threading, secrets, requests
from memoria_sem import recordar as recordar_sem
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
DEFAULT_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "openai/gpt-oss-120b",
    "qwen/qwen3-32b",
    "moonshotai/kimi-k2-instruct",
]
ROLE_MODEL = {
    "arquitecto": "meta-llama/llama-4-scout-17b-16e-instruct",
    "coder": "openai/gpt-oss-120b",
    "critico": "moonshotai/kimi-k2-instruct",
    "juez": "qwen/qwen3-32b",
    "vision": "meta-llama/llama-4-scout-17b-16e-instruct",
}
HARD_MODELS = [
    "deepseek-r1-distill-llama-70b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "openai/gpt-oss-120b",
    "qwen/qwen3-32b",
]
FROZEN_CORE = [
    ("invertir una cadena sin usar [::-1]", "assert solve('hola')=='aloh'"),
    ("contar vocales de un texto", "assert solve('murcielago')==5"),
    ("fibonacci posición n", "assert solve(10)==55"),
    ("detectar palíndromo ignorando espacios", "assert solve('ana lava lana')==True"),
    ("sumar dígitos de un número", "assert solve(999)==27"),
]
CRON_TASKS = [
    "un programa que detecte si un texto es palíndromo",
    "una función que convierta Celsius a Fahrenheit y muestre una tabla",
    "un programa que calcule Fibonacci de forma eficiente",
    "un script que genere contraseñas seguras aleatorias",
]
LAST_CRON = [0.0]
ALLOWED_LICENSES = ("mit", "apache-2.0", "apache 2.0", "bsd-2-clause", "bsd-3-clause",
                    "isc", "unlicense", "modified mit", "mpl-2.0")

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

# ---------- Sandbox, limpieza, auto-reparación ----------
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

# ---------- Ojos: screenshots y visión ----------
def take_screenshot(url):
    try:
        r = requests.get(f"https://image.thum.io/get/width/1024/crop/800/noanimate/{url}", timeout=60)
        if r.status_code == 200 and r.content.startswith(b"\x89PNG"):
            return r.content
    except Exception as e:
        print("[shot] thum error:", e)
    try:
        r = requests.get("https://api.microlink.io/", params={"url": url, "screenshot": "true", "meta": "false", "embed": "screenshot.url"}, timeout=60)
        if r.status_code == 200:
            shot_url = (r.json().get("data") or {}).get("screenshot", {}).get("url")
            if shot_url:
                r2 = requests.get(shot_url, timeout=60)
                if r2.status_code == 200 and len(r2.content) > 2000:
                    return r2.content
    except Exception as e:
        print("[shot] microlink error:", e)
    return None

def send_photo(chat_id, png, caption):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                      data={"chat_id": chat_id, "caption": caption[:1000]},
                      files={"photo": ("shot.png", png, "image/png")}, timeout=25)
    except Exception as e:
        print("[tg] photo error:", e)

def ask_vision(prompt, png_b64):
    if not GROQ_API_KEY:
        return ""
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    try:
        c = client.chat.completions.create(
            model=ROLE_MODEL["vision"],
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{png_b64}"}}]}],
            max_tokens=800)
        return c.choices[0].message.content or ""
    except Exception as e:
        print("[vision] error:", str(e)[:150])
        return ""

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

def read_repo_file(repo, path):
    try:
        r = requests.get(f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/{path}", headers=gh_headers(), timeout=15)
        if r.status_code == 200:
            return base64.b64decode(r.json()["content"]).decode(errors="ignore")
    except Exception:
        pass
    return None

# ---------- Groq con roles ----------
def ask_groq(prompt, history=None, model=None):
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
    # Memoria semantica: recuerdos por significado (pgvector + Gemini embeddings)
    try:
        recuerdos_sem = recordar_sem(prompt, limite=3)
        if recuerdos_sem:
            system += "\n\nRecuerdos relevantes por significado (usa estos si son pertinentes):\n" + recuerdos_sem
    except Exception as e:
        print(f"[mem_sem] fallo al recordar: {e}")

    messages = [{"role": "system", "content": system}]
    for m in (history or []):
        role = m.get("role")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": (m.get("content") or "")[:1500]})
    messages.append({"role": "user", "content": prompt})
    models = ([model] + DEFAULT_MODELS) if model else DEFAULT_MODELS
    for mdl in models:
        try:
            c = client.chat.completions.create(model=mdl, messages=messages,
                                               max_tokens=2500, temperature=0.9)
            print(f"[groq] OK con {mdl}")
            return c.choices[0].message.content
        except Exception as e:
            print(f"[groq] FALLÓ {mdl}: {str(e)[:150]}")
            if "rate limit" in str(e).lower():
                time.sleep(5)
            continue
    return "def tool(): return 'Todos los modelos fallaron - ver logs'"

def ask_role(role, prompt):
    return ask_groq(prompt, model=ROLE_MODEL.get(role))

# ---------- Genoma y diario ----------
def genome_register(kind, name, parents="", fitness=0.0, provenance="original", task=""):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/genome", headers=sb_headers(),
                      json={"id": name, "kind": kind, "name": name, "parents": parents,
                            "fitness": fitness, "provenance": provenance, "task": task}, timeout=8)
    except Exception as e:
        print("[genome] reg error:", e)

def genome_use(name):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/genome", headers=sb_headers(),
                         params={"id": f"eq.{name}", "select": "uses"}, timeout=8)
        if r.status_code == 200 and r.json():
            uses = (r.json()[0].get("uses") or 0) + 1
            requests.patch(f"{SUPABASE_URL}/rest/v1/genome", headers=sb_headers(),
                           params={"id": f"eq.{name}"}, json={"uses": uses}, timeout=8)
    except Exception:
        pass

def genome_list():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/genome", headers=sb_headers(),
                         params={"order": "created_at.desc", "limit": "60"}, timeout=8)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def journal_write(phase, entry):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/journal", headers=sb_headers(),
                      json={"phase": phase, "entry": entry[:1500]}, timeout=8)
        github_push(f"journal/{int(time.time())}_{phase}.md", f"# {phase}\n\n{entry}", f"journal {phase} [skip render]")
    except Exception as e:
        print("[journal] error:", e)

def log_experiment(hypothesis, result, ok):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/experiments", headers=sb_headers(),
                      json={"hypothesis": (hypothesis or "")[:800], "result": (result or "")[:800], "ok": bool(ok)}, timeout=8)
    except Exception:
        pass

# ---------- Autonomía real ----------
def _tok(s):
    import re as _re
    return set(_re.findall(r"[a-záéíóúñ0-9]{3,}", (s or "").lower()))

def bump_autonomy(own):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/autonomy", headers=sb_headers(), params={"id": "eq.1"}, timeout=6)
        if r.status_code == 200 and r.json():
            row = r.json()[0]
            payload = {"total": (row.get("total") or 0) + 1}
            if own:
                payload["own"] = (row.get("own") or 0) + 1
            requests.patch(f"{SUPABASE_URL}/rest/v1/autonomy", headers=sb_headers(),
                           params={"id": "eq.1"}, json=payload, timeout=6)
    except Exception:
        pass

def own_answer(text):
    gens = [g for g in genome_list() if g.get("kind") in ("solved", "crossover", "dream", "simulated", "evolved") and g.get("task")]
    tq = _tok(text)
    best = None
    for g in gens:
        inter = len(tq & _tok(g.get("task")))
        if inter >= 3 and (best is None or inter > best[0]):
            best = (inter, g)
    if not best:
        return None
    gid = best[1].get("id")
    code = CODE_LIBRARY.get(gid) or read_repo_file(GITHUB_REPO, f"evolution/{gid}.py")
    if not code:
        return None
    return gid, run_sandbox(code)

# ---------- Sentidos ----------
def transcribe_audio(file_bytes):
    if not GROQ_API_KEY:
        return ""
    import io
    from groq import Groq
    try:
        client = Groq(api_key=GROQ_API_KEY)
        with io.BytesIO(file_bytes) as fh:
            fh.name = "voice.ogg"
            t = client.audio.transcriptions.create(file=fh, model="whisper-large-v3-turbo")
        return t.text or ""
    except Exception as e:
        print("[voice] error:", str(e)[:150])
        return ""

def sense_search(q):
    import re as _re
    try:
        r = requests.get("https://es.wikipedia.org/w/api.php",
                         params={"action": "query", "list": "search", "srsearch": q, "format": "json", "srlimit": "3"}, timeout=10)
        out = []
        for s in (r.json().get("query", {}).get("search", []) if r.status_code == 200 else []):
            snip = _re.sub("<[^>]+>", "", s.get("snippet", ""))
            out.append(f"• {s.get('title')}: {snip}")
        return "\n".join(out) or "Sin resultados."
    except Exception:
        return "Búsqueda falló."

def sense_read(url):
    import re as _re
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 EVO-V9-research"})
        txt = _re.sub(r"(?s)<(script|style).*?</\1>", " ", r.text)
        txt = _re.sub("<[^>]+>", " ", txt)
        return " ".join(txt.split())[:4000]
    except Exception:
        return ""

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
            genome_register("evolved", name[:-3], parents="evolución-genética", fitness=score, provenance="evolución auto-evaluada", task=task)
            link = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/evolution/{name}"
            save_memory(chat_id, "assistant", f"[evolución] {task[:100]} score {score:.2f}")
            if ok or score >= 2.0:
                save_knowledge(task, code[:200])
            send_telegram(chat_id, f"🧬 EVOLUCIÓN COMPLETA\nScore: {score:.2f} | output correcto: {'SÍ ✅' if ok else 'NO ❌'}\n▶️ Test: {out[:200]}\n{link}\n\nMejor individuo:\n{code[:2000]}\n\nUsalo con: usar {name[:-3]}")
        except Exception as e:
            save_reflection(f"evolución {task[:60]}", e)
            send_telegram(chat_id, f"Error en evolución: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Duelo multi-modelo ----------
def start_duel(chat_id, task):
    def worker():
        try:
            solA = clean_code(ask_role("coder", f"Escribí código Python plano, sin markdown, para: {task}"))
            solB = clean_code(ask_role("critico", f"Escribí código Python plano, sin markdown, para: {task}"))
            outA = run_sandbox(solA)
            outB = run_sandbox(solB)
            verdict = (ask_role("juez", f"Task: {task}\nSolución A:\n{solA[:1500]}\nSalida A: {outA[:300]}\nSolución B:\n{solB[:1500]}\nSalida B: {outB[:300]}\nRespondé SOLO con la letra 'A' o 'B' de la mejor solución.") or "").strip().upper()
            pick = "A" if verdict.startswith("A") else "B"
            code, out = (solA, outA) if pick == "A" else (solB, outB)
            code, out = run_and_fix(code, task)
            name = f"duel_{int(time.time())}.py"
            github_push(f"evolution/{name}", code, f"duelo: {task[:40]} [skip render]")
            CODE_LIBRARY[name[:-3]] = code
            save_knowledge(f"duelo: {task}", f"ganó {pick}")
            send_telegram(chat_id, f"⚔️ DUELO MULTI-MODELO\nCoder(gpt-oss) vs Crítico(kimi-k2) → Juez(qwen3-32b) eligió: {pick}\n▶️ Test: {out[:250]}\nUsalo: usar {name[:-3]}")
        except Exception as e:
            save_reflection(f"duelo {task[:60]}", e)
            send_telegram(chat_id, f"Error duelo: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Modo profundo ----------
def deep_think(chat_id, q):
    def worker():
        try:
            subs = (ask_role("arquitecto", f"Descomponé esta pregunta en 3 subpreguntas necesarias y suficientes, una por línea, sin numerar: {q}") or "")
            acc = []
            for s in [x.strip() for x in subs.splitlines() if x.strip()][:3]:
                r = ask_groq(f"Respondé en 2 líneas como experto: {s}\nContexto acumulado: {'; '.join(acc)[-800:]}")
                acc.append(f"{s} → {(r or '')[:300]}")
            final = ask_role("juez", f"Pregunta original: {q}\nEvidencia por subpreguntas:\n" + "\n".join(acc) + "\nDa la respuesta final en 5 bullets claros.")
            journal_write("profundo", f"{q[:100]} → {(final or '')[:200]}")
            send_telegram(chat_id, f"🧠 MODO PROFUNDO (descomposición + síntesis)\n{final[:2000]}")
        except Exception as e:
            send_telegram(chat_id, f"Error modo profundo: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Agentes con roles ----------
def start_agent(chat_id, goal):
    def worker():
        try:
            plan_raw = ask_role("arquitecto", f"Dividí este objetivo en 2-4 pasos secuenciales. Respondé una línea por paso con formato ROL|paso, donde ROL es uno de: arquitecto, coder, critico, juez. Objetivo: {goal}")
            steps, roles = [], []
            for l in (plan_raw or "").splitlines():
                l = l.strip(" -•123.")
                if "|" in l:
                    r, s = l.split("|", 1)
                    roles.append(r.strip().lower() if r.strip().lower() in ROLE_MODEL else "coder")
                    steps.append(s.strip())
                elif l:
                    roles.append("coder")
                    steps.append(l)
            if not steps:
                steps, roles = [goal], ["coder"]
            prev_out, report, parts = "", [], ["# Agente multi-paso generado por EVO V9", f"# Objetivo: {goal}", ""]
            for i, step in enumerate(steps, 1):
                role_i = roles[i - 1] if i - 1 < len(roles) else "coder"
                code = clean_code(ask_role(role_i,
                    f"Paso {i} de un agente (tu rol: {role_i}): {step}\nOutput del paso anterior:\n{prev_out[:800]}\nEscribí SOLO código Python plano (sin markdown) que ejecute este paso y printee el resultado."))
                code, out = run_and_fix(code, step, attempts=1)
                prev_out = out
                report.append(f"🔹 Paso {i} [{role_i}]: {step}\n→ {out[:400]}")
                parts += [f"# --- Paso {i} [{role_i}]: {step} ---", code, ""]
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

# ---------- Auditoría visual ----------
def visual_audit(chat_id, url, desc, rounds=2):
    report = []
    repo = url.rstrip("/").split("/")[-1]
    for r in range(rounds):
        png = take_screenshot(url)
        if not png:
            report.append(f"Ronda {r+1}: no pude capturar screenshot")
            break
        b64 = base64.b64encode(png).decode()
        critique = ask_vision(
            f"Sos QA visual de UI. Esta es una web: {desc}. Listá bugs visuales concretos (página vacía, elementos rotos, textos superpuestos, botones invisibles). Si todo se ve bien respondé exactamente: SIN BUGS. Máximo 4 líneas.", b64)
        report.append(f"Ronda {r+1}: {(critique or 'visión no disponible')[:400]}")
        if chat_id:
            send_photo(chat_id, png, f"👁️ Auditoría visual ronda {r+1} de {repo}")
        if not critique or "SIN BUGS" in critique.upper():
            break
        for fname in ["script.js", "style.css", "index.html"]:
            cur = read_repo_file(repo, fname)
            if not cur:
                continue
            fixed = clean_code(ask_role("coder",
                f"Corregí estos bugs visuales en {fname} de una web ({desc}). Crítica del QA visual:\n{critique[:600]}\nArchivo actual:\n{cur[:5000]}\nDevolvé SOLO el archivo corregido, sin markdown."))
            if fixed:
                github_push_to(repo, fname, fixed, f"vision-fix {fname}")
        time.sleep(40)
    save_knowledge(f"auditoría visual: {desc}", " | ".join(report)[:300])
    if chat_id:
        send_telegram(chat_id, "👁️ AUDITORÍA VISUAL COMPLETA\n" + "\n\n".join(report))

# ---------- App rápida ----------
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
            send_telegram(chat_id, f"🌐 APP CONSTRUIDA Y PUBLICADA\nRepo: https://github.com/{GITHUB_USERNAME}/{name}\n🔴 EN VIVO (1-2 min): {url}\nAhora me audito visualmente...")
            time.sleep(40)
            visual_audit(chat_id, url, desc, rounds=2)
        except Exception as e:
            save_reflection(f"app {desc[:60]}", e)
            send_telegram(chat_id, f"Error creando app: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Proyecto MetaGPT + visión ----------
def start_project(chat_id, desc):
    def worker():
        try:
            spec = ask_role("arquitecto", f"Como Product Manager: escribí 5 bullets de especificación para esta app web: {desc}. Solo bullets, sin markdown.")
            plan = ask_role("arquitecto", f"Como Arquitecto: listá uno por línea los archivos de una web app estática para: {desc}. Incluí siempre index.html, style.css, script.js. Máximo 5 líneas, solo nombres.")
            names = [l.strip() for l in (plan or "").splitlines() if "." in l.strip()][:5]
            if not names or "index.html" not in names:
                names = ["index.html", "style.css", "script.js"]
            repo = f"app-{int(time.time())}"
            github_create_repo(repo)
            appkey = issue_app_key(repo)
            ctx = (f"Spec PM:\n{spec[:800]}\nApp: {desc}\n"
                   f"Datos/IA: fetch a {SERVICE_URL}/api/data y /api/groq con key '{appkey}' y app '{repo}'.")
            for fname in names:
                content = clean_code(ask_role("coder", f"Como Ingeniero: generá el contenido COMPLETO y funcional del archivo {fname}. {ctx} Solo el contenido, sin markdown."))
                github_push_to(repo, fname, content, f"proyecto: {fname}")
            if "script.js" in names:
                js = read_repo_file(repo, "script.js")
                if js:
                    fixed = clean_code(ask_role("critico", f"Como QA: corregí bugs de sintaxis, de fetch y de eventos en este script.js ({desc}). Devolvé SOLO el JS corregido:\n{js[:6000]}"))
                    if fixed:
                        github_push_to(repo, "script.js", fixed, "qa: fix script")
            enable_pages(repo)
            url = f"https://{GITHUB_USERNAME}.github.io/{repo}/"
            save_knowledge(f"proyecto web: {desc}", url)
            send_telegram(chat_id, f"🏗️ PROYECTO PM+ARQ+ING+QA LISTO\nSpec:\n{spec[:500]}\n\nArchivos: {', '.join(names)}\nRepo: https://github.com/{GITHUB_USERNAME}/{repo}\n🔴 EN VIVO: {url}\n👁️ Iniciando auditoría visual...")
            time.sleep(40)
            visual_audit(chat_id, url, desc, rounds=2)
        except Exception as e:
            save_reflection(f"proyecto {desc[:60]}", e)
            send_telegram(chat_id, f"Error proyecto: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Evolución de UI con fitness visual ----------
def start_ui_evolution(chat_id, desc):
    def worker():
        try:
            repo = f"app-{int(time.time())}"
            github_create_repo(repo)
            appkey = issue_app_key(repo)
            html_base = clean_code(ask_groq(
                f"Generá UN index.html completo para: {desc}. En el href del CSS escribí exactamente CSS_PATH y en el src del script exactamente JS_PATH. Solo HTML, sin markdown."))
            js = clean_code(ask_role("coder",
                f"Generá UN script.js plano para: {desc}. Datos/IA: fetch a {SERVICE_URL}/api/data y /api/groq con key '{appkey}' y app '{repo}'. Solo JS, sin markdown."))
            for v in range(1, 4):
                css = clean_code(ask_role(["arquitecto", "coder", "critico"][v - 1],
                    f"Generá UN style.css variante {v} con estética propia, moderna y distinta a las demás, para: {desc}. Solo CSS, sin markdown."))
                html_v = html_base.replace("CSS_PATH", f"v{v}/style.css").replace("JS_PATH", f"v{v}/script.js")
                github_push_to(repo, f"v{v}/index.html", html_v, f"ui-evo v{v}")
                github_push_to(repo, f"v{v}/style.css", css, f"ui-evo css v{v}")
                github_push_to(repo, f"v{v}/script.js", js, f"ui-evo js v{v}")
            enable_pages(repo)
            time.sleep(50)
            scores = []
            for v in range(1, 4):
                png = take_screenshot(f"https://{GITHUB_USERNAME}.github.io/{repo}/v{v}/")
                if not png:
                    continue
                b64 = base64.b64encode(png).decode()
                score_txt = ask_vision("Puntuá esta interfaz del 1 al 10 en belleza y usabilidad. Respondé SOLO el número.", b64)
                digits = "".join(ch for ch in (score_txt or "") if ch.isdigit())[:2]
                score = float(digits) if digits else 0.0
                scores.append((score, v, png))
                if chat_id:
                    send_photo(chat_id, png, f"🎨 Variante {v} → score visual: {score:.0f}/10")
            if not scores:
                send_telegram(chat_id, "No pude capturar/puntuar variantes")
                return
            scores.sort(key=lambda x: x[0], reverse=True)
            best_score, best_v, best_png = scores[0]
            for fname in ["index.html", "style.css", "script.js"]:
                content = read_repo_file(repo, f"v{best_v}/{fname}")
                if content:
                    content = content.replace(f"v{best_v}/style.css", "style.css").replace(f"v{best_v}/script.js", "script.js")
                    github_push_to(repo, fname, content, f"ui-evo ganadora v{best_v}")
            url = f"https://{GITHUB_USERNAME}.github.io/{repo}/"
            save_knowledge(f"ui evolution: {desc}", f"gana variante {best_v} con score {best_score:.0f}/10")
            send_telegram(chat_id, f"🎨 EVOLUCIÓN DE UI COMPLETA\n3 diseños compitieron → ganó la variante {best_v} con {best_score:.0f}/10 de fitness visual\n🔴 EN VIVO: {url}")
            if chat_id:
                send_photo(chat_id, best_png, "🏆 La UI ganadora que quedó publicada")
        except Exception as e:
            save_reflection(f"ui evolution {desc[:60]}", e)
            send_telegram(chat_id, f"Error ui evolution: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Clonar, mejorar, asimilar ----------
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
            original = read_repo_file(repo, path)
            if original is None:
                send_telegram(chat_id, f"No encontré {path} en {repo}")
                return
            improved = clean_code(ask_role("critico", f"Mejorá este código sin romper su función: más eficiente, con docstrings y manejo de errores. Devolvé SOLO el código mejorado:\n{original[:6000]}"))
            msg = f"improve {path}" + (" [skip render]" if repo == GITHUB_REPO else "")
            ok = github_push_to(repo, path, improved, msg)
            send_telegram(chat_id, f"🔧 MEJORADO: {repo}/{path}\n{'Commit OK ✅' if ok else 'Falló el commit ❌'}\n\nAntes:\n{original[:300]}\n\nAhora:\n{improved[:600]}")
        except Exception as e:
            save_reflection(f"mejora {repo}/{path}", e)
            send_telegram(chat_id, f"Error mejorando: {e}")
    threading.Thread(target=worker, daemon=True).start()

def repo_license(full_repo):
    try:
        r = requests.get(f"https://api.github.com/repos/{full_repo}/license", headers=gh_headers(), timeout=15)
        if r.status_code == 200:
            lic = r.json().get("license") or {}
            return (lic.get("spdx_id") or lic.get("name") or "").lower()
    except Exception:
        pass
    return ""

def start_assimilate(chat_id, full_repo):
    def worker():
        try:
            lic = repo_license(full_repo)
            ok_lic = any(a in lic for a in ALLOWED_LICENSES) and "no license" not in lic
            if not ok_lic:
                send_telegram(chat_id, f"⚖️ CLONADO DENEGADO: {full_repo} tiene licencia '{lic or 'desconocida'}'. Solo asimilo código con licencia abierta (MIT, Apache, BSD, ISC, Unlicense, Modified MIT). Así tu proyecto sigue 100% legal.")
                return
            github_fork(full_repo)
            short = full_repo.split("/")[-1]
            r = requests.get(f"https://api.github.com/repos/{full_repo}/contents", headers=gh_headers(), timeout=20)
            files = [f for f in (r.json() if r.status_code == 200 else []) if f["type"] == "file" and f["name"].endswith((".md", ".py"))][:4]
            genes = []
            for f in files:
                try:
                    content = requests.get(f["download_url"], timeout=10).text[:9000]
                    if len(content) < 100: continue
                    genes.append(f"--- {f['name']} ---\n{content}")
                except Exception:
                    pass
            blob = "\n".join(genes)[:14000]
            if not blob:
                send_telegram(chat_id, f"⚖️ {full_repo} forkeado, pero sin archivos legibles para asimilar.")
                return
            skill = clean_code(ask_role("coder",
                f"Del siguiente código abierto (licencia {lic}) extraé las técnicas reutilizables y escribí UN skill Python plano: una clase con 2-3 métodos que repliquen las ideas principales, con docstring citando fuente y licencia. Solo código:\n{blob[:9000]}"))
            doc = ask_role("arquitecto", f"Resumí en 500 caracteres los principios clave de este proyecto abierto (licencia {lic}) para la memoria de un agente:\n{blob[:6000]}")
            github_push(f"tools/{short}_skill.py", skill, f"asimilar {short} (lic {lic}) [skip render]")
            github_push(f"tools_evolution/{short}_genes.md", doc or "", f"genes {short} [skip render]")
            CODE_LIBRARY[f"{short}_skill"] = skill
            save_knowledge(f"asimilado {full_repo} (licencia {lic})", (doc or short)[:200])
            send_telegram(chat_id, f"⚖️✅ CLON LEGAL + FUSIÓN COMPLETA\nRepo: {full_repo}\nLicencia verificada: {lic}\nFork: https://github.com/{GITHUB_USERNAME}/{short}\nGenes: tools_evolution/{short}_genes.md\nSkill: tools/{short}_skill.py\nTu agente autoevolutivo sigue intacto: solo ganó conocimiento.")
        except Exception as e:
            save_reflection(f"asimilar {full_repo}", e)
            send_telegram(chat_id, f"Error asimilando: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Genesis: crossover, sueños, selección ----------
def start_crossover(chat_id, nameA, nameB):
    def worker():
        try:
            a = CODE_LIBRARY.get(nameA)
            b = CODE_LIBRARY.get(nameB)
            if not a or not b:
                send_telegram(chat_id, "Falta alguno de los dos padres en la biblioteca.")
                return
            child = clean_code(ask_role("coder",
                f"Recombiná estas dos herramientas Python en UNA nueva que combine sus capacidades (crossover genético). Padre A:\n{a[:2500]}\nPadre B:\n{b[:2500]}\nDevolvé SOLO el código hijo, plano, sin markdown, con docstring citando a sus padres."))
            child, out = run_and_fix(child, f"combinar {nameA} y {nameB}")
            cname = f"child_{int(time.time())}"
            github_push(f"evolution/{cname}.py", child, f"crossover {nameA}+{nameB} [skip render]")
            CODE_LIBRARY[cname] = child
            genome_register("crossover", cname, parents=f"{nameA}+{nameB}", fitness=1.0, provenance="crossover interno")
            journal_write("crossover", f"Nació {cname} de {nameA} + {nameB}. Test: {out[:200]}")
            send_telegram(chat_id, f"🧬🔀 CROSSOVER (reproducción de código)\nPadres: {nameA} + {nameB}\nHijo: {cname}\n▶️ Test: {out[:250]}\nUsalo: usar {cname}")
        except Exception as e:
            save_reflection(f"crossover {nameA}+{nameB}", e)
            send_telegram(chat_id, f"Error crossover: {e}")
    threading.Thread(target=worker, daemon=True).start()

def dream_shift(chat_id):
    try:
        names = sorted(CODE_LIBRARY.keys())
        if len(names) < 2:
            return
        pa, pb = secrets.choice(names), secrets.choice(names)
        idea = ask_role("arquitecto", f"Soñá una capacidad NUEVA combinando estos dos genes y tu sabiduría. Gen A: {pa}. Gen B: {pb}. Sabiduría: {GLOBAL_KB[-400:]}\nRespondé en 1 línea qué herramienta nueva imaginar y por qué.")
        code = clean_code(ask_role("coder", f"Prototipá en Python plano, sin markdown, esta capacidad soñada: {idea}"))
        code, out = run_and_fix(code, (idea or "")[:200])
        ok = bool(out) and not out.startswith(("Error", "Timeout")) and "Traceback" not in out
        if ok:
            dname = f"dream_{int(time.time())}"
            github_push(f"evolution/{dname}.py", code, f"dream: {(idea or '')[:40]} [skip render]")
            CODE_LIBRARY[dname] = code
            genome_register("dream", dname, parents=f"{pa}+{pb}", fitness=1.0, provenance="sueño nocturno")
            journal_write("sueno", f"Soñé la capacidad: {idea} → nació {dname}. Test: {out[:150]}")
            if chat_id:
                send_telegram(chat_id, f"💭🌙 SUEÑO ADOPTADO\nSoñé: {idea}\nNació: {dname} ▶️ {out[:150]}\nUsalo: usar {dname}")
        else:
            journal_write("sueno", f"Soñé: {idea} → prototipo falló, descartado. Aprendizaje: {out[:150]}")
            if chat_id:
                send_telegram(chat_id, f"💭🌙 Sueño descartado: {(idea or '')[:120]} (falló el prototipo, aprendí del intento)")
    except Exception as e:
        print("[dream] error:", e)

def selection_report(chat_id):
    gens = genome_list()
    if not gens:
        return
    dead = [g for g in gens if (g.get("uses") or 0) == 0 and (g.get("fitness") or 0) == 0]
    stars = sorted([g for g in gens if (g.get("uses") or 0) > 0], key=lambda g: g.get("uses") or 0, reverse=True)[:5]
    msg = "🌿 SELECCIÓN NATURAL\nTop: " + (", ".join(f"{g.get('id')}({g.get('uses')})" for g in stars) or "nada usado aún") + f"\nEn riesgo de extinción: {len(dead)}"
    journal_write("seleccion", msg[:400])
    if chat_id:
        send_telegram(chat_id, msg)

# ---------- Núcleo profundo ----------
def solve_hard(chat_id, problem):
    def worker():
        try:
            tests = clean_code(ask_role("juez",
                f"Escribí SOLO líneas de assert planos (sin def, sin markdown) que verifiquen una función solve() para este problema: {problem}. Incluí 4 casos borde. Los asserts DEBEN llamar a solve con argumentos, por ejemplo assert solve(999)==27."))
            cands = []
            for mdl in HARD_MODELS:
                sol = clean_code(ask_groq(
                    f"Escribí SOLO una función Python llamada solve que resuelva: {problem}. Recibí los datos por parámetro (ej: solve(n)). NO uses input(). NO imprimas nada. Plana, sin markdown.", model=mdl))
                if sol:
                    cands.append((mdl, sol))
            results = []
            for mdl, sol in cands:
                out = run_sandbox(sol + "\n\n" + tests + "\nprint('TESTS OK')")
                okk = ("TESTS OK" in out) and ("Traceback" not in out) and ("AssertionError" not in out)
                results.append((1.0 if okk else 0.0, mdl, sol, out))
            if not results:
                send_telegram(chat_id, "Ningún modelo produjo candidato.")
                return
            results.sort(key=lambda x: x[0], reverse=True)
            score, mdl, best, out = results[0]
            if score < 1.0:
                fixed = clean_code(ask_groq(
                    f"Esta solución falla los tests. Problema: {problem}\nCódigo:\n{best[:2500]}\nSalida:\n{out[:600]}\nDevolvé SOLO la función solve corregida, plana, recibiendo los datos por parámetro (ej: solve(n)), sin input() y sin prints, de modo que los asserts solve(...) pasen."))
                if fixed:
                    out2 = run_sandbox(fixed + "\n\n" + tests + "\nprint('TESTS OK')")
                    if ("TESTS OK" in out2) and ("Traceback" not in out2) and ("AssertionError" not in out2):
                        best, out, score = fixed, out2, 1.0
            import re as _re
            margs = _re.search(r"solve\(([^)]*)\)", tests)
            demo_args = margs.group(1) if margs else ""
            best = best + f"\n\nif __name__ == '__main__':\n    print(solve({demo_args}))\n"
            name = f"solved_{int(time.time())}"
            proof = (f"# PROBLEMA\n{problem}\n\n# MODELOS COMPETIDORES\n" + ", ".join(m for m, _ in cands) +
                     f"\n\n# GANADOR\n{mdl}\n\n# SOLUCIÓN\n{best}\n\n# TESTS DEL VERIFICADOR\n{tests}\n\n# RESULTADO\n{out[:800]}\n")
            github_push(f"proofs/{name}.py", best, f"proof: {problem[:40]} [skip render]")
            github_push(f"proofs/{name}_proof.md", proof, f"proof doc {name} [skip render]")
            CODE_LIBRARY[name] = best
            genome_register("solved", name, parents=mdl, fitness=score, provenance="núcleo profundo verificado", task=problem)
            save_knowledge(f"resuelto y verificado: {problem}", best[:200])
            journal_write("proof", f"{problem[:100]} → {mdl} con score {score}")
            log_experiment(problem, out[:300], score >= 1.0)
            metafit_extend(problem, best)
            send_telegram(chat_id, f"🧠 NÚCLEO PROFUNDO\nProblema: {problem[:120]}\nCompitieron {len(cands)} modelos con tests generados por un verificador\nResultado: {'PASÓ TODOS LOS TESTS ✅' if score >= 1.0 else 'PARCIAL ⚠️'}\nGanador: {mdl}\n📄 Prueba pública: proofs/{name}.py y proofs/{name}_proof.md\n▶️ {out[:250]}")
        except Exception as e:
            save_reflection(f"resuelve {problem[:60]}", e)
            send_telegram(chat_id, f"Error núcleo: {e}")
    threading.Thread(target=worker, daemon=True).start()

def start_debate(chat_id, question):
    def worker():
        try:
            a = ask_groq(f"Argumentá A FAVOR con evidencia concreta: {question}", model="openai/gpt-oss-120b")
            b = ask_groq(f"Argumentá EN CONTRA con evidencia concreta: {question}", model="moonshotai/kimi-k2-instruct")
            synth = ask_role("juez", f"Pregunta: {question}\nTesis A:\n{a[:1200]}\nTesis B:\n{b[:1200]}\nSintetizá la conclusión más verdadera en 5 bullets, marcando qué lado ganó cada punto.")
            journal_write("debate", f"{question} → {synth[:300]}")
            send_telegram(chat_id, f"⚖️ DEBATE MULTI-MODELO\n{synth[:2000]}")
        except Exception as e:
            send_telegram(chat_id, f"Error debate: {e}")
    threading.Thread(target=worker, daemon=True).start()

def run_benchmark(chat_id):
    def worker():
        try:
            okc = 0
            lines = []
            for prob, assertion in FROZEN_CORE:
                sol = clean_code(ask_groq(f"Escribí SOLO una función solve() plana para: {prob}. Sin markdown."))
                out = run_sandbox(sol + "\n\n" + assertion + "\nprint('OK')")
                okk = out.strip().endswith("OK") and "Traceback" not in out
                okc += 1 if okk else 0
                lines.append(f"{'✅' if okk else '❌'} {prob}")
            pct = okc * 100 // len(FROZEN_CORE)
            journal_write("benchmark", f"Score {pct}% ({okc}/{len(FROZEN_CORE)}) núcleo congelado")
            save_knowledge("benchmark interno", f"score {pct}%")
            if chat_id:
                send_telegram(chat_id, "📊 BENCHMARK NÚCLEO CONGELADO (nunca cambia, no puede mentirse)\n" + "\n".join(lines) + f"\nTotal: {pct}%")
        except Exception as e:
            send_telegram(chat_id, f"Error benchmark: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Curriculum y meta-fitness ----------
def curriculum_next():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/curriculum", headers=sb_headers(),
                         params={"done": "eq.false", "order": "created_at.asc", "limit": "1"}, timeout=8)
        rows = r.json() if r.status_code == 200 else []
        if rows:
            return rows[0]
        ch = ask_role("arquitecto",
            f"Basado en tu biblioteca y sabiduría, proponé UN desafío nuevo y concreto de Python que estire tus capacidades actuales. Una sola línea.\nBiblioteca: {', '.join(sorted(CODE_LIBRARY.keys())[:10])}\nSabiduría: {GLOBAL_KB[-400:]}")
        if ch:
            requests.post(f"{SUPABASE_URL}/rest/v1/curriculum", headers=sb_headers(), json={"challenge": ch[:300]}, timeout=8)
            return {"id": None, "challenge": ch[:300]}
    except Exception as e:
        print("[curr] error:", e)
    return None

def curriculum_done(ch_id):
    if not ch_id:
        return
    try:
        requests.patch(f"{SUPABASE_URL}/rest/v1/curriculum", headers=sb_headers(),
                       params={"id": f"eq.{ch_id}"}, json={"done": True}, timeout=8)
    except Exception:
        pass

def metafit_extend(problem, solution):
    try:
        newt = clean_code(ask_role("juez",
            f"Proponé 2 asserts nuevos y MÁS DIFÍCILES (sin def, sin markdown) para una función solve() que resuelve: {problem}. Solución actual:\n{solution[:1500]}"))
        if newt:
            github_push(f"tests/ext_{int(time.time())}.py",
                        f"# suite extendida para: {problem[:80]}\n# requiere función solve()\n{newt}\nprint('SUITE OK')",
                        f"metafit: {problem[:40]} [skip render]")
    except Exception:
        pass

# ---------- LAB JARVIS ----------
def simulate_until_100(chat_id, problem, max_rounds=5):
    def worker():
        try:
            tests = clean_code(ask_role("juez",
                f"Escribí SOLO asserts planos (sin def, sin markdown) con 5 casos (incluí borde y error) para una función solve() que resuelve: {problem}. Para comparaciones con decimales usá round(x, 2) en ambos lados del assert."))
            sol = clean_code(ask_role("coder", f"Escribí SOLO una función solve() plana para: {problem}. Sin markdown."))
            log = []
            final_ok = False
            for rnd in range(1, max_rounds + 1):
                out = run_sandbox(sol + "\n\n" + tests + "\nprint('TESTS OK')")
                okk = ("TESTS OK" in out) and ("Traceback" not in out) and ("AssertionError" not in out)
                log.append(f"Ronda {rnd}: {'100% ✅' if okk else 'falló ❌'}")
                log_experiment(f"[sim r{rnd}] {problem}", out[:300], okk)
                if okk:
                    final_ok = True
                    break
                diag = ask_role("critico", f"Diagnóstico en 2 líneas de por qué falla este código según la salida. Problema: {problem}\nCódigo:\n{sol[:2000]}\nSalida:\n{out[:700]}")
                strategy = ["corregí el bug puntual", "reescribí la lógica desde cero con otro enfoque",
                            "agregué manejo de casos borde y tipos", "optimizá y simplificá manteniendo corrección",
                            "cambiá totalmente de algoritmo"][rnd - 1]
                sol = clean_code(ask_role("coder" if rnd % 2 else "arquitecto",
                    f"Estrategia de simulación: {strategy}. Diagnóstico previo: {diag}\nProblema: {problem}\nCódigo anterior:\n{sol[:2000]}\nSalida fallida:\n{out[:500]}\nDevolvé SOLO la función solve() nueva, plana."))
            name = f"sim_{int(time.time())}"
            github_push(f"proofs/{name}.py", sol, f"sim100: {problem[:40]} [skip render]")
            github_push(f"proofs/{name}_lab.md",
                        f"# SIMULACIÓN JARVIS\nProblema: {problem}\n\n## Rondas\n" + "\n".join(log) +
                        f"\n\n## Resultado\n{'100% logrado' if final_ok else 'no convergió en ' + str(len(log)) + ' rondas'}\n\n## Código final\n{sol}\n\n## Tests\n{tests}\n",
                        f"sim100 doc {name} [skip render]")
            CODE_LIBRARY[name] = sol
            genome_register("simulated", name, parents="lab-jarvis", fitness=1.0 if final_ok else 0.5,
                            provenance="simulación hasta 100%", task=problem)
            journal_write("simulacion", f"{problem[:100]} → {'100% en ' + str(len(log)) + ' rondas' if final_ok else 'no convergió'}")
            send_telegram(chat_id, f"🧪 LAB JARVIS (simulación hasta 100%)\nProblema: {problem[:120]}\n" + "\n".join(log) +
                          f"\n\nResultado: {'🎯 100% LOGRADO' if final_ok else '⚠️ no convergió, quedó el mejor intento'}\nReporte público: proofs/{name}_lab.md\nUsalo: usar {name}")
        except Exception as e:
            save_reflection(f"simula {problem[:60]}", e)
            send_telegram(chat_id, f"Error lab: {e}")
    threading.Thread(target=worker, daemon=True).start()

# ---------- Autonomía nocturna ----------
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
        if up.startswith("EVOLUCIONAR:"):
            task = decision.split(":", 1)[1].strip()
            cur_id = None
        else:
            cur = curriculum_next()
            cur_id = cur.get("id") if cur else None
            task = (cur.get("challenge") if cur else "") or CRON_TASKS[int(time.time()) % len(CRON_TASKS)]
        code, score, ok = evolve_program(task)
        code, out = run_and_fix(code, task)
        name = f"evolved_{int(time.time())}.py"
        github_push(f"evolution/{name}", code, f"[auto] evolve: {task[:40]} [skip render]")
        CODE_LIBRARY[name[:-3]] = code
        genome_register("evolved", name[:-3], parents="turno-autónomo", fitness=score, provenance="evolución nocturna", task=task)
        if ok or score >= 2.0:
            save_knowledge(f"[auto] {task}", code[:200])
        curriculum_done(cur_id)
        metafit_extend(task, code)
        log_experiment(task, out[:300], ok or score >= 2.0)
        if chat_id:
            send_telegram(chat_id, f"🌙 Turno autónomo: evolucioné '{task}'\nScore: {score:.2f} | ▶️ test: {out[:150]}\nUsalo: usar {name[:-3]}")
    except Exception as e:
        print("[auto] error:", e)
        save_reflection("turno autónomo", e)

def shift_wrapper():
    autonomous_shift()
    if secrets.randbelow(100) < 35:
        dream_shift(OWNER_CHAT[0])
    selection_report(OWNER_CHAT[0])

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
            {"command": "movil", "description": "Enviar tarea al celular (ARTEMIS)"},
            {"command": "piensa", "description": "Razonamiento profundo"},
            {"command": "simula", "description": "Lab: simular hasta 100%"},
            {"command": "proyecto", "description": "Proyecto PM+Arq+Ing+QA+visión"},
            {"command": "ui", "description": "Evolución de UI con fitness visual"},
            {"command": "app", "description": "App web rápida + auditoría"},
            {"command": "duelo", "description": "Torneo multi-modelo"},
            {"command": "evolucionar", "description": "Evolucionar un programa"},
            {"command": "asimilar", "description": "Clonar IA con auditoría legal"},
            {"command": "biblioteca", "description": "Código aprendido"},
        ]}, timeout=10)
    except Exception as e:
        print("[tg] commands:", e)

set_commands()

# ---------- Rutas ----------
@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

@app.route("/")
def home():
    return f"EVO V18 PUENTE - skills: {len(SKILLS)} - biblioteca: {len(CODE_LIBRARY)} - sabiduria: {len(GLOBAL_KB)} chars - memoria: {'ON' if SUPABASE_KEY else 'OFF'}", 200

@app.route("/cron")
def cron():
    admin_only()
    if time.time() - LAST_CRON[0] < 6 * 3600:
        return "cron: ya trabajé hace menos de 6h", 200
    LAST_CRON[0] = time.time()
    threading.Thread(target=shift_wrapper, daemon=True).start()
    return "cron: turno autónomo lanzado (puede incluir sueños)", 200

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

@app.route("/api/genesis")
def api_genesis():
    return jsonify({"genome": genome_list()[:40], "library": sorted(CODE_LIBRARY.keys()),
                    "sabiduria": GLOBAL_KB[-1500:], "skills": len(SKILLS)})

@app.route("/api/lab")
def api_lab():
    def get(table, limit=10):
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}", headers=sb_headers(),
                             params={"order": "created_at.desc", "limit": str(limit)}, timeout=8)
            return r.json() if r.status_code == 200 else []
        except Exception:
            return []
    try:
        aut = requests.get(f"{SUPABASE_URL}/rest/v1/autonomy", headers=sb_headers(),
                           params={"id": "eq.1"}, timeout=6).json() or [{}]
    except Exception:
        aut = [{}]
    return jsonify({"experiments": get("experiments", 15), "curriculum": get("curriculum", 10),
                    "journal": get("journal", 8), "genome": genome_list()[:20], "autonomy": aut[0],
                    "library": sorted(CODE_LIBRARY.keys())})

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
        if not chat_id:
            return "ok", 200
        OWNER_CHAT[0] = chat_id
        voice = (msg.get("voice") or msg.get("audio") or {})
        if not text and voice.get("file_id"):
            try:
                fi = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile", params={"file_id": voice["file_id"]}, timeout=10).json()
                dl = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/file/{fi['result']['file_path']}", timeout=25).content
                text = transcribe_audio(dl) or ""
                if text:
                    send_telegram(chat_id, f"🎧 Te escuché: {text[:200]}")
            except Exception as e:
                print("[voice] error:", e)
        if not text:
            return "ok", 200
        low = text.lower()

        if low.startswith("/start") or low == "hola":
            send_telegram(chat_id, "🧠 EVO V18 PUENTE activo.\n/movil <tarea> | /resuelve | /debate | /benchmark | /piensa | /simula | /proyecto | /ui | /app | /duelo | /evolucionar | /asimilar | /biblioteca | /genoma | /diario | /autonomia")
            return "ok", 200

        if low.startswith("movil status"):
            try:
                r = requests.get(f"{SUPABASE_URL}/rest/v1/artemis_queue", headers=sb_headers(),
                                 params={"order": "created_at.desc", "limit": "5",
                                         "select": "id,task,status,result,updated_at"}, timeout=10)
                rows = r.json() if r.status_code == 200 else []
                if not rows:
                    send_telegram(chat_id, "📱 No hay tareas móviles aún.")
                else:
                    lines = [f"[{(row.get('status') or '').upper()}] #{row.get('id')} · {(row.get('task') or '')[:60]}\n→ {(row.get('result') or '')[:120]}" for row in rows]
                    send_telegram(chat_id, "📱 ÚLTIMAS TAREAS MÓVILES:\n\n" + "\n\n".join(lines))
            except Exception as e:
                send_telegram(chat_id, f"Error consultando cola: {e}")
            return "ok", 200

        if low.startswith("movil "):
            instruction = text.split(" ", 1)[1].strip()
            if not instruction:
                send_telegram(chat_id, "Uso: movil <instrucción>. Ej: movil abrir calculadora y sumar 5 mas 3")
                return "ok", 200
            try:
                r = requests.post(f"{SUPABASE_URL}/rest/v1/artemis_queue", headers=sb_headers(),
                                  json={"task": instruction, "status": "pending"}, timeout=10)
                if r.status_code in (200, 201):
                    send_telegram(chat_id, f"📱 Tarea encolada para tu celular:\n→ {instruction[:150]}\nEl worker de Termux la toma en ~10 s.\nConsultá con: movil status")
                else:
                    send_telegram(chat_id, f"Error al encolar: {r.status_code}")
            except Exception as e:
                send_telegram(chat_id, f"Error conectando con Supabase: {e}")
            return "ok", 200

        if low.startswith("resuelve "):
            problem = text.split(" ", 1)[1]
            solve_hard(chat_id, problem)
            send_telegram(chat_id, f"🧠 Núcleo profundo activado: {problem[:100]}\n4 modelos compiten + verificador con tests + prueba pública. ~2 min.")
            return "ok", 200

        if low.startswith("debate "):
            question = text.split(" ", 1)[1]
            start_debate(chat_id, question)
            send_telegram(chat_id, f"⚖️ Debate iniciado: {question[:100]}")
            return "ok", 200

        if low.startswith("benchmark"):
            run_benchmark(chat_id)
            send_telegram(chat_id, "📊 Corriendo benchmark del núcleo congelado...")
            return "ok", 200

        if low.startswith("piensa "):
            q = text.split(" ", 1)[1]
            deep_think(chat_id, q)
            send_telegram(chat_id, f"🧠 Pensamiento profundo sobre: {q[:80]}")
            return "ok", 200

        if low.startswith("simula "):
            problem = text.split(" ", 1)[1]
            simulate_until_100(chat_id, problem)
            send_telegram(chat_id, f"🧪 Simulando en el lab: {problem[:100]}\nRondas de prueba→diagnóstico→reescritura hasta 100%. ~2-4 min.")
            return "ok", 200

        if low.startswith("ui ") or low == "/ui":
            desc = text.split(" ", 1)[1] if " " in text else ""
            if not desc:
                send_telegram(chat_id, "Uso: ui <descripción>")
                return "ok", 200
            start_ui_evolution(chat_id, desc)
            send_telegram(chat_id, f"🎨 Evolución de UI iniciada: {desc}\n3 diseños → screenshots → fitness visual. ~3-5 min.")
            return "ok", 200

        if low.startswith("auditar "):
            url = text.split(" ", 1)[1].strip()
            if not url.startswith("http"):
                url = "https://" + url
            threading.Thread(target=visual_audit, args=(chat_id, url, "web auditada a pedido", 2), daemon=True).start()
            send_telegram(chat_id, f"👁️ Auditando visualmente: {url}")
            return "ok", 200

        if low.startswith("duelo ") or low == "/duelo":
            task = text.split(" ", 1)[1] if " " in text else ""
            if not task:
                send_telegram(chat_id, "Uso: duelo <task>")
                return "ok", 200
            start_duel(chat_id, task)
            send_telegram(chat_id, f"⚔️ Duelo iniciado: {task[:100]}")
            return "ok", 200

        if low.startswith("proyecto ") or low == "/proyecto":
            desc = text.split(" ", 1)[1] if " " in text else ""
            if not desc:
                send_telegram(chat_id, "Uso: proyecto <descripción>")
                return "ok", 200
            start_project(chat_id, desc)
            send_telegram(chat_id, f"🏗️ Proyecto iniciado: {desc}\nPM → Arq → Ing → QA → 👁️ visión. ~3-5 min.")
            return "ok", 200

        if low.startswith("app ") or low == "/app":
            desc = text.split(" ", 1)[1] if " " in text else ""
            if not desc:
                send_telegram(chat_id, "Uso: app <descripción>")
                return "ok", 200
            start_app_build(chat_id, desc)
            send_telegram(chat_id, f"🌐 Construyendo app: {desc} (~1-2 min + auditoría visual)")
            return "ok", 200

        if low.startswith("asimilar "):
            full = text.split(" ", 1)[1].strip()
            if "/" not in full:
                send_telegram(chat_id, "Uso: asimilar usuario/repo")
                return "ok", 200
            start_assimilate(chat_id, full)
            send_telegram(chat_id, f"⚖️ Analizando licencia y asimilando {full}...")
            return "ok", 200

        if low.startswith("cruzar "):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                send_telegram(chat_id, "Uso: cruzar <nombreA> <nombreB>")
                return "ok", 200
            start_crossover(chat_id, parts[1].strip(), parts[2].strip())
            send_telegram(chat_id, f"🔀 Cruzando {parts[1]} + {parts[2]}...")
            return "ok", 200

        if low.startswith("busca "):
            q = text.split(" ", 1)[1]
            res = sense_search(q)
            reply = ask_groq(f"Con esta búsqueda de Wikipedia, respondé breve y en español: {q}\n{res[:1500]}")
            send_telegram(chat_id, f"🔎 {q}\n{reply[:1500]}\nFuente: Wikipedia")
            return "ok", 200

        if low.startswith("lee "):
            url = text.split(" ", 1)[1].strip()
            if not url.startswith("http"):
                url = "https://" + url
            content = sense_read(url)
            if not content:
                send_telegram(chat_id, "No pude leer esa URL.")
                return "ok", 200
            reply = ask_groq(f"Resumí en 6 bullets lo esencial de este texto:\n{content[:6000]}")
            send_telegram(chat_id, f"📖 {url}\n{reply[:2000]}")
            return "ok", 200

        if "genoma" in low:
            gens = genome_list()
            lines = [f"• {g.get('id')} [{g.get('kind')}] padres: {g.get('parents') or '-'} usos: {g.get('uses')}" for g in gens[:15]]
            send_telegram(chat_id, "🧬 GENOMA (linaje de criaturas):\n" + ("\n".join(lines) or "aún sin criaturas registradas"))
            return "ok", 200

        if "diario" in low:
            try:
                r = requests.get(f"{SUPABASE_URL}/rest/v1/journal", headers=sb_headers(),
                                 params={"order": "created_at.desc", "limit": "5"}, timeout=8)
                rows = r.json() if r.status_code == 200 else []
                send_telegram(chat_id, "📓 DIARIO DEL AGENTE:\n" + ("\n\n".join(f"[{x.get('phase')}] {(x.get('entry') or '')[:300]}" for x in rows) or "aún sin entradas"))
            except Exception:
                send_telegram(chat_id, "Diario no disponible.")
            return "ok", 200

        if "curriculo" in low or "currículo" in low:
            try:
                r = requests.get(f"{SUPABASE_URL}/rest/v1/curriculum", headers=sb_headers(),
                                 params={"order": "created_at.desc", "limit": "8"}, timeout=8)
                rows = r.json() if r.status_code == 200 else []
                lines = [f"{'✅' if x.get('done') else '⏳'} {x.get('challenge')}" for x in rows]
                send_telegram(chat_id, "🎯 SU PROPIO CURRICULUM:\n" + ("\n".join(lines) or "aún sin desafíos"))
            except Exception:
                send_telegram(chat_id, "Curriculum no disponible.")
            return "ok", 200

        if "experimentos" in low:
            try:
                r = requests.get(f"{SUPABASE_URL}/rest/v1/experiments", headers=sb_headers(),
                                 params={"order": "created_at.desc", "limit": "6"}, timeout=8)
                rows = r.json() if r.status_code == 200 else []
                lines = [f"{'✅' if x.get('ok') else '❌'} {x.get('hypothesis')[:90]}" for x in rows]
                send_telegram(chat_id, "🔬 SUS EXPERIMENTOS:\n" + ("\n".join(lines) or "aún sin experimentos"))
            except Exception:
                send_telegram(chat_id, "Experimentos no disponibles.")
            return "ok", 200

        if "autonomia" in low or "autonomía" in low:
            try:
                r = requests.get(f"{SUPABASE_URL}/rest/v1/autonomy", headers=sb_headers(), params={"id": "eq.1"}, timeout=6)
                row = (r.json() or [{}])[0]
                t, o = row.get("total") or 0, row.get("own") or 0
                pct = (o * 100 // t) if t else 0
                send_telegram(chat_id, f"🔓 AUTONOMÍA REAL\nRespuestas con mi propio código probado: {o}/{t} ({pct}%)\nCuanto más suba, menos dependo de IAs externas.")
            except Exception:
                send_telegram(chat_id, "Métricas no disponibles.")
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
            genome_use(name)
            out = run_sandbox(code)
            send_telegram(chat_id, f"▶️ {name}:\n{out[:3000]}")
            return "ok", 200

        if len(text) > 12:
            hit = own_answer(text)
            if hit:
                bump_autonomy(True)
                send_telegram(chat_id, f"🔓 AUTONOMÍA ({hit[0]}): respondí con MI PROPIO código probado, sin pedirle nada a ninguna IA externa.\n▶️ {hit[1][:1500]}")
                return "ok", 200
            bump_autonomy(False)

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


# ---------- Memoria semantica: guardar despues de cada interaccion ----------
def save_semantic_memory(content, fuente="chat"):
    """Guarda un recuerdo en memoria_vec. Falla en silencio."""
    try:
        from memoria_sem import guardar
        guardar(content, fuente=fuente)
    except Exception as e:
        print(f"[mem_sem] fallo al guardar: {e}")
