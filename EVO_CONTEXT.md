
## 2026-09-23: Servidor MCP propio
- Archivo: ~/artemis-bridge/servidor_mcp.py
- Herramientas expuestas: tomar_foto, hablar, vibrar, linterna, obtener_gps, enviar_sms, ocr_imagen
- Protocolo: JSON-RPC sobre stdio (sin FastMCP, sin Rust)
- Test: bash test_mcp.sh (vibración exitosa)

## 2026-09-23: Reflexion funcionando
- Archivo: ~/artemis-bridge/reflexion.py
- Tabla: reflections (contexto, error, leccion, embedding vector(3072))
- Función SQL: match_reflections(query_emb, limite)
- Flujo: error → Groq analiza → extrae lección → Gemini embed → Supabase guarda → consulta semántica recupera
- Test exitoso: lección guardada y recuperada con similitud 0.76
