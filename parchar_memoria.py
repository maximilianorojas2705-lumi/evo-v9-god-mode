#!/usr/bin/env python3
"""Aplica los 3 cambios de memoria semantica a app.py. No destructivo."""
import os, shutil, re
from datetime import datetime

SRC = "app.py"
BAK = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

# 1. Backup
shutil.copy(SRC, BAK)
print(f"✅ backup creado: {BAK}")

src = open(SRC, "r", encoding="utf-8").read()
src_original = src
cambios = 0

# CAMBIO 1: importar memoria_sem
if "from memoria_sem import" not in src:
    src = src.replace(
        "import os, base64, time, glob, importlib.util, subprocess, sys, threading, secrets, requests",
        "import os, base64, time, glob, importlib.util, subprocess, sys, threading, secrets, requests\nfrom memoria_sem import recordar as recordar_sem",
        1
    )
    cambios += 1
    print("✅ cambio 1: import agregado")
else:
    print("⚠️ cambio 1: ya existía el import")

# CAMBIO 2: inyectar recuerdos en system prompt (justo despues de GLOBAL_KB)
bloque_recuerdos = """
    # Memoria semantica: recuerdos por significado (pgvector + Gemini embeddings)
    try:
        recuerdos_sem = recordar_sem(prompt, limite=3)
        if recuerdos_sem:
            system += f"\\n\\nRecuerdos relevantes por significado (usa estos si son pertinentes):\\n{recuerdos_sem}"
    except Exception as e:
        print(f"[mem_sem] fallo al recordar: {e}")
"""

if "recuerdos_sem = recordar_sem" not in src:
    # Buscar el bloque de GLOBAL_KB y agregar despues
    patron = r'(    if GLOBAL_KB:\n        system \+= f"\\nCosas que YA aprendiste en evoluciones anteriores \(usalas\):\\n\{GLOBAL_KB\}")'
    if re.search(patron, src):
        src = re.sub(patron, r'\1' + bloque_recuerdos, src, count=1)
        cambios += 1
        print("✅ cambio 2: recuerdos inyectados despues de GLOBAL_KB")
    else:
        # Fallback: agregar despues del primer system += 
        patron2 = r'(        system \+= f"\\nConocimiento de tus cerebros fusionados:\\n\{BRAIN_CONTEXT\}")'
        if re.search(patron2, src):
            src = re.sub(patron2, r'\1' + bloque_recuerdos, src, count=1)
            cambios += 1
            print("✅ cambio 2: recuerdos inyectados despues de BRAIN_CONTEXT (fallback)")
        else:
            print("❌ cambio 2: NO se pudo encontrar punto de inserción")
else:
    print("⚠️ cambio 2: ya existía la inyección")

# CAMBIO 3: funcion save_semantic_memory al final
if "def save_semantic_memory" not in src:
    funcion_aux = """

# ---------- Memoria semantica: guardar despues de cada interaccion ----------
def save_semantic_memory(content, fuente="chat"):
    \"\"\"Guarda un recuerdo en memoria_vec. Falla en silencio.\"\"\"
    try:
        from memoria_sem import guardar
        guardar(content, fuente=fuente)
    except Exception as e:
        print(f"[mem_sem] fallo al guardar: {e}")
"""
    src = src.rstrip() + "\n" + funcion_aux
    cambios += 1
    print("✅ cambio 3: funcion save_semantic_memory agregada")
else:
    print("⚠️ cambio 3: ya existía la funcion")

if cambios > 0:
    open(SRC, "w", encoding="utf-8").write(src)
    print(f"\n🎉 {cambios} cambios aplicados a {SRC}")
    print(f"📊 tamaño nuevo: {len(src)} bytes (antes: {len(src_original)})")
else:
    print("\nℹ️ el archivo ya estaba parcheado, no se escribió nada")
