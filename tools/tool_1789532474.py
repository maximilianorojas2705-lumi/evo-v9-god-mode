import subprocess
import time
from pathlib import Path

# Ruta del script que se ejecutará cada hora
SCRIPT_PATH = Path("tool_1789516825.py")
# Archivo donde se guardarán los guiones generados
OUTPUT_FILE = Path("ideas_virales.txt")

# Intervalo de ejecución en segundos (1 hora)
INTERVAL = 60 * 60


def run_tool_and_save():
    """Ejecuta el script y guarda su salida en ideas_virales.txt."""
    try:
        # Ejecutar el script y capturar su salida (stdout)
        result = subprocess.run(
            ["", str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()

        # Añadir la salida al archivo de ideas virales
        with OUTPUT_FILE.open("a", encoding="utf-8") as f:
            f.write(output + "\n")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Guión guardado correctamente.")
    except subprocess.CalledProcessError as e:
        # En caso de error, registrar la salida de error
        error_msg = e.stderr.strip() if e.stderr else "Error desconocido"
        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error al ejecutar el script: {error_msg}"
        )


if __name__ == "__main__":
    print("Iniciando el programador de guiones (ejecución cada hora).")
    while True:
        run_tool_and_save()
        time.sleep(INTERVAL)