# Contribuir a Alice Agent

¡Gracias por contribuir a Alice Agent! Esta guía cubre todo lo que necesitas: configurar tu entorno de desarrollo, entender la arquitectura, decidir qué construir y conseguir que tu PR sea aceptado.

---

## Prioridades de Contribución

Valoramos las contribuciones en este orden:

1. **Correcciones de errores** — bloqueos, comportamiento incorrecto, pérdida de datos. Siempre la máxima prioridad.
2. **Compatibilidad entre plataformas** — macOS, diferentes distribuciones de Linux y WSL2 en Windows. Queremos que Alice funcione en todas partes.
3. **Fortalecimiento de seguridad** — inyección de shell, inyección de prompts, traversal de rutas, escalada de privilegios. Ver [Consideraciones de Seguridad](#consideraciones-de-seguridad).
4. **Rendimiento y robustez** — lógica de reintento, manejo de errores, degradación elegante.
5. **Nuevas habilidades** — pero solo las ampliamente útiles. Ver [¿Debería ser una Habilidad o una Herramienta?](#debería-ser-una-habilidad-o-una-herramienta)
6. **Nuevas herramientas** — raramente necesarias. La mayoría de las capacidades deberían ser habilidades. Ver más abajo.
7. **Documentación** — correcciones, aclaraciones, nuevos ejemplos.

---

## ¿Debería ser una Habilidad o una Herramienta?

Esta es la pregunta más común para los nuevos colaboradores. La respuesta casi siempre es **habilidad**.

### Hazlo una Habilidad cuando:

- La capacidad se puede expresar como instrucciones + comandos de shell + herramientas existentes
- Envuelve una CLI externa o API que el agente puede llamar a través de `terminal` o `web_extract`
- No necesita integración personalizada de Python ni gestión de claves API integrada en el agente
- Ejemplos: búsqueda en arXiv, flujos de trabajo de git, gestión de Docker, procesamiento de PDF, email a través de herramientas CLI

### Hazlo una Herramienta cuando:

- Requiere integración de extremo a extremo con claves API, flujos de autenticación o configuración de múltiples componentes gestionada por el harness del agente
- Necesita lógica de procesamiento personalizada que debe ejecutarse con precisión en cada ocasión (no "mejor esfuerzo" de la interpretación del LLM)
- Maneja datos binarios, streaming o eventos en tiempo real que no pueden pasar por el terminal
- Ejemplos: automatización de navegador (gestión de sesiones Browserbase), TTS (codificación de audio + entrega en plataforma), análisis de visión (manejo de imágenes base64)

### ¿Debería la Habilidad estar incluida?

Las habilidades incluidas (en `skills/`) se envían con cada instalación de Alice. Deben ser **ampliamente útiles para la mayoría de los usuarios**:

- Manejo de documentos, investigación web, flujos de trabajo de desarrollo comunes, administración de sistemas
- Usadas regularmente por una amplia gama de personas

Si tu habilidad es oficial y útil pero no universalmente necesaria (ej., una integración de servicio de pago, una dependencia pesada), ponla en **`optional-skills/`** — se envía con el repositorio pero no está activada por defecto. Los usuarios pueden descubrirla a través de `alice skills browse` (etiquetada como "oficial") e instalarla con `alice skills install` (sin advertencia de terceros, confianza integrada).

Si tu habilidad es especializada, contribuida por la comunidad o de nicho, es mejor para un **Skills Hub** — súbela a un registro de habilidades y compártela en el [Discord de Stuko](https://stuko.dev). Los usuarios pueden instalarla con `alice skills install`.

---

## Proveedores de Memoria: Publicar como Plugin Independiente

**Ya no aceptamos nuevos proveedores de memoria en este repositorio.** El conjunto de proveedores integrados en `plugins/memory/` (honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb) está cerrado. Si quieres añadir un nuevo backend de memoria, publícalo como un **repositorio de plugin independiente** que los usuarios instalen en `~/.alice/plugins/` (o a través de un entry point de pip).

Los plugins de memoria independientes:

- Implementan el mismo ABC `MemoryProvider` (`agent/memory_provider.py`) — `sync_turn`, `prefetch`, `shutdown` y opcionalmente `post_setup(alice_home, config)` para integración con el asistente de configuración
- Usan el mismo sistema de descubrimiento — `discover_memory_providers()` los recoge desde directorios de plugins de usuario/proyecto y entry points de pip
- Se integran con `alice memory setup` a través de `post_setup()` — sin necesidad de tocar el código base
- Pueden registrar sus propios subcomandos CLI a través de `register_cli(subparser)` en un archivo `cli.py`
- Obtienen todos los mismos hooks de ciclo de vida y plomería de configuración que los proveedores incluidos en el árbol

Los PRs que añadan un nuevo directorio bajo `plugins/memory/` serán cerrados con un puntero para publicar el proveedor como su propio repositorio. Los proveedores en árbol existentes se mantienen; las correcciones de errores para ellos son bienvenidas.

Esto no es una barra de calidad — es una decisión de acoplamiento y mantenimiento. Los proveedores de memoria son el tipo de plugin más común y no deberían vivir todos en este árbol.

---

## Configuración del Desarrollo

### Prerequisitos

| Requisito | Notas |
|-----------|-------|
| **Git** | Con la extensión `git-lfs` instalada |
| **Python 3.11+** | uv lo instalará si falta |
| **uv** | Gestor de paquetes Python rápido ([instalar](https://docs.astral.sh/uv/)) |
| **Node.js 20+** | Opcional — necesario para herramientas de navegador y puente WhatsApp (coincide con los engines de `package.json` raíz) |

### Clonar e instalar

```bash
git clone https://10.1.200.116:3000/arquant-admin/NewAlice.git
cd alice-agent

# Crear venv con Python 3.11
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# Instalar con todos los extras (mensajería, cron, menús CLI, herramientas de desarrollo)
uv pip install -e ".[all,dev]"

# Opcional: herramientas de navegador
npm install
```

### Configurar para desarrollo

```bash
mkdir -p ~/.alice/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.alice/config.yaml
touch ~/.alice/.env

# Añadir al menos una clave de proveedor LLM:
echo "OPENROUTER_API_KEY=***" >> ~/.alice/.env
```

### Ejecutar

```bash
# Enlace simbólico para acceso global
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/alice" ~/.local/bin/alice

# Verificar
alice doctor
alice chat -q "Hola"
```

### Ejecutar tests

```bash
# Preferido — coincide con CI (entorno hermético, 4 workers xdist); ver AGENTS.md
scripts/run_tests.sh

# Alternativa (activa el venv primero). El wrapper sigue recomendándose
# para paridad con GitHub Actions antes de abrir un PR:
pytest tests/ -v
```

---

## Estructura del Proyecto

```
alice-agent/
├── run_agent.py              # Clase AIAgent — bucle de conversación central, despacho de herramientas, persistencia de sesión
├── cli.py                    # Clase AliceCLI — TUI interactiva, integración prompt_toolkit
├── model_tools.py            # Orquestación de herramientas (capa delgada sobre tools/registry.py)
├── toolsets.py               # Agrupaciones y presets de herramientas (alice-cli, alice-telegram, etc.)
├── alice_state.py           # Base de datos de sesiones SQLite con búsqueda de texto completo FTS5, títulos de sesión
├── batch_runner.py           # Procesamiento en lote paralelo para generación de trayectorias
│
├── agent/                    # Internos del agente (módulos extraídos)
│   ├── prompt_builder.py         # Ensamblaje del prompt del sistema (identidad, habilidades, archivos de contexto, memoria)
│   ├── context_compressor.py     # Auto-resumición al acercarse a los límites de contexto
│   ├── auxiliary_client.py       # Resuelve clientes OpenAI auxiliares (resumición, visión)
│   ├── display.py                # KawaiiSpinner, formateo del progreso de herramientas
│   ├── model_metadata.py         # Longitudes de contexto del modelo, estimación de tokens
│   └── trajectory.py             # Ayudantes para guardar trayectorias
│
├── alice_cli/               # Implementaciones de comandos CLI
│   ├── main.py                   # Punto de entrada, análisis de argumentos, despacho de comandos
│   ├── config.py                 # Gestión de configuración, migración, definiciones de variables de entorno
│   ├── setup.py                  # Asistente de configuración interactivo
│   ├── auth.py                   # Resolución de proveedor, OAuth, validación de clave API
│   ├── models.py                 # Listas de selección de modelos de OpenRouter
│   ├── banner.py                 # Banner de bienvenida, arte ASCII
│   ├── commands.py               # Registro central de comandos de barra (CommandDef), autocompletado, ayudantes del gateway
│   ├── callbacks.py              # Callbacks interactivos (aclarar, sudo, aprobación)
│   ├── doctor.py                 # Diagnósticos
│   ├── skills_hub.py             # CLI del Skills Hub + comando de barra /skills
│   └── skin_engine.py            # Motor de skins/temas — personalización visual de CLI basada en datos
│
├── tools/                    # Implementaciones de herramientas (auto-registradas)
│   ├── registry.py               # Registro central de herramientas (esquemas, manejadores, despacho)
│   ├── approval.py               # Detección de comandos peligrosos + aprobación por sesión
│   ├── terminal_tool.py          # Orquestación del terminal (sudo, ciclo de vida del entorno, backends)
│   ├── file_operations.py        # read_file, write_file, búsqueda, patch, etc.
│   ├── web_tools.py              # web_search, web_extract (Paralelo/Firecrawl + resumición Gemini)
│   ├── vision_tools.py           # Análisis de imágenes a través de modelos multimodales
│   ├── delegate_tool.py          # Lanzamiento de subagentes y ejecución paralela de tareas
│   ├── code_execution_tool.py    # Python sandboxado con acceso a herramientas vía RPC
│   ├── session_search_tool.py    # Búsqueda en conversaciones pasadas con FTS5 + ventanas ancladas
│   ├── cronjob_tools.py          # Gestión de tareas programadas
│   ├── skill_tools.py            # Búsqueda, carga y gestión de habilidades
│   └── environments/             # Backends de ejecución del terminal
│       ├── base.py                   # ABC BaseEnvironment
│       ├── local.py, docker.py, ssh.py, singularity.py, modal.py, daytona.py
│
├── gateway/                  # Gateway de mensajería
│   ├── run.py                    # GatewayRunner — ciclo de vida de plataformas, enrutamiento de mensajes, cron
│   ├── config.py                 # Resolución de configuración de plataformas
│   ├── session.py                # Almacén de sesiones, prompts de contexto, políticas de reset
│   └── platforms/                # Adaptadores de plataformas
│       ├── telegram.py, discord_adapter.py, slack.py, whatsapp.py
│
├── scripts/                  # Scripts del instalador y puente
│   ├── install.sh                # Instalador Linux/macOS
│   ├── install.ps1               # Instalador Windows PowerShell
│   └── whatsapp-bridge/          # Puente WhatsApp Node.js (Baileys)
│
├── skills/                   # Habilidades incluidas (copiadas a ~/.alice/skills/ en la instalación)
├── optional-skills/          # Habilidades opcionales oficiales (descubribles vía hub, no activadas por defecto)
├── tests/                    # Suite de tests
├── website/                  # Sitio de documentación (alice-agent.stuko.dev)
│
├── cli-config.yaml.example   # Configuración de ejemplo (copiada a ~/.alice/config.yaml)
└── AGENTS.md                 # Guía de desarrollo para asistentes de codificación IA
```

### Configuración del usuario (almacenada en `~/.alice/`)

| Ruta | Propósito |
|------|-----------|
| `~/.alice/config.yaml` | Configuración (modelo, terminal, toolsets, compresión, etc.) |
| `~/.alice/.env` | Claves API y secretos |
| `~/.alice/auth.json` | Credenciales OAuth |
| `~/.alice/skills/` | Todas las habilidades activas (incluidas + instaladas desde hub + creadas por el agente) |
| `~/.alice/memories/` | Memoria persistente (MEMORY.md, USER.md) |
| `~/.alice/state.db` | Base de datos de sesiones SQLite |
| `~/.alice/sessions/` | Índice de enrutamiento del gateway (`sessions.json`), migas de pan de solicitudes, transcripciones `*.jsonl` del gateway y (opcionalmente) snapshots JSON por sesión cuando `sessions.write_json_snapshots: true` está configurado. Los snapshots por sesión están desactivados por defecto; state.db es canónica. |
| `~/.alice/cron/` | Datos de trabajos programados |
| `~/.alice/whatsapp/session/` | Credenciales del puente WhatsApp |

---

## Descripción General de la Arquitectura

### Bucle Central

```
Mensaje del usuario → AIAgent._run_agent_loop()
  ├── Construir prompt del sistema (prompt_builder.py)
  ├── Construir kwargs de API (modelo, mensajes, herramientas, configuración de razonamiento)
  ├── Llamar al LLM (API compatible con OpenAI)
  ├── Si tool_calls en la respuesta:
  │     ├── Ejecutar cada herramienta a través del despacho del registro
  │     ├── Añadir resultados de herramientas a la conversación
  │     └── Volver a la llamada al LLM
  ├── Si respuesta de texto:
  │     ├── Persistir sesión en DB
  │     └── Devolver final_response
  └── Compresión de contexto si se acerca al límite de tokens
```

### Patrones de Diseño Clave

- **Herramientas auto-registradas**: Cada archivo de herramienta llama a `registry.register()` en el momento de importación. `model_tools.py` activa el descubrimiento importando todos los módulos de herramientas.
- **Agrupación en toolsets**: Las herramientas se agrupan en toolsets (`web`, `terminal`, `file`, `browser`, etc.) que pueden habilitarse/deshabilitarse por plataforma.
- **Persistencia de sesión**: Todas las conversaciones se almacenan en SQLite (`alice_state.py`) con búsqueda de texto completo y títulos de sesión únicos.
- **Inyección efímera**: Los prompts del sistema y los mensajes de relleno se inyectan en el momento de la llamada API, nunca se persisten en la base de datos ni en los logs.
- **Abstracción de proveedor**: El agente funciona con cualquier API compatible con OpenAI. La resolución del proveedor ocurre en el momento de la inicialización.
- **Enrutamiento de proveedor**: Al usar OpenRouter, `provider_routing` en config.yaml controla la selección del proveedor.

---

## Estilo de Código

- **PEP 8** con excepciones prácticas (no imponemos longitud de línea estricta)
- **Comentarios**: Solo cuando se explica la intención no obvia, compromisos o peculiaridades de API. No narres lo que hace el código
- **Manejo de errores**: Captura excepciones específicas. Registra con `logger.warning()`/`logger.error()` — usa `exc_info=True` para errores inesperados
- **Multiplataforma**: Nunca asumas Unix. Ver [Compatibilidad Multiplataforma](#compatibilidad-multiplataforma)

---

## Añadir una Nueva Herramienta

Antes de escribir una herramienta, pregúntate: [¿debería ser una habilidad en su lugar?](#debería-ser-una-habilidad-o-una-her