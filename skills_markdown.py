import os

SKILLS_DIR = os.path.expanduser("~/evo-brain/skills")
SKILL_ACTIVA_FILE = os.path.expanduser("~/evo-brain/skill_activa.txt")

os.makedirs(SKILLS_DIR, exist_ok=True)

def listar_skills():
    if not os.path.exists(SKILLS_DIR):
        return []
    archivos = os.listdir(SKILLS_DIR)
    return [f.replace(".md", "") for f in archivos if f.endswith(".md")]

def obtener_skill_activa():
    if os.path.exists(SKILL_ACTIVA_FILE):
        try:
            with open(SKILL_ACTIVA_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return None
    return None

def activar_skill(nombre_skill):
    skills = listar_skills()
    if nombre_skill in skills:
        with open(SKILL_ACTIVA_FILE, "w", encoding="utf-8") as f:
            f.write(nombre_skill)
        return True
    return False

def desactivar_skill():
    if os.path.exists(SKILL_ACTIVA_FILE):
        os.remove(SKILL_ACTIVA_FILE)
        return True
    return False

def obtener_prompt_skill_activa():
    nombre = obtener_skill_activa()
    if not nombre:
        return ""
    filepath = os.path.join(SKILLS_DIR, f"{nombre}.md")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                contenido = f.read().strip()
                return f"\n\n--- MODULO SKILL ACTIVO: {nombre.upper()} ---\n{contenido}\n--- FIN SKILL ---"
        except Exception:
            return ""
    return ""
