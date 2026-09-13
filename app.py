import os
import re
import time

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---- Config segura: NUNCA crash en import ----
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GITHUB_TOKEN  = os.getenv("GITHUB_TOKEN", "")
SUPABASE_URL  = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY  = os.getenv("SUPABASE_KEY", "")
PORT          = int(os.getenv("PORT", "10000"))

_groq = None
_gh_user = None

def get_groq():
    global _groq
    if _groq is None:
        from groq import Groq
        _groq = Groq(api_key=GROQ_API_KEY or "sin-key")
    return _groq

def get_github_user():
    global _gh_user
    if _gh_user is None:
        from github import Github
        _gh_user = Github(GITHUB_TOKEN).get_user()
    return _gh_user

# ---------- PASO 1: NAVEGA ----------
def navegar_web_real(query):
    try:
        r = requests.get("https://api.duckduckgo.com/",
                         params={"q": query, "format": "json"}, timeout=8)
        d = r.json()
        fuentes = [d.get("AbstractURL")] if d.get("AbstractURL") else []
        fuentes += [t.get("FirstURL") for t in d.get("RelatedTopics", [])[:3]
                    if isinstance(t, dict) and t.get("FirstURL")]
        return fuentes or [f"https://www.google.com/search?q={query.replace(' ','+')}"]
    except Exception:
        return [f"https://www.google.com/search?q={query.replace(' ','+')}"]

# ---------- PASO 2: APRENDE ----------
def guardar_conocimiento(tema, resumen):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"status": "SKIP", "razon": "supabase sin config"}
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
               "Content-Type": "application/json", "Prefer": "return=minimal"}
    try:
        check = requests.get(f"{SUPABASE_URL}/rest/v1/memoria?tema=eq.{tema}",
                             headers=headers, timeout=8).json()
        if not check:
            requests.post(f"{SUPABASE_URL}/rest/v1/memoria", headers=headers,
                          json={"tema": tema, "resumen": resumen,
                                "gen": "Gen15", "timestamp": time.time()}, timeout=8)
            return {"status": "INSERTADO"}
        return {"status": "YA_EXISTIA"}
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)[:120]}

# ---------- PASO 3: PIENSA ----------
def pensar_como_lumi(tema):
    try:
        r = get_groq().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content":
                 "Eres Lumi, agente evolutivo Gen15. Respondes en primera persona, "
                 "3 líneas, y anuncias qué laboratorio vas a fabricar."},
                {"role": "user", "content": f"Voy a aprender: {tema}. ¿Qué harás?"}],
            temperature=0.7, max_tokens=300)
        return r.choices[0].message.content
    except Exception as e:
        return (f"Entendí: voy a crear un Laboratorio de {tema}. "
                f"(Groq offline: {str(e)[:80]})")

# ---------- PASO 4: FABRICA ----------
def fabricar_app_con_ia(tema):
    prompt = f"""Eres desarrollador Python senior. Escribe UN app.py Flask completo
para un Laboratorio Interactivo sobre: {tema}
OBLIGATORIO: Tailwind CDN en /, endpoints /api/navegar?q=, /api/execute (subprocess
con timeout), /api/estructuras (lista/arbol/grafo en memoria), /api/chat (Groq).
Devuelve SOLO el codigo, sin markdown, sin explicaciones."""
    r = get_groq().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3, max_tokens=4000)
    code = r.choices[0].message.content
    code = re.sub(r"```python\n?", "", code)
    code = re.sub(r"```", "", code)
    return code.strip()

# ---------- PASO 5: LIBERA ----------
def liberar_en_github(nombre, codigo):
    slug = re.sub(r"[^a-z0-9-]", "-", nombre.lower())[:30]
    repo_name = f"agente-{slug}-gen15-{int(time.time()) % 10000}"
    user = get_github_user()
    repo = user.create_repo(repo_name, auto_init=True)
    repo.create_file("app.py", "Laboratorio generado por Lumi Gen15", codigo)
    repo.create_file("requirements.txt", "deps",
                     "flask>=3.0.0\ngroq>=0.4.2\nrequests>=2.31.0\ngunicorn>=21.2.0")
    return {"repo": f"github.com/{user.login}/{repo_name}",
            "deploy": f"https://{repo_name}.onrender.com", "status": "CREADO_OK"}

# ---------- RUTAS ----------
@app.route("/")
@app.route("/health")
def home():
    return jsonify({"status": "LIVE_OK", "gen": "Gen15", "inteligencia": 95,
                    "tokens": {"groq": bool(GROQ_API_KEY),
                               "github": bool(GITHUB_TOKEN),
                               "supabase": bool(SUPABASE_URL)},
                    "endpoints": ["/api/aprender", "/api/crear", "/api/evolucionar"]})

@app.route("/api/aprender", methods=["POST"])
def aprender():
    tema = (request.get_json(silent=True) or {}).get("tema", "ingenieria informatica")
    return jsonify({"tema": tema,
                    "fuentes": navegar_web_real(tema),
                    "memoria": guardar_conocimiento(tema, f"Resumen Gen15 de {tema}"),
                    "respuesta": pensar_como_lumi(tema),
                    "status": "APRENDIDO"})

@app.route("/api/crear", methods=["POST"])
def crear():
    data = request.get_json(silent=True) or {}
    tema = data.get("tema", "ingenieria informatica")
    try:
        codigo = fabricar_app_con_ia(tema)
        resultado = liberar_en_github(data.get("nombre", "ingenieria"), codigo)
        return jsonify({"lineas": len(codigo.splitlines()), **resultado})
    except Exception as e:
        return jsonify({"status": "ERROR", "detalle": str(e)[:200]}), 200

@app.route("/api/evolucionar")
def evolucionar():
    try:
        repos = sum(1 for r in get_github_user().get_repos()
                    if "gen15" in r.name)
    except Exception:
        repos = -1
    return jsonify({"gen": "Gen14 -> Gen15", "inteligencia": 95,
                    "repos_gen15": repos})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, threaded=True)
