#!/usr/bin/env python3
"""Repara el bloque roto y aplica memoria semantica sin regex peligrosos."""
import shutil
from datetime import datetime
SRC = 'app.py'
shutil.copy(SRC, f'app_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py')
lineas = open(SRC, encoding='utf-8').read().split('\n')

BLOQUE = [
    '    # Memoria semantica: recuerdos por significado (pgvector + Gemini embeddings)',
    '    try:',
    '        recuerdos_sem = recordar_sem(prompt, limite=3)',
    '        if recuerdos_sem:',
    '            system += "\\n\\nRecuerdos relevantes por significado (usa estos si son pertinentes):\\n" + recuerdos_sem',
    '    except Exception as e:',
    '        print(f"[mem_sem] fallo al recordar: {e}")',
]

# 1) Extirpar bloque viejo o roto (desde el comentario hasta el except)
ini = fin = -1
for i, l in enumerate(lineas):
    if '# Memoria semantica: recuerdos por significado' in l:
        ini = i
    if ini >= 0 and 'fallo al recordar' in l:
        fin = i
        break
if ini >= 0 and fin > ini:
    del lineas[ini:fin+1]
    print(f'extirpado bloque roto (lineas {ini+1}-{fin+1})')
else:
    print('no habia bloque previo que extirpar')

# 2) Insertar bloque sano despues del if GLOBAL_KB
texto = '\n'.join(lineas)
marcador = '        system += f"\\nCosas que YA aprendiste en evoluciones anteriores (usalas):\\n{GLOBAL_KB}"'
if marcador in texto:
    texto = texto.replace(marcador, marcador + '\n' + '\n'.join(BLOQUE), 1)
    print('bloque sano insertado despues de GLOBAL_KB')
else:
    print('ERROR: marcador GLOBAL_KB no encontrado')

# 3) Import (si falta)
if 'from memoria_sem import' not in texto:
    ls = texto.split('\n')
    for i, l in enumerate(ls):
        if l.startswith('import os,'):
            ls.insert(i+1, 'from memoria_sem import recordar as recordar_sem')
            break
    texto = '\n'.join(ls)
    print('import agregado')
else:
    print('import ya presente')

# 4) Funcion auxiliar (si falta)
if 'def save_semantic_memory' not in texto:
    texto = texto.rstrip() + '\n\n\n# ---------- Memoria semantica ----------\ndef save_semantic_memory(content, fuente="chat"):\n    try:\n        from memoria_sem import guardar\n        guardar(content, fuente=fuente)\n    except Exception as e:\n        print(f"[mem_sem] fallo al guardar: {e}")\n'
    print('funcion agregada')
else:
    print('funcion ya presente')

open(SRC, 'w', encoding='utf-8').write(texto)
print('app.py reescrito')
