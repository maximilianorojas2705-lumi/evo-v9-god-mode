"""Memoria persistente de largo plazo (capa Mem0-style sobre Supabase)."""
import os, requests

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

def guardar_recuerdo(user_id, contenido, importancia=1):
    url, key = _supa()
    if not url or not key:
        return False
    try:
        r = requests.post(f"{url}/rest/v1/memories",
            headers={"apikey": key, "Authorization": f"Bearer {key}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": str(user_id), "contenido": contenido,
                  "importancia": importancia}, timeout=10)
        return r.status_code in (200, 201)
    except Exception as e:
        print(f"[memoria] guardar fallo: {e}")
        return False

def _query(url, key, params):
    try:
        r = requests.get(f"{url}/rest/v1/memories", params=params,
            headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=10)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print(f"[memoria] query fallo: {e}")
        return []

def buscar_recuerdos(user_id, query, limit=5):
    """Frase completa primero; si no, palabra por palabra."""
    url, key = _supa()
    if not url or not key:
        return []
    rs = _query(url, key, {"user_id": f"eq.{user_id}",
                           "contenido": f"ilike.%{query}%",
                           "order": "importancia.desc,creado_at.desc", "limit": limit})
    if rs:
        return rs
    seen, out = set(), []
    for palabra in [p.strip("?!,.:;()[]{}\'\"") for p in query.split()]:
        if len(palabra) < 3:
            continue
        for rec in _query(url, key, {"user_id": f"eq.{user_id}",
                                     "contenido": f"ilike.%{palabra}%",
                                     "order": "importancia.desc,creado_at.desc", "limit": limit}):
            if rec["id"] not in seen:
                seen.add(rec["id"])
                out.append(rec)
        if len(out) >= limit:
            break
    return out[:limit]

def ultimos_recuerdos(user_id, limit=10):
    url, key = _supa()
    if not url or not key:
        return []
    return _query(url, key, {"user_id": f"eq.{user_id}",
                             "order": "creado_at.desc", "limit": limit})

if __name__ == "__main__":
    print("=== TEST memoria persistente ===")
    ok = guardar_recuerdo("test_cli", "Maxi prefiere mate amargo", importancia=2)
    print(f"guardar: {'✅' if ok else '❌'}")
    rs = buscar_recuerdos("test_cli", "mate")
    print(f"buscar 'mate': {len(rs)} resultados")
    ult = ultimos_recuerdos("test_cli", limit=3)
    print(f"ultimos: {len(ult)} recuerdos")
