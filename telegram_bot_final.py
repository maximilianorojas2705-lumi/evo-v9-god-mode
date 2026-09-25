#!/usr/bin/env python3
import os, sys, time, requests, base64, json, traceback
from datetime import datetime

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

print("✅ Bot final iniciado")
print(f"   Groq: {'✅' if GROQ else '❌'} | Gemini: {'✅' if GEMINI else '❌'}")

contextos = {}

def enviar(chat_id, texto, parse_mode="Markdown"):
    try:
        requests.post(f"{TELE}/sendMessage", json={
            "chat_id": chat_id, "text": texto[:4000],
            "parse_mode": parse_mode
        }, timeout=10)
    except: pass

def enviar_typing(chat_id):
    try:
        requests.post(f"{TELE}/sendChatAction",
                      json={"chat_id": chat_id, "action": "typing"}, timeout=3)
    except: pass

def get_embedding(texto):
    if not GEMINI:
        return None
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={GEMINI}",
            json={"content": {"parts": [{"text": texto}]}},
            timeout=8)
        if r.status_code == 200:
            return r.json()["embedding"]["values"]
    except:
        pass
    return None

def guardar_memoria(chat_id, texto, tipo="mensaje"):
    emb = get_embedding(texto)
    if not emb or not SUPA_URL:
        return False
    try:
        r = requests.post(f"{SUPA_URL}/rest/v1/memoria_vec",
            headers={
                "apikey": SUPA_KEY,
                "Authorization": f"Bearer {SUPA_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "contenido": texto[:2000],
                "tipo": tipo,
                "chat_id": str(chat_id),
                "embedding": emb,
                "creado": datetime.now().isoformat()
            },
            timeout=8)
        return r.status_code in [200, 201]
    except:
        return False

def buscar_memoria(query, limit=3):
    emb = get_embedding(query)
    if not emb or not SUPA_URL:
        return []
    try:
        r = requests.post(f"{SUPA_URL}/rest/v1/rpc/match_memoria",
            headers={
                "apikey": SUPA_KEY,
                "Authorization": f"Bearer {SUPA_KEY}",
                "Content-Type": "application/json"
            },
            json={"query_embedding": emb, "match_count": limit},
            timeout=8)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def procesar_texto(chat_id, texto):
    enviar_typing(chat_id)
    if texto.startswith("/"):
        return procesar_comando(chat_id, texto)
    guardar_memoria(chat_id, texto, tipo="usuario")
    if chat_id not in contextos:
        contextos[chat_id] = []
    contextos[chat_id].append({"role": "user", "content": texto})
    if len(contextos[chat_id]) > 8:
        contextos[chat_id] = contextos[chat_id][-8:]
    recuerdos = buscar_memoria(texto, limit=3)
    contexto_memoria = ""
    if recuerdos:
        contexto_memoria = "Recuerdos relevantes:\n"
        for rec in recuerdos:
            contexto_memoria += f"- {rec['contenido'][:150]}\n"
    mensajes = [{
        "role": "system",
        "content": "Sos EVO, asistente con cuerpo en Termux. " + contexto_memoria
    }]
    mensajes.extend(contextos[chat_id])
    if GROQ:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ}"},
                json={
                    "model": "openai/gpt-oss-120b",
                    "messages": mensajes,
                    "max_tokens": 600,
                    "temperature": 0.7
                }, timeout=25)
            if r.status_code == 200:
                resp = r.json()["choices"][0]["message"]["content"]
                contextos[chat_id].append({"role": "assistant", "content": resp})
                guardar_memoria(chat_id, resp, tipo="asistente")
                return enviar(chat_id, resp)
        except:
            pass
    if GEMINI:
        try:
            prompt = contexto_memoria + "\n\nUsuario: " + texto
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=25)
            if r.status_code == 200:
                resp = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                contextos[chat_id].append({"role": "assistant", "content": resp})
                guardar_memoria(chat_id, resp, tipo="asistente")
                return enviar(chat_id, resp)
        except:
            pass
    enviar(chat_id, "⚠️ No pude procesar")

def procesar_comando(chat_id, texto):
    cmd = texto.split()[0].lower()
    if cmd == "/start":
        return enviar(chat_id,
            "🧠 *EVO completo*\n\n"
            "/memoria - recuerdos\n"
            "/reflexion - lecciones\n"
            "/status - estado\n"
            "/piensa <tema> - reflexion\n\n"
            "O hablame normal, recuerdo todo.")
    elif cmd == "/status":
        return enviar(chat_id,
            f"✅ Groq: {'✅' if GROQ else '❌'}\n"
            f"✅ Gemini: {'✅' if GEMINI else '❌'}\n"
            f"✅ Memoria: activa\n"
            f"✅ Contexto: {len(contextos.get(chat_id, []))} msgs")
    elif cmd == "/memoria":
        recuerdos = buscar_memoria("cosas importantes", limit=5)
        if recuerdos:
            msg = "🧠 *Recuerdos:*\n\n"
            for rec in recuerdos:
                msg += f"• {rec['contenido'][:100]}\n"
            return enviar(chat_id, msg)
        return enviar(chat_id, "(sin recuerdos)")
    elif cmd == "/reflexion":
        r = requests.get(f"{SUPA_URL}/rest/v1/reflections?order=creado_at.desc&limit=3",
            headers={"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}"},
            timeout=8)
        if r.status_code == 200 and r.json():
            msg = "🔄 *Lecciones:*\n\n"
            for ref in r.json():
                msg += f"• {ref['leccion'][:100]}\n"
            return enviar(chat_id, msg)
        return enviar(chat_id, "(sin lecciones)")
    elif cmd == "/piensa":
        tema = texto.replace("/piensa", "").strip()
        if not tema:
            return enviar(chat_id, "Uso: /piensa <tema>")
        if GROQ:
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ}"},
                    json={
                        "model": "openai/gpt-oss-120b",
                        "messages": [
                            {"role": "system", "content": "Reflexiona profundamente."},
                            {"role": "user", "content": f"Sobre: {tema}"}
                        ],
                        "max_tokens": 1000
                    }, timeout=30)
                if r.status_code == 200:
                    resp = r.json()["choices"][0]["message"]["content"]
                    return enviar(chat_id, f"🤔 *{tema}:*\n\n{resp}")
            except:
                pass
        enviar(chat_id, "⚠️ Error")
    else:
        enviar(chat_id, f"Comando desconocido: {cmd}")

def procesar_foto(chat_id, file_id, caption):
    enviar_typing(chat_id)
    try:
        fi = requests.get(f"{TELE}/getFile", params={"file_id": file_id}, timeout=8).json()
        foto = requests.get(f"{TELE}/file/{fi['result']['file_path']}", timeout=20).content
        b64 = base64.b64encode(foto).decode()
        r = requests.post(VISION_LOCAL,
            json={"image": b64, "prompt": caption or "Describi lo que ves"},
            timeout=60)
        if r.status_code == 200:
            data = r.json()
            resp = (data.get("answer") or data.get("respuesta") or
                    data.get("decision") or data.get("descripcion") or
                    str(data)[:300])
            enviar(chat_id, f"👁️ {resp}")
        else:
            enviar(chat_id, f"❌ Vision: {r.status_code}")
    except:
        enviar(chat_id, "❌ Error procesando foto")

def procesar_audio(chat_id, file_id):
    if not GROQ:
        return enviar(chat_id, "⚠️ Sin Groq")
    enviar_typing(chat_id)
    try:
        fi = requests.get(f"{TELE}/getFile", params={"file_id": file_id}, timeout=8).json()
        audio = requests.get(f"{TELE}/file/{fi['result']['file_path']}", timeout=25).content
        r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ}"},
            files={"file": ("a.ogg", audio, "audio/ogg")},
            data={"model": "whisper-large-v3", "language": "es"},
            timeout=40)
        if r.status_code == 200:
            texto = r.json().get("text", "")
            enviar(chat_id, f"🎙️ _{texto}_")
            return procesar_texto(chat_id, texto)
        enviar(chat_id, f"❌ Whisper: {r.status_code}")
    except:
        enviar(chat_id, "❌ Error audio")

offset = 0
print("🔄 Escuchando...")
while True:
    try:
        r = requests.get(f"{TELE}/getUpdates",
            params={"offset": offset, "timeout": 20},
            timeout=25)
        if r.status_code != 200:
            time.sleep(3); continue
        data = r.json()
        for update in data.get("result", []):
            offset = update["update_id"] + 1
            msg = update.get("message") or {}
            chat_id = (msg.get("chat") or {}).get("id")
            if not chat_id: continue
            try:
                if "photo" in msg:
                    procesar_foto(chat_id, msg["photo"][-1]["file_id"], msg.get("caption", ""))
                elif "voice" in msg or "audio" in msg:
                    procesar_audio(chat_id, (msg.get("voice") or msg.get("audio"))["file_id"])
                elif "text" in msg:
                    procesar_texto(chat_id, msg["text"])
            except Exception as e:
                print(f"[error] {e}")
                try: enviar(chat_id, f"⚠️ Error")
                except: pass
    except KeyboardInterrupt:
        break
    except:
        time.sleep(3)
