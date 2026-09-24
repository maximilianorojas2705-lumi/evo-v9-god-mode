#!/usr/bin/env python3
"""Parche definitivo: modelo gemini-2.5-flash + variable GEMINI_KEY definida."""
import shutil
from datetime import datetime

SRC = "app.py"
shutil.copy(SRC, f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
print("backup creado")

src = open(SRC, encoding="utf-8").read()

# 1) Asegurar que GEMINI_KEY esté definida (si no está, la agregamos)
if "GEMINI_KEY" not in src or "GEMINI_KEY = " not in src:
    # Buscar dónde definir la variable (cerca de GROQ_API_KEY)
    if "GROQ_API_KEY = " in src:
        src = src.replace("GROQ_API_KEY = ", 
                          "GROQ_API_KEY = ", 1).replace(
                              "GROQ_API_KEY = ", 
                              'GROQ_API_KEY = os.getenv("GROQ_API_KEY", os.getenv("GROQ_KEY", ""))\nGEMINI_KEY = os.getenv("GEMINI_KEY", "")\n', 1)
        print("✅ GEMINI_KEY agregada cerca de GROQ_API_KEY")
    else:
        # Agregar al inicio después de imports
        src = 'import os\nGEMINI_KEY = os.getenv("GEMINI_KEY", "")\n' + src
        print("✅ GEMINI_KEY agregada al inicio")
else:
    print("ℹ️ GEMINI_KEY ya existe")

# 2) Cambiar modelo en ask_vision
if "gemini-1.5-flash" in src:
    src = src.replace("gemini-1.5-flash", "gemini-2.5-flash")
    print("✅ Modelo cambiado a gemini-2.5-flash")
else:
    print("ℹ️ Modelo ya no es gemini-1.5-flash")

open(SRC, "w", encoding="utf-8").write(src)
print("app.py reescrito")
