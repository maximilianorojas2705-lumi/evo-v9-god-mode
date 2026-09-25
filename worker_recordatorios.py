"""Worker que revisa recordatorios vencidos cada minuto."""
import time, requests, os
from datetime import datetime
from recordatorios import obtener_recordatorios_vencidos, marcar_enviado

def _secrets():
    secrets = {}
    for ruta in ["~/artemis-bridge/.secrets", "~/.secrets"]:
        r = os.path.expanduser(ruta)
        if os.path.exists(r):
            for linea in open(r):
                if "=" in linea:
                    k, v = linea.split("=", 1)
                    secrets[k.strip()] = v.strip()
    return secrets

def enviar_telegram(chat_id, texto):
    """Envía mensaje por Telegram."""
    secrets = _secrets()
    bot_token = secrets.get("BOT_TOKEN", "")
    if not bot_token:
        print(f"[worker] ❌ BOT_TOKEN no encontrado")
        return False
    
    try:
        r = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": f"⏰ *Recordatorio*\\n\\n{texto}",
                  "parse_mode": "Markdown"}, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[worker] error enviando telegram: {e}")
        return False

def procesar_recordatorios():
    """Procesa todos los recordatorios vencidos."""
    vencidos = obtener_recordatorios_vencidos()
    
    if not vencidos:
        return 0
    
    procesados = 0
    for rec in vencidos:
        chat_id = rec.get("user_id")
        mensaje = rec.get("contenido")
        rec_id = rec.get("id")
        
        print(f"[worker] {datetime.now().strftime('%H:%M:%S')} - Enviando recordatorio a {chat_id}: {mensaje[:50]}...")
        
        if enviar_telegram(chat_id, mensaje):
            if marcar_enviado(rec_id):
                procesados += 1
                print(f"[worker] ✅ Recordatorio {rec_id} enviado y marcado")
            else:
                print(f"[worker] ⚠️ Recordatorio enviado pero no marcado")
        else:
            print(f"[worker] ❌ Error enviando recordatorio {rec_id}")
    
    return procesados

if __name__ == "__main__":
    print("🕐 Worker de recordatorios iniciado")
    print("   Revisando cada 60 segundos...")
    print("   Ctrl+C para detener\n")
    
    try:
        while True:
            procesados = procesar_recordatorios()
            if procesados > 0:
                print(f"[worker] {datetime.now().strftime('%H:%M:%S')} - {procesados} recordatorios procesados")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[worker] Detenido por el usuario")
