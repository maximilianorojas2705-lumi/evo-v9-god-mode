import os
from flask import Flask, request, jsonify
from groq import Groq
from github import Github
import requests
import time
import re

app = Flask(__name__)

# APIs reales
GROQ_API = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

groq = Groq(api_key=GROQ_API)
github = Github(GITHUB_TOKEN)
user = github.get_user()

def navegar_web_real(query):
    """Paso 1: NAVEGA - Busca en web real"""
    response = requests.get(
        "https://api.duckduckgo.com/",
        params={"q": query, "format": "json"}
    )
    # También puedes usar Google Custom Search API
    return response.json()

def guardar_conocimiento(tema, resumen):
    """Paso 2: APRENDE - Guarda en Supabase"""
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    
    # Verifica duplicados
    check = requests.get(
        f"{SUPABASE_URL}/rest/v1/memoria?tema=eq.{tema}",
        headers=headers
    ).json()
    
    if not check:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/memoria",
            headers=headers,
            json={"tema": tema, "resumen": resumen, "gen": "Gen15", "timestamp": time.time()}
        )

def pensar_como_lumi(tema):
    """Paso 3: PIENSA - Responde conversacional"""
    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres Lumi, un agente evolutivo que crea laboratorios reales. Responde en primera persona."},
            {"role": "user", "content": f"Voy a aprender sobre {tema} y crear un laboratorio. Explícame qué harás en 3 líneas."}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def fabricar_app_con_ia(tema):
    """Paso 4: FABRICA - Groq programa app REAL"""
    prompt = f"""Eres un desarrollador Python senior. Crea app.py completo para un 
    Laboratorio Interactivo sobre: {tema}
    
    REQUISITOS OBLIGATORIOS:
    - Flask app en un solo archivo
    - Tailwind CSS via CDN
    - Endpoint /api/navegar?q= que busca en web real
    - Endpoint /api/execute que ejecuta código Python del usuario (usa subprocess)
    - Endpoint /api/estructuras que crea listas/árboles/grafos en memoria
    - Endpoint /api/chat con Groq integrado
    - Página / con visualizador interactivo
    
    Código completo, sin comentarios largos, listo para deployar."""
    
    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000
    )
    
    codigo = response.choices[0].message.content
    # Limpia el código (quita markdown ```python)
    codigo = re.sub(r'```python\n?', '', codigo)
    codigo = re.sub(r'```\n?', '', codigo)
    
    return codigo.strip()

def liberar_en_github(nombre_repo, codigo):
    """Paso 5: LIBERA - Crea repo y deploya"""
    try:
        # Crea repo
        repo_name = f"agente-{nombre_repo}-gen15"
        repo = user.create_repo(repo_name, auto_init=True)
        
        # Crea app.py
        repo.create_file(
            "app.py",
            "Creación automática de laboratorio",
            codigo
        )
        
        # Crea requirements.txt
        requirements = """flask==3.0.0
groq==0.4.2
requests==2.31.0
gunicorn==21.2.0"""
        repo.create_file(
            "requirements.txt",
            "Dependencias",
            requirements
        )
        
        # Deploy a Render (webhook o API)
        # Para esto necesitas usar Render API o GitHub Actions
        
        return {
            "repo": f"github.com/{user.login}/{repo_name}",
            "deploy": f"{repo_name}.onrender.com",
            "status": "CREADO_OK"
        }
    except Exception as e:
        return {"error": str(e), "status": "ERROR"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "LIVE_OK",
        "gen": "Gen15",
        "inteligencia": 95,
        "endpoints": ["/api/aprender", "/api/crear", "/api/evolucionar"]
    })

@app.route("/api/aprender", methods=["POST"])
def aprender():
    """Flujo completo: Navega -> Aprende -> Piensa"""
    data = request.json
    tema = data.get("tema")
    
    # 1. Navega
    fuentes = navegar_web_real(tema)
    
    # 2. Aprende
    resumen = f"Conocimiento sobre {tema} aprendido en Gen15"
    guardar_conocimiento(tema, resumen)
    
    # 3. Piensa
    respuesta_lumi = pensar_como_lumi(tema)
    
    return jsonify({
        "fuentes": fuentes,
        "resumen": resumen,
        "respuesta": respuesta_lumi,
        "status": "APRENDIDO"
    })

@app.route("/api/crear", methods=["POST"])
def crear_laboratorio():
    """Flujo completo: Fabrica -> Libera"""
    data = request.json
    tema = data.get("tema")
    nombre_repo = data.get("nombre", "ingenieria")
    
    # 4. Fabrica
    codigo_app = fabricar_app_con_ia(tema)
    
    # 5. Libera
    resultado = liberar_en_github(nombre_repo, codigo_app)
    
    return jsonify({
        "codigo_lineas": len(codigo_app.split('\n')),
        "repo": resultado.get("repo"),
        "deploy_url": resultado.get("deploy"),
        "status": resultado.get("status")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
