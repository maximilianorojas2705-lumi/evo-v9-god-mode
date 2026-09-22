def generar_contraseña(longitud=8):
    import string, random
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def crear(task):
    # Detectar solicitud de generación de contraseña
    if "contraseña" in task.lower() and any(str(num) in task for num in range(4, 13)):
        # extraer longitud si se menciona, por ejemplo "8 caracteres"
        import re
        match = re.search(r'(\d+)\s*caracter', task.lower())
        longitud = int(match.group(1)) if match else 8
        return f"🔐 Contraseña generada ({longitud} caracteres): {generar_contraseña(longitud)}"
    # Aquí puedes añadir más sub‑comandos bajo "crear"
    return "❓ No entiendo la petición de crear."