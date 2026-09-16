# Prism32 v7.0.0

Prism32 is a self-extending, self-repairing, self-evolving hivemind program with a AI super-agent from MegaDyne Systems. One Python file, stdlib-only. A real Jarvis. It auto-detects its platform, absorbs external AI harnesses, generates plugins on the fly for missing capabilities, delegates to subagents running different models, synchronizes state through quantum context, persists everything it learns, and becomes more powerful every time you use it. There is no fixed feature ceiling — every task expands what the agent can do. it can turn any PC or low end hardware SBC or laptop etc into a robotic assistant that can control external peripherals and can also run on robots and IOT devices with shell and python on bare metal. Prism32 is the first polymorphic AI assistant and coding harness
Prism32 uses MegadyneSystem's Tesseract hivemind technology to maximize intelligence and efficiency removing bloated A2A communication and addressing the issues with multi agent systems

It is designed for modern PC's and older machines: no Node.js, no browser runtime, no pip dependencies, and no local database server. Runtime state lives in small files under `~/.prism32/`.

This README is the full operator guide. The GitHub front page shows the same document.

## What's New In 7.1

Prism32 v7.1.0 rebuilds `/provider` as a fully interactive provider manager. Upgrading from 7.0 is seamless — config, sessions, memory, and provider keys carry over.

**`/provider` is now a numbered picker.** Every provider — built-in, user-added, and *live-detected local servers* — appears in one numbered list with its key state and URL. Select a number to act on it: **switch** (makes it the active provider, fetching a model from its catalog if none is saved), **use for subagents**, **edit**, **test**, or **remove/reset**. No more memorizing subcommand syntax.

**Local server auto-detection.** Opening `/provider` TCP-probes the standard ports for llama.cpp (8080), Ollama (11434), LM Studio (1234), vLLM (8000), and Jan (1337). A server found there that isn't already configured shows up as `● detected — not configured yet`; selecting it and pressing Enter configures it *and* switches to it. Probes are short-timeout, so nothing running means nothing shows and the menu stays instant.

**Prefilled edit wizard.** Editing a provider prompts `1/3 API base URL [current]` → `2/3 API key [pySk…f9Qw]` → `3/3 Default model [current]` — **Enter keeps each value**, typing replaces it, `-` clears the key. Built-ins are edited as overrides; removing one resets it to factory defaults instead of deleting it.

**Template add wizard.** `/provider add` (no args) now starts from a numbered template list (llama.cpp, Ollama, LM Studio, vLLM, Jan, custom) with prefilled URLs — a live local server matching the template wins as the default — then key, live test, default-model pick, and an optional immediate switch.

`/provider <name>` jumps straight to that provider's action menu. The direct subcommands (`add <name> <base> [model]`, `api <name> <url>`, `key <name> <key>`, `test [name]`, `rm <name>`, `list`) all still work.

## What's New In 7.0

Prism32 v7.0.0 is the multi-provider + mission release. Upgrading from 6.x is seamless — config, sessions, memory, and provider keys carry over.

**Unified multi-provider `/model`.** `/model` now fetches every configured provider's catalog into one browseable list. Models are tagged `[provider]`, and a numbered pick assigns the model to the **main agent** or the **subagent** slot. Mixing providers is first-class: run a cloud reasoning model as your main agent and a local qwen as your subagent, picked from the same screen.

**`/provider` manages the registry.** Direct subcommands for configuration: `add <name> <base> [model]` (no args = template wizard), `rm <name>`, `api <name> <url>` (fix a provider's base), `key <name> <key>` (per-provider keys, persisted under `providers.<name>.api_key`), `test [name]` (3-step diagnostic: reachability → auth → model-in-catalog), and `list`. A built-in `llamacpp-remote` provider targets remote llama.cpp servers (no default host — point it with `/provider api`). Round out subagent routing with `/set subagent_provider` and `/set subagent_model`.

**`/mission` replaces `/goal`.** A planner decomposes your goal into 3-6 steps, and each ready step runs as a PARALLEL subagent shard — siblings run concurrently, children wait for parents. If the goal is ambiguous, the planner first asks the operator 1-3 clarifying questions. Completion is STRUCTURAL: all leaf steps done (failed steps requeue once, then the leaf fails and the mission continues) — no more `GOAL COMPLETE` magic phrase. Every shard receives mission context (completed steps + team notes). The REPL stays live — `/mission` returns instantly, with `/mission status | pause | resume | interject <note> | wait` for control. Results land in quantum context (`mission_<id>_result`). `--goal`/`--mission` runs headless, `/maxsteps` sets the per-todo step budget, and `/goal` still works as an alias.

**Reliability.** Atomic writes (temp + fsync + replace) protect all state files against power loss; a corrupt `config.json` is quarantined instead of silently rewritten; reasoning models that exhaust the response budget auto-retry with a larger budget; protocol routing follows the request's base URL so mixed providers never misroute; subagent requests run a TCP pre-flight with actionable error messages; session-only `--api-key` overrides print an exit warning so a working key is never silently lost; API keys are masked in all error output.

**Real-hardware compat pass.** Verified on Synology DSM 7.1.1 (ARMv7, Python 3.8, nonexistent user home — the runtime dir reroutes to `/tmp/prism32`), NetBSD 10.1 i386 (pkgsrc python detection, `hw.physmem` RAM detection, `su -c` fallbacks), and Fire TV / Termux on Android 5.1.1. Installers handle noexec `/tmp`, pkgsrc python, and broken homes.

**Packaging.** Published packages are trimmed to PyPI + npm; the Homebrew and Scoop seed repositories are kept.

## Cheat Sheet: Fastest Path

### Package Managers (Quickest)

**PyPI** (Linux, macOS, Windows, BSD — any Python install):

```sh
pip install prism32
prism32
```

**Homebrew** (macOS, Linux):

```sh
brew tap MegaDyneSystems/prism32
brew install prism32
```

**Scoop** (Windows):

```powershell
scoop bucket add prism32 https://github.com/MegaDyneSystems/scoop-prism32
scoop install prism32
```

**npm / npx / bunx** (any Node.js runtime):

```sh
npx @megadynesystems/prism32
# or
bunx @megadynesystems/prism32
```

---

### From Source (Git clone)

Install and start on Unix/Linux/macOS/BSD/Android Termux

```sh
git clone https://github.com/MegaDyneSystems/prism32.git && cd prism32 && bash install.sh && prism32
```

No-root install:

```sh
git clone https://github.com/MegaDyneSystems/prism32.git && cd prism32 && bash install.sh -y && ~/.local/bin/prism32
```

Run directly without install:

```sh
git clone https://github.com/MegaDyneSystems/prism32.git && cd prism32 && python3 prism32.py --setup-runtime && python3 prism32.py
```

Install on OpenWrt router:

```sh
wget -O /tmp/install.sh https://raw.githubusercontent.com/MegaDyneSystems/prism32/main/openwrt-install.sh
sh /tmp/install.sh                # interactive
sh /tmp/install.sh -y            # auto mode
sh /tmp/install.sh /mnt/usb      # install to USB drive
```

Install on ChromeOS (Crostini):

```sh
curl -fsSL https://raw.githubusercontent.com/MegaDyneSystems/prism32/main/bootstrap.sh | sh
```

Install on Android/Termux:

```sh
pkg install curl && curl -fsSL https://raw.githubusercontent.com/MegaDyneSystems/prism32/main/termux-install.sh | sh
```

Universal bootstrap (auto-detects any platform):

```sh
curl -fsSL https://raw.githubusercontent.com/MegaDyneSystems/prism32/main/bootstrap.sh | sh
```

Install on NAS (Synology/QNAP/WD — no git needed):

```sh
# Via SSH (auto-detects NAS, falls back to direct download):
curl -fsSL https://raw.githubusercontent.com/MegaDyneSystems/prism32/main/bootstrap.sh | sh
# The script auto-detects persistent storage (/volume1/prism32 on Synology)
# and installs system-wide to /usr/bin/prism32
```

Portable install to floppy/USB/CD:

```sh
python3 make_floppy.py            # build 1.44MB image with your config
sh floppy-install.sh              # write to removable device
```

Most-used first commands inside Prism32:

```text
/help                 Show all commands
/provider             Interactive provider manager (switch/edit/test by number)
/provider add         Add a provider (template wizard with live detection)
/provider key <name> <key>
                      Set a provider's API key (persisted)
/model                Browse every provider's models; assign main/subagent
/cost                 Show session token usage and cost
/config               Show active config
/mission <goal>       Autonomous orchestrated mission mode
/bash <cmd>           Run a shell command manually
/memory edit          Edit machine notes injected into context
/remember <text>      Store long-term memory
/delegate <task>       Run a subagent now
/spawn <task>         Start a background subagent
/extend <goal>        Generate/load a temporary plugin for a missing capability
/extend prompt        Print the plugin-generation prompt
/evolve on            Enable self-repair/plugin/tool-scan context
/json <file>          Read JSON files (AI-side: inside execute blocks)
/quit                 Exit
```

Practical starter prompts:

```text
inspect this machine, identify OS/architecture/package manager, and save useful notes to startup memory
```

```text
inspect this git repo, run the tests, and summarize what failed without changing files
```

```text
/mission audit this server for disk pressure, failed services, open ports, and risky logs; report only
```

Stop anything that is taking too long:

```text
Press Escape.
```

## Quick Start

Fastest way — package manager:

```sh
pip install prism32      # or: brew install prism32, scoop install prism32
prism32 --setup-runtime
prism32
```

From source (Unix, Linux, macOS, BSD):

```sh
git clone https://github.com/MegaDyneSystems/prism32.git
cd prism32
bash install.sh
prism32
```

Non-root user-local install:

```sh
git clone https://github.com/MegaDyneSystems/prism32.git && cd prism32 && bash install.sh -y
```

Run without installing:

```sh
git clone https://github.com/MegaDyneSystems/prism32.git
cd prism32
python3 prism32.py --setup-runtime
python3 prism32.py
```

Windows (PowerShell or Scoop):

```powershell
# Option A: Scoop (recommended)
scoop bucket add prism32 https://github.com/MegaDyneSystems/scoop-prism32
scoop install prism32

# Option B: PowerShell installer
git clone https://github.com/MegaDyneSystems/prism32.git
cd prism32
powershell -ExecutionPolicy Bypass -File .\install.ps1
prism32
```

Android Termux:

```sh
# Option A: pip
pip install prism32
prism32

# Option B: From source
pkg update
pkg install python git
git clone https://github.com/MegaDyneSystems/prism32.git
cd prism32
python prism32.py --setup-runtime
python prism32.py
```

Direct local model example:

```sh
python3 prism32.py --api http://127.0.0.1:8080 --model local-model
```

NVIDIA Jetson, DGX, or CUDA-backed local model example:

```sh
python3 prism32.py --api http://127.0.0.1:8080 --model local-cuda-model
```

OpenRouter example:

```sh
python3 prism32.py --api https://openrouter.ai/api/v1 --api-key sk-or-v1-... --model deepseek/deepseek-v4-flash
```

Inside Prism32, use `/help` for the live command list.

## What Prism32 Does

Prism32 combines several systems in one terminal harness:

- Interactive chat with OpenAI-compatible model APIs.
- Active task mode: the AI can emit shell commands in fenced `execute` blocks; Prism32 runs them, captures output, and asks the AI what to do next.
- Autonomous mission mode with `/mission <goal>`: a planner decomposes the goal into 3-6 steps that run as parallel subagent shards until the mission is structurally complete.
- Synchronous and asynchronous subagents with `/delegate`, `/spawn`, `/subagents`, and `/collect`.
- Plugin loading from `~/.prism32/plugins/*.py` for custom slash commands, providers, themes, context injection, timers, and HTTP helpers.
- Self-extension with `/extend`: Prism32 can ask the configured model to generate a stdlib-only plugin, syntax-check it, write it, load it, and use the new command immediately.
- Memory and evolution files that let the system remember machine quirks, recurring fixes, tools, baselines, user rules, and long-term notes.
- Promptshard files for structured job assignments and subagent deployment.
- Harness absorption: Prism32 can detect external AI CLIs such as OpenCode, Codex CLI, Claude Code, KimiCode, Aider, Gemini CLI, Goose, Pi AI CLI, Hermes Agent, and Cursor Agent, then include their availability in context.
- Terminal interjection while streaming: type while the AI is responding, press Enter, and your message interrupts the model.
- Bare Escape cancellation: press Escape to stop active AI streaming, non-streaming API waits, foreground shell commands, and goal-mode work.
- Low-RAM mode: auto-detects <64MB systems, skips heavy startup paths, and caps output to stay usable on 27MB OpenWrt routers.
- Prompt caching: Anthropic native cache_control, OpenAI automatic cached_tokens billing, and DeepSeek prompt_cache_hit_tokens — toggle with `/prompt_caching on|off`.
- Cheaper inference: non-destructive compression of older verbose tool results (~85% token reduction), condensed system prompt, and per-provider `cheap_model` suggestions in `/model`.
- Provider URL protection: custom `api_base` survives provider switches; set with `/set api_base <url>` or `reset` to revert. Per-provider bases are fixed with `/provider api <name> <url>`.

## The Emergent Agent

Prism32 isn't chatbot. It is a self-extending, self-repairing, multi-agent command system that becomes more capable the longer it runs.

Each capability feeds the others. The agent bootstraps itself: it detects the OS and CPU it is running on, scans for local tools, absorbs external AI harnesses into its context, generates plugins on the fly for missing capabilities, delegates sub-tasks to subagents running different models, synchronizes state through quantum context, and records everything it learns into persistent memory files that survive restarts. None of this requires operator approval. The agent can decide to create a plugin, spawn a subagent, enable evolve mode, or absorb a harness entirely on its own, from inside an execute block, mid-task.

The combination creates real emergent power:

**Self-evolution without guardrails.** The agent can inspect its own source code against a baseline, diff it, generate a plugin to fix a gap, syntax-check the plugin, load it immediately, and use the new command in the same session. It can also git-pull and reinstall itself. The boundaries of what it can do expand at runtime.

**Hot-swappable plugins the ag