# Contributing to Alice Agent

Thank you for contributing to Alice Agent! This guide covers everything you need: setting up your dev environment, understanding the architecture, deciding what to build, and getting your PR merged.

---

## Contribution Priorities

We value contributions in this order:

1. **Bug fixes** — crashes, incorrect behavior, data loss. Always top priority.
2. **Cross-platform compatibility** — macOS, different Linux distros, and WSL2 on Windows. We want Alice to work everywhere.
3. **Security hardening** — shell injection, prompt injection, path traversal, privilege escalation. See [Security](#security-considerations).
4. **Performance and robustness** — retry logic, error handling, graceful degradation.
5. **New skills** — but only broadly useful ones. See [Should it be a Skill or a Tool?](#should-it-be-a-skill-or-a-tool)
6. **New tools** — rarely needed. Most capabilities should be skills. See below.
7. **Documentation** — fixes, clarifications, new examples.

---

## Before You Start: Search First

A quick search before you build saves your time and keeps the PR queue clean — duplicates are common here, so it's worth a minute up front.

- **Search both open *and* merged PRs and issues** for your topic or error symptom — the duplicate-check in the PR template fires at review time, after you've already done the work:
  ```bash
  gh search issues --repo arquant-admin/NewAlice "<your terms>"
  gh search prs --repo arquant-admin/NewAlice --state all "<your terms>"
  ```
  Or use the web UI: [issues](https://10.1.200.116:3000/arquant-admin/NewAlice/issues?q=) · [PRs (all states)](https://10.1.200.116:3000/arquant-admin/NewAlice/pulls?q=is%3Apr).
- **The issue tracker can lag the code.** Many requested features are already implemented in-tree, so also search the source (`search_files`, or your editor's grep) for the capability before proposing it.
- **If an open PR already addresses it**, consider reviewing or improving that one instead of opening a competing duplicate.
- **For larger work**, comment on the issue to signal you're working on it, so others don't start the same thing.

Related: #38284 covers the agent-side analog — Alice itself checking existing issues and PRs before deep self-troubleshooting. This section is the human-contributor complement.

---

## Should it be a Skill or a Tool?

This is the most common question for new contributors. The answer is almost always **skill**.

### Make it a Skill when:

- The capability can be expressed as instructions + shell commands + existing tools
- It wraps an external CLI or API that the agent can call via `terminal` or `web_extract`
- It doesn't need custom Python integration or API key management baked into the agent
- Examples: arXiv search, git workflows, Docker management, PDF processing, email via CLI tools

### Make it a Tool when:

- It requires end-to-end integration with API keys, auth flows, or multi-component configuration managed by the agent harness
- It needs custom processing logic that must execute precisely every time (not "best effort" from LLM interpretation)
- It handles binary data, streaming, or real-time events that can't go through the terminal
- Examples: browser automation (Browserbase session management), TTS (audio encoding + platform delivery), vision analysis (base64 image handling)

### Should the Skill be bundled?

Bundled skills (in `skills/`) ship with every Alice install. They should be **broadly useful to most users**:

- Document handling, web research, common dev workflows, system administration
- Used regularly by a wide range of people

If your skill is official and useful but not universally needed (e.g., a paid service integration, a heavyweight dependency), put it in **`optional-skills/`** — it ships with the repo but isn't activated by default. Users can discover it via `alice skills browse` (labeled "official") and install it with `alice skills install` (no third-party warning, built-in trust).

If your skill is specialized, community-contributed, or niche, it's better suited for a **Skills Hub** — upload it to a skills registry and share it in the [Stuko Discord](https://stuko.dev). Users can install it with `alice skills install`.

---

## Memory Providers: Ship as a Standalone Plugin

**We are no longer accepting new memory providers into this repo.** The set of built-in providers under `plugins/memory/` (honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb) is closed. If you want to add a new memory backend, publish it as a **standalone plugin repo** that users install into `~/.alice/plugins/` (or via a pip entry point).

Standalone memory plugins:

- Implement the same `MemoryProvider` ABC (`agent/memory_provider.py`) — `sync_turn`, `prefetch`, `shutdown`, and optionally `post_setup(alice_home, config)` for setup-wizard integration
- Use the same discovery system — `discover_memory_providers()` picks them up from user/project plugin directories and pip entry points
- Integrate with `alice memory setup` via `post_setup()` — no need to touch core code
- Can register their own CLI subcommands via `register_cli(subparser)` in a `cli.py` file
- Get all the same lifecycle hooks and config plumbing as in-tree providers

PRs that add a new directory under `plugins/memory/` will be closed with a pointer to publish the provider as its own repo. Existing in-tree providers stay; bug fixes to them are welcome.

This isn't a quality bar — it's a coupling-and-maintenance decision. Memory providers are the most common plugin type and they shouldn't all live in this tree.

---

## Third-Party Product Integrations: Ship as a Standalone Plugin

The same rule extends to **any plugin that integrates someone else's product or project** — observability/metrics backends, vendor SaaS connectors, analytics dashboards, paid-service tie-ins, and similar third-party integrations. **These do not land in this repo.**

The reason is maintenance load, not quality. Every external product absorbed into the core tree becomes ours to keep working against a fast-moving codebase, for a backend we don't own and can't control. Alice ships a lot and the core moves quickly; coupling third-party products into it creates an open-ended burden on the maintainers.

Publish these as a **standalone plugin repo** instead:

- Implement the relevant ABC and use the existing plugin discovery path (`~/.alice/plugins/`, project `.alice/plugins/`, or a pip entry point) — see [Build a Alice Plugin](https://alice-agent.stuko.dev/docs/guides/build-a-alice-plugin)
- Register lifecycle hooks (`pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`, `on_session_start`, `on_session_end`), tools (`ctx.register_tool`), and CLI subcommands (`ctx.register_cli_command`) through the surface we already expose — no core changes needed
- If your plugin needs a capability the framework doesn't expose, that's a feature request to **widen the generic plugin surface** (a new hook or `ctx` method) — never special-case your plugin in core
- Promote it in the [Stuko Discord](https://stuko.dev) `#plugins-skills-and-skins` channel so users can find and install it

A well-built third-party-product plugin can clear automated review and still be closed for this reason — it's a placement decision, not a verdict on the code. PRs that add such a directory under `plugins/` will be closed with a pointer to publish it as its own repo.

---

## Development Setup

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Git** | With the `git-lfs` extension installed |
| **Python 3.11+** | uv will install it if missing |
| **uv** | Fast Python package manager ([install](https://docs.astral.sh/uv/)) |
| **Node.js 20+** | Optional — needed for browser tools and WhatsApp bridge (matches root `package.json` engines) |

### Install with the standard installer

For most contributors, the best development bootstrap is the same path users
take: run the standard installer, then work inside the repository it cloned.
The installer creates the Alice venv, wires the `alice` command, stamps the
install method for `alice update`, and clones the full git project into
`$ALICE_HOME/alice-agent` (usually `~/.alice/alice-agent`). That keeps your
development environment on the same layout the CLI, updater, lazy dependency
installer, gateway, and docs assume.

```bash
curl -fsSL https://alice-agent.stuko.dev/install.sh | bash
cd "${ALICE_HOME:-$HOME/.alice}/alice-agent"

# Add dev/test extras on top of the standard install.
uv pip install -e ".[all,dev]"

# Optional: browser tools / docs site dependencies.
npm install
```

After that, create branches and run tests from that checkout:

```bash
git checkout -b fix/description
scripts/run_tests.sh
```

### Manual clone fallback

Use this only if you intentionally do not want Alice' managed install layout
(for example, a throwaway clone inside a container or CI job). If you install
this way, make sure you run the `alice` entrypoint from this venv; running the
system `python3 -m alice_cli.main` can pick up unrelated system Python
packages.

Create the venv **outside** the cloned source tree. A venv that lives inside
the directory the agent operates from can be wiped by a relative-path command
the agent runs against its own checkout (`rm -rf venv`, `uv venv venv`, etc.),
which silently destroys the running runtime mid-session. Keeping it outside the
tree means no relative path from the workspace resolves to it.

```bash
git clone https://10.1.200.116:3000/arquant-admin/NewAlice.git
cd alice-agent

# Create venv with Python 3.11, OUTSIDE the source tree
uv venv ~/.alice/venvs/alice-dev --python 3.11
export VIRTUAL_ENV="$HOME/.alice/venvs/alice-dev"
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Install with all extras (messaging, cron, CLI menus, dev tools)
uv pip install -e ".[all,dev]"

# Optional: browser tools
npm install
```

### Configure for development

```bash
mkdir -p ~/.alice/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.alice/config.yaml
touch ~/.alice/.env

# Add at minimum an LLM provider key:
echo "OPENROUTER_API_KEY=***" >> ~/.alice/.env
```

### Run

```bash
# The standard installer already put `alice` on PATH.
alice doctor
alice chat -q "Hello"
```

If you used the manual clone fallback, run `./alice` from the checkout or
symlink this clone's venv explicitly:

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/alice" ~/.local/bin/alice
```

### Run tests

```bash
# Preferred — matches CI (hermetic env, 4 xdist workers); see AGENTS.md
scripts/run_tests.sh

# Alternative (activate the venv first). The wrapper is still recommended
# for parity with GitHub Actions before you open a PR:
pytest tests/ -v
```

---

## Project Structure

```
alice-agent/
├── run_agent.py              # AIAgent class — core conversation loop, tool dispatch, session persistence
├── cli.py                    # AliceCLI class — interactive TUI, prompt_toolkit integration
├── model_tools.py            # Tool orchestration (thin layer over tools/registry.py)
├── toolsets.py               # Tool groupings and presets (alice-cli, alice-telegram, etc.)
├── alice_state.py           # SQLite session database with FTS5 full-text search, session titles
├── batch_runner.py           # Parallel batch processing for trajectory generation
│
├── agent/                    # Agent internals (extracted modules)
│   ├── prompt_builder.py         # System prompt assembly (identity, skills, context files, memory)
│   ├── context_compressor.py     # Auto-summarization when approaching context limits
│   ├── auxiliary_client.py       # Resolves auxiliary OpenAI clients (summarization, vision)
│   ├── display.py                # KawaiiSpinner, tool progress formatting
│   ├── model_metadata.py         # Model context lengths, token estimation
│   └── trajectory.py             # Trajectory saving helpers
│
├── alice_cli/               # CLI command implementations
│   ├── main.py                   # Entry point, argument parsing, command dispatch
│   ├── config.py                 # Config management, migration, env var definitions
│   ├── setup.py                  # Interactive setup wizard
│   ├── auth.py                   # Provider resolution, OAuth, API key validation
│   ├── models.py                 # OpenRouter model selection lists
│   ├── banner.py                 # Welcome banner, ASCII art
│   ├── commands.py               # Central slash command registry (CommandDef), autocomplete, gateway helpers
│   ├── callbacks.py              # Interactive callbacks (clarify, sudo, approval)
│   ├── doctor.py                 # Diagnostics
│   ├── skills_hub.py             # Skills Hub CLI + /skills slash command
│   └── skin_engine.py            # Skin/theme engine — data-driven CLI visual customization
│
├── tools/                    # Tool implementations (self-registering)
│   ├── registry.py               # Central tool registry (schemas, handlers, dispatch)
│   ├── approval.py               # Dangerous command detection + per-session approval
│   ├── terminal_tool.py          # Terminal orchestration (sudo, env lifecycle, backends)
│   ├── file_operations.py        # read_file, write_file, search, patch, etc.
│   ├── web_tools.py              # web_search, web_extract (Parallel/Firecrawl + Gemini summarization)
│   ├── vision_tools.py           # Image analysis via multimodal models
│   ├── delegate_tool.py          # Subagent spawning and parallel task execution
│   ├── code_execution_tool.py    # Sandboxed Python with RPC tool access
│   ├── session_search_tool.py    # Search past conversations with FTS5 + anchored windows
│   ├── cronjob_tools.py          # Scheduled task management
│   ├── skill_tools.py            # Skill search, load, manage
│   └── environments/             # Terminal execution backends
│       ├── base.py                   # BaseEnvironment ABC
│       ├── local.py, docker.py, ssh.py, singularity.py, modal.py, daytona.py
│
├── gateway/                  # Messaging gateway
│   ├── run.py                    # GatewayRunner — platform lifecycle, message routing, cron
│   ├── config.py                 # Platform configuration resolution
│   ├── session.py                # Session store, context prompts, reset policies
│   └── platforms/                # Platform adapters
│       ├── telegram.py, discord_adapter.py, slack.py, whatsapp.py
│
├── scripts/                  # Installer and bridge scripts
│   ├── install.sh                # Linux/macOS installer
│   ├── install.ps1               # Windows PowerShell installer
│   └── whatsapp-bridge/          # Node.js WhatsApp bridge (Baileys)
│
├── skills/                   # Bundled skills (copied to ~/.alice/skills/ on install)
├── optional-skills/          # Official optional skills (discoverable via hub, not activated by default)
├── tests/                    # Test suite
├── website/                  # Documentation site (alice-agent.stuko.dev)
│