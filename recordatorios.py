"""Sistema de recordatorios programados con Supabase."""
import requests, os
from datetime import datetime, timedelta
import re

def _supa():
    secrets = {}
    for ruta in ["~/artemis-bridge/.secrets", "~/.secrets"]:
        r = os.path.expanduser(ruta)
        if os.path.exists(r):
            for linea in open(r):
                if "=" in linea:
                    k, v = linea.split("=", 1)
                    secrets[k.strip()] = v.strip()
    return secrets.get("SUPABASE_URL", ""), secrets.get("SUPABASE_KEY", "")

def parsear_tiempo(texto):
    """Convierte texto a timedelta o datetime.
    
    Ejemplos:
    - "2h" -> timedelta(hours=2)
    - "30m" -> timedelta(minutes=30)
    - "1d" -> timedelta(days=1)
    - "14/03" -> datetime del próximo 14 de marzo a las 9am
    - "14/03 15:00" -> datetime del próximo 14 de marzo a las 15:00
    """
    texto = texto.strip().lower()
    
    # Formato relativo: 2h, 30m, 1d
    match = re.match(r'^(\d+)([hmd])$', texto)
    if match:
        valor, unidad = int(match.group(1)), match.group(2)
        if unidad == 'h':
            return timedelta(hours=valor)
        elif unidad == 'm':
            return timedelta(minutes=valor)
        elif unidad == 'd':
            return timedelta(days=valor)
    
    # Formato de fecha: 14/03 o 14/03 15:00
    match = re.match(r'^(\d{1,2})/(\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?$', texto)
    if match:
        dia, mes = int(match.group(1)), int(match.group(2))
        hora = int(match.group(3)) if match.group(3) else 9
        minuto = int(match.group(4)) if match.group(4) else 0
        
        ahora = datetime.now()
        año = ahora.year
        fecha = datetime(año, mes, dia, hora, minuto)
        
        # Si la fecha ya pasó este año, usar el próximo
        if fecha < ahora:
            fecha = datetime(año + 1, mes, dia, hora, minuto)
        
        return fecha
    
    return None

def programar_recordatorio(user_id, mensaje, tiempo):
    """Programa un recordatorio.
    
    Args:
        user_id: ID del usuario de Telegram
        mensaje: Texto del recordatorio
        tiempo: timedelta (relativo) o datetime (absoluto)
    
    Returns:
        (bool, str): (éxito, mensaje descriptivo)
    """
    url, key = _supa()
    if not url or not key:
        return False, "❌ Supabase no configurado"
    
    # Calcular timestamp
    if isinstance(tiempo, timedelta):
        recordar_en = datetime.now() + tiempo
        descripcion = f"en {tiempo}"
    elif isinstance(tiempo, datetime):
        recordar_en = tiempo
        descripcion = f"el {recordar_en.strftime('%d/%m/%Y a las %H:%M')}"
    else:
        return False, "❌ Tiempo inválido"
    
    try:
        r = requests.post(f"{url}/rest/v1/memories",
            headers={"apikey": key, "Authorization": f"Bearer {key}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={
                "user_id": str(user_id),
                "contenido": mensaje,
                "importancia": 2,
                "recordar_en": recordar_en.isoformat(),
                "enviado": False
            }, timeout=10)
        
        if r.status_code in (200, 201):
            return True, f"⏰ Programado {descripcion}"
        else:
            return False, f"❌ Error: {r.status_code}"
    except Exception as e:
        return False, f"❌ Error: {str(e)[:100]}"

def obtener_recordatorios_vencidos():
    """Obtiene recordatorios que ya vencieron y no fueron enviados.
    
    Returns:
        list: Lista de recordatorios vencidos
    """
    url, key = _supa()
    if not url or not key:
        return []
    
    ahora = datetime.now().isoformat()
    
    try:
        # Query: recordar_en <= ahora AND enviado = false
        r = requests.get(f"{url}/rest/v1/memories",
            params={
                "recordar_en": f"lte.{ahora}",
                "enviado": "eq.false",
                "order": "recordar_en.asc"
            },
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            timeout=10)
        
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        print(f"[recordatorios] error obteniendo vencidos: {e}")
        return []

def marcar_enviado(recordatorio_id):
    """Marca un recordatorio como enviado.
    
    Args:
        recordatorio_id: ID del recordatorio en Supabase
    
    Returns:
        bool: True si se actualizó correctamente
    """
    url, key = _supa()
    if not url or not key:
        return False
    
    try:
        r = requests.patch(f"{url}/rest/v1/memories?id=eq.{recordatorio_id}",
            headers={"apikey": key, "Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            json={"enviado": True},
            timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[recordatorios] error marcando enviado: {e}")
        return False

if __name__ == "__main__":
    print("=== TEST recordatorios ===\n")
    
    # Test parsear_tiempo
    print("Parseo de tiempos:")
    print(f"  2h -> {parsear_tiempo('2h')}")
    print(f"  30m -> {parsear_tiempo('30m')}")
    print(f"  1d -> {parsear_tiempo('1d')}")
    print(f"  14/03 -> {parsear_tiempo('14/03')}")
    print(f"  14/03 15:00 -> {parsear_tiempo('14/03 15:00')}")
    
    # Test programar (sin guardar realmente)
    print("\nProgramación (sin guardar):")
    tiempo = parsear_tiempo("2m")
    if tiempo:
        recordar_en = datetime.now() + tiempo
        print(f"  Recordatorio en {tiempo}: {recordar_en.strftime('%H:%M:%S')}")
    
    # Test obtener vencidos
    print("\nRecordatorios vencidos:")
    vencidos = obtener_recordatorios_vencidos()
    print(f"  Encontrados: {len(vencidos)}")
