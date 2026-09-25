
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

## 2026-09-24 00:10: Manos ADB = NULO por ahora (heladera)
- adb pair Termux: bug binario arm64 (protocol fault), Google issue 329947334
- LADB v2.6 (checksum verificado OK): pairing no completa en A04, "shell is dead"
- Decision: no bloquear el organismo por manos; avanzar sin ellas
- Proximo intento (de dia): Shizuku (Play Store) o PC + copia de adbkey a Termux
- Leccion guardada en tabla reflections

## 2026-09-25 19:15: Migracion Render completada
- Cuenta vieja: proyecto borrado (limite free agotado)
- Cuenta nueva: Lumina's workspace
- URL nueva: https://evo-v9-god-mode.onrender.com
- 10 variables migradas, SIN BOT_TOKEN (bot vive en Termux por polling)
- Scripts locales actualizados a la URL nueva

## 2026-09-24 20:50: VISIÓN POR TELEGRAM OPERATIVA (cierre debugging 14h)

### Lo que se logró hoy:
- **Migración de Render**: cuenta vieja suspendida → cuenta nueva (Lumina's workspace) con horas free frescas
- **Bot 100% local**: polling en Termux, sin webhook, sin conflictos
- **Fix del guard `__main__`**: movido al final de app.py (estaba en línea 1594, bloqueando rutas posteriores)
- **Fix de URL de descarga**: `/file/bot<TOKEN>/` en vez de `/bot<TOKEN>/file/` (bug desde el día 1)
- **Validación de magic bytes**: el bot verifica que descargue imagen real, no JSON de error
- **Cadena de modelos actualizada**: gemini-3-flash-preview al frente (los otros están muertos)
- **Visión completa**: foto → Telegram → bot → Gemini → descripción → respuesta

### Bugs encontrados y resueltos:
1. Guard `if __name__ == "__main__": app.run()` en medio de app.py → rutas posteriores no se registraban
2. URL invertida para descarga de archivos de Telegram
3. Procesos zombie con código viejo en memoria
4. Modelos muertos en cadena de fallback

### Lecciones guardadas en Reflexion:
- Verificar rutas vivas con endpoint /rutas
- Validar magic bytes de descargas externas
- Matar procesos zombie antes de juzgar código
- Auditar cadenas de fallback contra modelos vivos
- Guardar foto cruda a disco para reproducir bugs por CLI

## 2026-09-24 20:50: VISIÓN POR TELEGRAM OPERATIVA (cierre debugging 14h)

### Lo que se logró hoy:
- **Migración de Render**: cuenta vieja suspendida → cuenta nueva con horas free
- **Bot 100% local**: polling en Termux, sin webhook
- **Fix guard __main__**: movido al final de app.py
- **Fix URL descarga**: /file/bot<TOKEN>/ en vez de /bot<TOKEN>/file/
- **Validación magic bytes**: verifica descargas reales
- **Cadena de modelos**: gemini-3-flash-preview al frente
- **Visión completa**: foto → Telegram → Gemini → descripción

### Lecciones en Reflexion:
- Verificar rutas con /rutas
- Validar magic bytes
- Matar zombies antes de juzgar código
- Auditar modelos vivos
- Guardar foto cruda para reproducir bugs

## 2026-09-25 12:30: MEMORIA PERSISTENTE OPERATIVA

### Lo que se logró:
- **Tabla memories en Supabase**: recuerdos de largo plazo con importancia y fecha
- **Módulo memoria_persistente.py**: guardar/buscar/listar recuerdos
- **Comandos del bot**:
  - `/remember <algo>` - guardar recuerdo manualmente
  - `/recall <busqueda>` - buscar recuerdos
  - `/memories` - ver últimos 10 recuerdos
- **Auto-captura**: frases que empiezan con "recordá que..." se guardan automáticamente
- **Inyección de contexto**: antes de cada respuesta, EVO busca recuerdos relevantes y los usa

### Bugs encontrados y resueltos:
1. Falta de SUPABASE_URL en .secrets
2. URL duplicada (.supabase.co.supabase.co)
3. Tabla memories no existía (creada manualmente en Supabase dashboard)
4. Fallback por palabras no limpiaba puntuación ("cumpleaños?" no matcheaba)
5. Funciones de memoria agregadas después del loop (nunca se ejecutaban)
6. Bloque de inyección de contexto con formato diferente al esperado

### Lección clave:
La memoria persistente transforma a EVO de un pez con memoria de 3 segundos a una criatura que recuerda cumpleaños, preferencias y datos importantes del usuario sin que se los pidan explícitamente.

### Estado actual del organismo:
- 👁️ Visión: operativa
- 🗣️ Voz: operativa
- 🧠 Memoria conversación: operativa (8 msgs)
- 🧠 Memoria persistente: operativa (Supabase)
- 🕷️ Web: operativa (búsqueda + lectura)
- 🤖 Razonamiento: operativo (Groq + Gemini)
- 🔄 Reflexión: operativa
