#!/usr/bin/env python3
"""Agente de visión con Reflexion: aprende de errores de navegación."""
import sys, reflexion, skill_vision

def ver_y_tocar_con_reflexion(objetivo):
    """Ejecuta visión consultando lecciones previas."""
    # 1. Consultar lecciones relevantes
    lecciones = reflexion.obtener_lecciones_relevantes(objetivo)
    if lecciones:
        print(f"[vision] Lecciones previas consultadas:\n{lecciones}\n")
    
    # 2. Intentar ejecutar la tarea
    resultado = skill_vision.ver_y_tocar(objetivo, max_pasos=5)
    
    # 3. Si falló, reflexionar sobre el error
    if "❌" in resultado or "⏱️" in resultado:
        print("[vision] ❌ Tarea falló, reflexionando...")
        reflexion.reflexionar_sobre_error(
            contexto=f"Intentando: {objetivo}",
            error=resultado
        )
    
    return resultado

if __name__ == "__main__":
    objetivo = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "abrí la calculadora"
    print(ver_y_tocar_con_reflexion(objetivo))
