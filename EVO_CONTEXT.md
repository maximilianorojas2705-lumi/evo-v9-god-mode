
## 2026-09-23: Servidor MCP propio
- Archivo: ~/artemis-bridge/servidor_mcp.py
- Herramientas expuestas: tomar_foto, hablar, vibrar, linterna, obtener_gps, enviar_sms, ocr_imagen
- Protocolo: JSON-RPC sobre stdio (sin FastMCP, sin Rust)
- Test: bash test_mcp.sh (vibración exitosa)
