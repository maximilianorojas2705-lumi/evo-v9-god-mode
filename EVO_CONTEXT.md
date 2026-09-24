
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

## 2026-09-23 23:15: Visión funcionando
- Endpoint /vision en app.py (línea ~1598)
- Cadena de fallback de modelos Gemini: gemini-3.6-flash → gemini-flash-latest → gemini-3.5-flash → gemini-2.5-flash
- Test exitoso: STATUS 200, descripción precisa de imagen de prueba
- Anti-fragil: si un modelo muere, pregunta al siguiente automáticamente
- Lección aprendida: nunca hardcodear modelos (Groq mató llama-4-scout, Google mató 1.5-flash y 2.5-flash en el mismo día)
