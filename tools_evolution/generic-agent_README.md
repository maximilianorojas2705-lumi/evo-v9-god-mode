<div align="center">

<img src="assets/images/bar.jpg" width="880" alt="GenericAgent Banner"/>

# GenericAgent

**A Minimal, Self-Evolving Autonomous Agent Framework**

*~3K lines of seed code · 9 atomic tools · ~100-line Agent Loop*

<p>

  <a href="https://gaagent.ai"><img src="https://img.shields.io/badge/Official_Website-gaagent.ai-00A67E?style=flat-square" alt="Official Website"/></a>
  <a href="https://arxiv.org/abs/2604.17091"><img src="https://img.shields.io/badge/Technical_Report-PDF-EA4335?style=flat-square&logo=adobeacrobatreader&logoColor=white" alt="Technical Report"/></a>
  <a href="https://github.com/JinyiHan99/GA-Technical-Report"><img src="https://img.shields.io/badge/Code_%26_Data-Reproduction-181717?style=flat-square&logo=github" alt="Reproduction Repo"/></a>
  <a href="https://datawhalechina.github.io/hello-generic-agent/"><img src="https://img.shields.io/badge/Tutorial-Datawhale-blue?style=flat-square" alt="Tutorial"/></a>
  <a href="https://fudankw.cn/sophub"><img src="https://img.shields.io/badge/Skill_Hub-Sophub-purple?style=flat-square" alt="Sophub"/></a>
</p>

<p>
  <a href="https://trendshift.io/repositories/25944" target="_blank"><img src="https://trendshift.io/api/badge/repositories/25944" alt="Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

**[English](#-english) · [中文](#-中文)**

</div>

> 📌 **Official:** GitHub + https://gaagent.ai only. DintalClaw is the sole authorized commercial partner; others are not affiliated.

---

<a id="-english"></a>

## 🌟 Overview

**GenericAgent** is a minimal, self-evolving autonomous agent framework. Its core is just **~3K lines of code**. Through **9 atomic tools + a ~100-line Agent Loop**, it grants any LLM system-level control over a local computer — covering browser, terminal, filesystem, keyboard/mouse input, screen vision, and mobile devices (ADB).

> Design philosophy — **don't preload skills, evolve them.**

Every time GenericAgent solves a new task, it automatically crystallizes the execution path into a reusable **Skill**. The longer you use it, the more skills accumulate — forming a personal skill tree grown entirely from 3K lines of seed code.

> 🤖 **Self-Bootstrap Proof** — Everything in this repository, from installing Git and running `git init` to every commit message, was completed autonomously by GenericAgent. The author never opened a terminal once.

### 📑 Table of Contents

- [Key Features](#-key-features)
- [Demo Showcase](#-demo-showcase)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Unlocking Advanced Capabilities](#-unlocking-advanced-capabilities)
- [Architecture](#-architecture)
- [Self-Evolution Mechanism](#-self-evolution-mechanism)
- [Comparison](#-comparison)
- [Evaluation](#-evaluation)
- [Roadmap & News](#-roadmap--news)
- [Community & Support](#-community--support)
- [License](#-license)

---

## 📋 Key Features

| Feature | Description |
| :--- | :--- |
| 🧬 **Self-Evolving** | Automatically crystallizes each task into a Skill. Capabilities grow with every use, forming your personal skill tree. |
| 🪶 **Minimal Architecture** | ~3K lines of core code. Agent Loop is ~100 lines. No complex dependencies, zero deployment overhead. |
| ⚡ **Strong Execution** | **TMWebdriver** injects into a real browser (preserving login sessions). 9 atomic tools take direct control of the system. |
| 🔌 **High Compatibility** | Supports Claude / Gemini / Kimi / MiniMax and other major models. Cross-platform. |
| 💰 **Token Efficient** | <30K context window — a fraction of the 200K–1M other agents consume. Less noise, fewer hallucinations, higher success rate, lower cost. |

---

## 🎯 Demo Showcase

<table>
  <tr>
    <td align="center" width="50%"><b>🛡️ Real-Browser CAPTCHA Survival</b></td>
    <td align="center" width="50%"><b>🌐 Autonomous Web Exploration</b></td>
  </tr>
  <tr>
    <td><img src="assets/demo/discord_hcaptcha_real_browser.gif" width="100%" alt="Discord hCaptcha passed in real browser"></td>
    <td><img src="assets/demo/autonomous_explore.png" width="100%" alt="Web Exploration"></td>
  </tr>
  <tr>
    <td><sub>While configuring a Discord bot, an hCaptcha <i>"Are you human?"</i> challenge pops up mid-task — GA's real browser session passes it and the task continues. See <a href="#browser-realness-of-ga-web-tools">Browser Realness</a>.</sub></td>
    <td><sub>Autonomously browses and periodically summarizes web content.</sub></td>
  </tr>
  <tr>
    <td align="center"><b>🧋 Food Delivery Order</b></td>
    <td align="center"><b>📈 Quantitative Stock Screening</b></td>
  </tr>
  <tr>
    <td><img src="assets/demo/order_tea.gif" width="100%" alt="Order Tea"></td>
    <td><img src="assets/demo/selectstock.gif" width="100%" alt="Stock Selection"></td>
  </tr>
  <tr>
    <td><sub><i>"Order me a milk tea"</i> — navigates the delivery app, selects items, completes checkout.</sub></td>
    <td><sub><i>"Find GEM stocks with EXPMA golden cross, turnover &gt; 5%"</i> — quantitative screening.</sub></td>
  </tr>
  <tr>
    <td align="center"><b>💰 Expense Tracking</b></td>
    <td align="center"><b>💬 Batch Messaging</b></td>
  </tr>
  <tr>
    <td><img src="assets/demo/alipay_expense.png" width="100%" alt="Alipay Expense"></td>
    <td align="center"><img src="assets/demo/wechat_batch.png" width="65%" alt="WeChat Batch"></td>
  </tr>
  <tr>
    <td><sub><i>"Find expenses over ¥2K in the last 3 months"</i> — drives Alipay via ADB.</sub></td>
    <td><sub>Sends bulk WeChat messages, fully driving the WeChat client.</sub></td>
  </tr>
</table>

---

## 🚀 Quick Start

> ⚠️ **Python version**: use **Python 3.11 or 3.12**. **Do not** use Python 3.14 — it is incompatible with `pywebview` and a few other GA dependencies.
>
> 📖 Detailed installation guide: **[installation.md](docs/installation.md)** · **[installation_zh.md（中文）](docs/installation_zh.md)**

### For LLM Agents

Fetch the installation guide and follow it:

```bash
curl -fsSL https://raw.githubusercontent.com/lsdefine/GenericAgent/refs/heads/main/docs/installation.md
```

### For Humans

#### Method 1 — Clone & install *(recommended)*

```bash
git clone https://github.com/lsdefine/GenericAgent.git && cd GenericAgent
uv venv && uv pip install -e ".[ui]"
cp mykey_template_en.py mykey.py   # fill in your LLM API key
```

Dependencies are deliberately tiered: the agent core needs only `requests`, plus four lightweight packages (`beautifulsoup4`, `bottle`, `simple-websocket-server`, `aiohttp`) for TMWebdriver's local server. The `[ui]` extra pulls in frontend libraries (Streamlit, `prompt_toolkit`/`rich` for the TUI, …) — install it for the bundled UIs, or skip it entirely and drive the agent headless. No Playwright, no LangChain, no browser binaries to download.

Then launch:

```bash
python frontends/tui_v3.py   # Terminal UI (recommended)
python launch.pyw            # Streamlit web UI
```

#### Method 2 — One-line installer *(convenience)*

Sets up a self-contained directory with an isolated Python environment, Git, and a ready-to-run package. The script is in [`assets/`](assets/) if you'd like to read it first.

**Windows PowerShell**

```powershell
powershell -ExecutionPolicy Bypass -c "$env:GLOBAL=1; irm https://raw.githubusercontent.com/lsdefine/GenericAgent/main/assets/ga_install.ps1 | iex"
```

**Linux / macOS**

```bash
GLOBAL=1 bash -c "$(curl -fsSL https://raw.githubusercontent.com/lsdefine/GenericAgent/main/assets/ga_install.sh)"
```

> 💡 GenericAgent grows its environment **through the Agent itself** — don't pre-install everything. See [Unlocking Advanced Capabilities](#-unlocking-advanced-capabilities) below.

---

## 💻 Usage

### Frontends

#### Terminal UI *(recommended)*

A lightweight, scrollback-first terminal interface built on `prompt_toolkit` + `rich`. Supports multiple concurrent sessions and real-time streaming.

```bash
python frontends/tui_v3.py
```

<details>
<summary><b>⚠️ Windows TUI Troubleshooting</b></summary>

TUI rendering on Windows can be flaky depending on terminal + font. Common causes:

1. `prompt_toolkit` / `rich` are not on the latest version — `pip install -U prompt_toolkit rich` first.
2. PowerShell / cmd ship with terminals that have rough Unicode + key-binding support. **Prefer Git Bash on Windows**, which is much better behaved.
3. If it still looks broken, ask GA itself to fix it:
   > *"My experience using `frontends/tui_v3.py` in PowerShell / cmd / Git Bash on Windows is very poor — lots of incompatibility. Please refer to Claude Code's best practices for the Windows terminal and fix all font and rendering incompatibilities."*

</details>

#### Streamlit UI

```bash
python launch.pyw
```

### Bot Interface (IM)

GenericAgent also supports IM frontends such as Telegram, Discord, and Lark.

| Platform | Command |
| :--- | :--- |
| Telegram | `python frontends/tgapp.py` |
| Discord | `python frontends/dcapp.py` |
| Lark / Feishu | `python frontends/fsapp.py` |

> WeChat, QQ, WeCom and DingTalk are also supported — see the Chinese section below.
> For detailed setup, ask GenericAgent itself.

---

## 🔓 Unlocking Advanced Capabilities

In GA, advanced capabilities are unlocked by **instructing the agent**, not by reading
docs or installing extras. Each instruction below makes GA read its pre-installed SOPs
(battle-tested playbooks in its memory), install whatever is missing, adapt to your OS,
and persist the result into its own memory.

| Capability | Just tell GA |
| :--- | :--- |
| 🌐 Web automation | *"Set up your web automation capability."* — GA guides you through the one manual step: dragging the bundled Chrome extension into `chrome://extensions`. |
| 🔤 OCR | *"Set up your OCR capability with rapidocr and save it to memory."* |
| 👁️ Vision | *"Set up your vision capability from the template in memory/."* — GA copies the template, wires it to your existing LLM keys, and self-tests. |
| 🖱️ Computer use | *"Probe this system and set up your computer-use capability."* |

> 💡 **About language**: the pre-installed SOPs are written in Chinese — GA reads them
> natively, so this never blocks you. If you prefer an English knowledge base, just say:
> *"Read your pre-installed SOPs and rewrite them in English (keep code, paths and error
> strings verbatim)."*
>
> 🌍 **About platforms**: the SOPs were honed on Windows, but cross-platform adaptation is
> itself a GA task — on macOS/Linux, GA swaps in the platform equivalents (window
> enumeration, input control, screenshots) on its own. Same self-evolution principle.

---

## 🧠 Architecture

GenericAgent accomplishes complex tasks through **Layered Memory × Minimal Toolset × Autonomous Execution Loop**, continuously accumulating experience during execution.

### 1️⃣ Layered Memory System

> *Memory crystallizes throughout task execution, letting the agent build stable, efficient working patterns over time.*

| Layer | Name | Description |
| :---: | :--- | :--- |
| **L0** | Meta Rules | Core behavioral rules and system constraints |
| **L1** | Insight Index | Minimal memory index for fast routing and recall |
| **L2** | Global Facts | Stable knowledge accumulated over long-term operation |
| **L3** | Task Skills / SOPs | Reusable workflows for completing specific task types |
| **L4** | Session Archive | Archived task records distilled from finished sessions for long-horizon recall |

### 2️⃣ Autonomous Execution Loop

> *Perceive environment state → Task reasoning → Execute tools → Write experience to memory → Loop*

The entire core loop is just **~100 lines of code** ([`agent_loop.py`](agent_loop.py)).

### 3️⃣ Minimal Toolset

> *GenericAgent provides only **9 atomic tools**, forming the foundational capabilities for interacting with the outside world.*

| Tool | Function |
| :--- | :--- |
| `code_run` | Execute arbitrary code (Python / PowerShell) |
| `file_read` | Read files |
| `file_write` | Write / create / overwrite files |
| `file_patch` | Patch / modify files |
| `web_scan` | Perceive web content |
| `web_execute_js` | Control browser behavior |
| `ask_user` | Human-in-the-loop confirmation |
| `update_working_checkpoint` | *(memory)* Short-term working notepad |
| `start_long_term_update` | *(memory)* Distill long-term memory |

### 4️⃣ Capability Extension

> *Capable of dynamically creating new tools.*

Via `code_run`, GenericAgent can dynamically install Python packages, write new scripts, call external APIs, or control hardware at runtime — crystallizing temporary abilities into permanent tools.

<div align="center">
  <img src="assets/images/workflow.jpg" alt="GenericAgent Workflow" width="420"/>
  <br/><em>GenericAgent Workflow Diagram</em>
</div>

---

## 🧬 Self-Evolution Mechanism

This is what fundamentally distinguishes GenericAgent from every other agent framework.

```text
[New Task]
   │
   ▼
[Autonomous Exploration]   ─►  install deps · write scripts · debug · verify
   │
   ▼
[Crystallize into Skill]   ─►  write to memory layer
   │
   ▼
[Direct Recall on Next Similar Task]
```

| What you say | First time | Every time after |
| :--- | :--- | :--- |
| *"Read my WeChat messages"* | Install deps → reverse DB → write read script → save Skill | **one-line invoke** |
| *"Give me a morning digest of Hacker News"* | Write scraper → build digest → schedule daily run → save Skill | **one-line invoke** |
| *"Monitor stocks and alert me"* | Install `mootdx` → build selection flow → configure cron → save Skill | **one-line start** |
| *"Send this file via Gmail"* | Configure OAuth → write send script → save Skill | **ready to use** |

After a few weeks, your agent instance will have a skill tree no one else in the world has — all grown from 3K lines of seed code.

---

## 📊 Comparison

| Feature | **GenericAgent** | OpenClaw | Claude Code |
| :--- | :---: | :---: | :---: |
| **Codebase** | ~3K lines | ~530,000 lines | Open-sourced (large) |
| **Deployment** | `pip install` + API Key | Multi-service orchestration | CLI + subscription |
| **Browser Control** | Real browser (session preserved) | Sandbox / headless browser | Via MCP plugin |
| **OS Control** | Mouse/kbd, vision, ADB | Multi-agent delegation | File + terminal |
| **Self-Evolution** | Autonomous skill growth | Plugin ecosystem | Stateless between sessions |
| **Out of the Box** | Few core files + starter skills | Hundreds of modules | Rich CLI toolset |

---

## 📈 Evaluation

> 📂 Full evaluation datasets and results: [**JinyiHan99/GA-Technical-Report**](https://github.com/JinyiHan99/GA-Technical-Report/tree/main)

We evaluate GenericAgent across **five dimensions**:

| # | Dimension | Question | Benchmarks |
| :---: | :--- | :--- | :--- |
| 1 | **Task Completion & Token Efficiency** | Can GA complete hard tasks more cheaply than leading agents? | SOP-Bench, Lifelong AgentBench, RealFin-Benchmark |
| 2 | **Tool-Use Efficiency** | Can a minimal atomic toolset solve what specialized toolsets solve, with less overhead? | Tool Efficiency Benchmark (11 simple + 5 long-horizon) |
| 3 | **Memory S