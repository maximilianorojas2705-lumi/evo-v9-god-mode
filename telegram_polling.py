#!/usr/bin/env python3
"""Bot de Telegram por polling (sin URL pública). Reemplaza al webhook muerto."""
import os, sys, time, requests, base64, json, traceback

# Cargar secrets
def _secrets():
    d = dict(os.environ)
    for ruta in ["~/artemis-bridge/.secrets", "~/.secrets"]:
        r = os.path.expanduser(ruta)
        if os.path.exists(r):
            for linea in open(r):
                if "=" in linea:
                    k, v = linea.split("=", 1)
                    d[k.strip()] = v.strip()
    return d

S = _secrets()
BOT = S.get("BOT_TOKEN", "").strip()
GROQ = S.get("GROQ_KEY", "").strip()
GEMINI = S.get("GEMINI_KEY", "").strip()
SUPA_URL = S.get("SUPABASE_URL", "")
SUPA_KEY = S.get("SUPABASE_KEY", "")

TELE = f"https://api.telegram.org/bot{BOT}"
VISION_LOCAL = "http://localhost:10000/vision"

if not BOT:
    print("❌ BOT_TOKEN no configurado"); sys.exit(1)

print(f"✅ Bot iniciado (polling mode)")
print(f"   Groq: {'sí' if GROQ else 'NO'} | Gemini: {'sí' if GEMINI else 'NO'}")
print(f"   Vision local: {VISION_LOCAL}")

# Importar el cerebro del app.py (sin Flask)
sys.path.insert(0, os.path.dirname(__file__))

# Funciones de respuesta
def enviar(chat_id, texto):
    try:
        requests.post(f"{TELE}/sendMessage", json={
            "chat_id": chat_id, "text": texto[:4000],
            "parse_mode": "Markdown"
        }, timeout=15)
    except Exception as e:
        print(f"[enviar] error: {e}")

def enviar_typing(chat_id):
    try:
        requests.post(f"{TELE}/sendChatAction", 
                      json={"chat_id": chat_id, "action": "typing"}, timeout=5)
    except: pass

def procesar_texto(chat_id, texto):
    """Pasa el mensaje al cerebro (Groq/Gemini)."""
    enviar_typing(chat_id)
    
    # Comando especial
    if texto.startswith("/"):
        if texto == "/start":
            return enviar(chat_id, "🧠 *EVO online* (modo local)\n\n"
                          "Hablame normal o usá:\n"
                          "/vision - mirar foto que mandes\n"
                          "/reflexion - ver lecciones aprendidas\n"
                          "/status - estado del organismo")
        if texto == "/status":
            return enviar(chat_id, "✅ Cerebro local vivo\n"
                          f"• Groq: {'✅' if GROQ else '❌'}\n"
                          f"• Gemini: {'✅' if GEMINI else '❌'}\n"
                          "• Visión: localhost:10000\n"
                          "• Modo: polling (sin Render)")
        if texto == "/reflexion":
            r = requests.get(f"{SUPA_URL}/rest/v1/reflections?order=creado_at.desc&limit=5",
                headers={"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}"},
                timeout=10)
            if r.status_code == 200:
                refs = r.json()
                if refs:
                    msg = "🔄 *Últimas lecciones:*\n\n"
                    for ref in refs:
                        msg += f"• {ref['leccion']}\n"
                    return enviar(chat_id, msg)
            return enviar(chat_id, "(sin lecciones aún)")
    
    # Mensaje normal → Groq
    if GROQ:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ}"},
                json={
                    "model": "openai/gpt-oss-120b",
                    "messages": [
                        {"role": "system", "content": "Sos EVO, un asistente con cuerpo físico en Termux. Respuestas concisas."},
                        {"role": "user", "content": texto}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.7
                }, timeout=30)
            if r.status_code == 200:
                resp = r.json()["choices"][0]["message"]["content"]
                return enviar(chat_id, resp)
            print(f"[groq] error {r.status_code}: {r.text[:100]}")
        except Exception as e:
            print(f"[groq] excepcion: {e}")
    
    # Fallback Gemini
    if GEMINI:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI}",
                json={"contents": [{"parts": [{"text": texto}]}]},
                timeout=30)
            if r.status_code == 200:
                resp = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return enviar(chat_id, resp)
        except Exception as e:
            print(f"[gemini] excepcion: {e}")
    
    enviar(chat_id, "⚠️ No pude procesar (Groq y Gemini fallaron)")

def procesar_foto(chat_id, file_id, caption):
    """Descarga la foto y la manda al endpoint /vision local."""
    enviar_typing(chat_id)
    
    try:
        # Descargar foto
        fi = requests.get(f"{TELE}/getFile", params={"file_id": file_id}, timeout=10).json()
        foto_bytes = requests.get(
            f"{TELE}/file/{fi['result']['file_path']}", timeout=25).content
        
        b64 = base64.b64encode(foto_bytes).decode()
        prompt = caption or "Describí lo que ves en una frase."
        
        # Llamar a visión local
        r = requests.post(VISION_LOCAL,
            json={"image": b64, "prompt": prompt},
            timeout=90)
        
        if r.status_code == 200:
            respuesta = r.json().get("answer", "(sin respuesta)")
            enviar(chat_id, f"👁️ {respuesta}")
        else:
            enviar(chat_id, f"❌ Vision fallo: {r.status_code}")
    
    except requests.exceptions.ConnectionError:
        enviar(chat_id, "❌ Cerebro local no responde (corré run_local.sh)")
    except Exception as e:
        enviar(chat_id, f"❌ Error: {str(e)[:200]}")

def procesar_audio(chat_id, file_id):
    """Descarga audio y lo transcribe con Groq whisper."""
    if not GROQ:
        return enviar(chat_id, "⚠️ Sin Groq, no puedo transcribir audio")
    
    enviar_typing(chat_id)
    try:
        fi = requests.get(f"{TELE}/getFile", params={"file_id": file_id}, timeout=10).json()
        audio_bytes = requests.get(
            f"{TELE}/file/{fi['result']['file_path']}", timeout=30).content
        
        # Groq Whisper
        r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ}"},
            files={"file": ("audio.ogg", audio_bytes, "audio/ogg")},
            data={"model": "whisper-large-v3", "language": "es"},
            timeout=60)
        
        if r.status_code == 200:
            texto = r.json().get("text", "")
            enviar(chat_id, f"🎙️ _{texto}_\n\nProcesando...")
            # Pasar el texto transcrito al cerebro
            return procesar_texto(chat_id, texto)
        enviar(chat_id, f"❌ Whisper fallo: {r.status_code}")
    except Exception as e:
        enviar(chat_id, f"❌ Error audio: {str(e)[:200]}")

# Loop principal: long polling
offset = 0
print("🔄 Escuchando mensajes (Ctrl+C para parar)...")
while True:
    try:
        r = requests.get(f"{TELE}/getUpdates",
            params={"offset": offset, "timeout": 30},
            timeout=40)
        
        if r.status_code != 200:
            print(f"[poll] error {r.status_code}"); time.sleep(5); continue
        
        data = r.json()
        if not data.get("ok"):
            print(f"[poll] no ok: {data}"); time.sleep(5); continue
        
        for update in data.get("result", []):
            offset = update["update_id"] + 1
            msg = update.get("message") or update.get("channel_post") or {}
            chat_id = (msg.get("chat") or {}).get("id")
            
            if not chat_id: continue
            
            try:
                if "photo" in msg:
                    # Foto: tomar la de mayor resolución (última)
                    file_id = msg["photo"][-1]["file_id"]
                    caption = msg.get("caption") or ""
                    procesar_foto(chat_id, file_id, caption)
                
                elif "voice" in msg or "audio" in msg:
                    file_id = (msg.get("voice") or msg.get("audio"))["file_id"]
                    procesar_audio(chat_id, file_id)
                
                elif "text" in msg:
                    procesar_texto(chat_id, msg["text"])
                
                else:
                    enviar(chat_id, "(tipo de mensaje no soportado aún)")
            
            except Exception as e:
                print(f"[proceso] error: {e}")
                traceback.print_exc()
                try: enviar(chat_id, f"⚠️ Error: {str(e)[:150]}")
                except: pass
    
    except KeyboardInterrupt:
        print("\n⏹️ Parando..."); break
    except requests.exceptions.Timeout:
        continue  # normal en long polling
    except Exception as e:
        print(f"[loop] error: {e}")
        time.sleep(5)
