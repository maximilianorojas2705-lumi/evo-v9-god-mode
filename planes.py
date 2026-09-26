"""Planes persistentes estilo Manus: sobreviven reinicios y caidas."""
import os, json, requests

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

def _headers(key):
    return {"apikey": key, "Authorization": f"Bearer {key}",
            "Content-Type": "application/json", "Prefer": "return=representation"}

def crear_plan(user_id, titulo, pasos):
    url, key = _supa()
    r = requests.post(f"{url}/rest/v1/planes", headers=_headers(key),
        json={"user_id": str(user_id), "titulo": titulo,
              "pasos": json.dumps(pasos), "paso_actual": 0,
              "estado": "en_progreso"}, timeout=10)
    return r.json()[0] if r.status_code in (200, 201) and r.json() else None

def planes_activos(user_id):
    url, key = _supa()
    r = requests.get(f"{url}/rest/v1/planes", headers=_headers(key),
        params={"user_id": f"eq.{user_id}", "estado": "eq.en_progreso",
                "order": "creado_at.asc"}, timeout=10)
    return r.json() if r.status_code == 200 else []

def obtener_plan(plan_id):
    url, key = _supa()
    r = requests.get(f"{url}/rest/v1/planes", headers=_headers(key),
        params={"id": f"eq.{plan_id}"}, timeout=10)
    return r.json()[0] if r.status_code == 200 and r.json() else None

def avanzar_plan(plan_id):
    plan = obtener_plan(plan_id)
    if not plan:
        return None
    pasos = json.loads(plan["pasos"])
    nuevo = plan["paso_actual"] + 1
    estado = "completado" if nuevo >= len(pasos) else "en_progreso"
    url, key = _supa()
    requests.patch(f"{url}/rest/v1/planes?id=eq.{plan_id}", headers=_headers(key),
        json={"paso_actual": nuevo, "estado": estado}, timeout=10)
    return obtener_plan(plan_id)

def vista_plan(plan):
    pasos = json.loads(plan["pasos"])
    i = plan["paso_actual"]
    lineas = [f"🗺️ *{plan['titulo']}* ({plan['estado']})\n"]
    for n, p in enumerate(pasos):
        marca = "✅" if n < i else ("👉" if n == i else "⬜")
        lineas.append(f"{marca} {p}")
    return "\n".join(lineas)

if __name__ == "__main__":
    print("=== TEST planes ===")
    p = crear_plan("test_cli", "Plan de prueba", ["paso uno", "paso dos", "paso tres"])
    print(f"creado: id={p['id'] if p else None}")
    if p:
        p = avanzar_plan(p["id"])
        print(vista_plan(p))
        p = avanzar_plan(p["id"]); p = avanzar_plan(p["id"])
        print(vista_plan(p))
