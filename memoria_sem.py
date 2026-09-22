#!/usr/bin/env python3
"""Memoria semantica de EVO (version Render): embeddings Gemini + pgvector."""
import os, requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://eqddscjgvsphzizobyef.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "")

HEAD = {"apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"}

def embed(texto):
    r = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent",
        headers={"x-goog-api-key": GEMINI_KEY},
        json={"content": {"parts": [{"text": texto}]}}, timeout=30)
    if r.status_code != 200:
        return None
    return r.json()["embedding"]["values"]

def guardar(contenido, fuente="chat"):
    vec = embed(contenido)
    if vec is None:
        return False
    r = requests.post(f"{SUPABASE_URL}/rest/v1/memoria_vec", headers=HEAD,
                      json={"contenido": contenido, "fuente": fuente, "embedding": vec})
    return r.status_code in (200, 201)

def recordar(query, limite=3):
    vec = embed(query)
    if vec is None:
        return ""
    r = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/match_memoria", headers=HEAD,
                      json={"query_emb": vec, "limite": limite})
    if r.status_code != 200:
        return ""
    filas = r.json()
    return "\n".join(f"- {f['contenido']}" for f in filas)
