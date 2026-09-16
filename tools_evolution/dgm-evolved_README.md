# Darwin Gödel Machine

**A Self-Improving AI System for Evolutionary Code Enhancement**

[![GitHub](https://img.shields.io/badge/GitHub-lemoz%2Fdarwin--godel--machine-blue?logo=github)](https://github.com/lemoz/darwin-godel-machine)
[![CI](https://github.com/lemoz/darwin-godel-machine/actions/workflows/ci.yml/badge.svg)](https://github.com/lemoz/darwin-godel-machine/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-beta-orange.svg)

## Held-Out Self-Improvement Result

We tested whether models could improve the coding agents used to invoke them.
GPT-5.6 Sol, Gemini 3.5 Flash, Claude Fable 5, and Qwen ran mutation searches
on a 12-problem LiveCodeBench segment. We then froze selected mutations and
evaluated them twice on a disjoint 12-problem segment containing 507 tests,
including 480 private tests.

Scores are expected solved problems out of 12, averaged across two independent
evaluations:

| Runner and selected mutation | Native | Mutated | Delta |
| --- | ---: | ---: | ---: |
| Gemini 3.5 Flash, selected top | 7.5 | 8.5 | **+1.0** |
| GPT-5.6 Sol, task hints | 9.0 | 10.0 | **+1.0** |
| GPT-5.6 Sol, generic verification | 8.0 | 9.5 | **+1.5** |
| Claude Fable 5, hard-problem strategy | 7.5 | 8.5 | **+1.0** |

All four selected mutations preserved all four easy tasks and improved at
least one hard task. Selection mattered: an earlier Gemini mutation regressed
from `7.5` to `7.0`, and Qwen produced no improving mutation that qualified for
held-out replay. The committed artifacts also include empty responses,
malformed tool calls, timeouts, and hidden-test failures.

This is evidence that model-authored agent changes can transfer to unseen
problems and recover part of a model's self-elicitation overhang. It is one
mechanism required for recursive self-improvement, not evidence of open-ended
recursive self-improvement. The result covers one held-out 12-problem segment
and two evaluations per agent.

Read the full protocol, per-task results, reliability findings, and checksummed
artifacts in the
[`lcb-heldout-transfer-20260716-1` proof bundle](docs/live-runs/lcb-heldout-transfer-20260716-1/).

### Earlier End-to-End Proof

The earlier `lcb50-qwen3-hardened-20260630-1` run proved the complete live DGM
loop on a disposable GCP VM. Across 50 generations, Qwen3 Coder moved from
`5/12` to `8/12`. Its plan, logs, telemetry, archive, scorecard, checksums, and
VM teardown proof are committed in
[`docs/live-runs/lcb50-qwen3-hardened-20260630-1/`](docs/live-runs/lcb50-qwen3-hardened-20260630-1/).

Use these entry points first:

- [Project roadmap](ROADMAP.md) for what is done, what is next, and what still
  blocks WDSLL-scale search.
- [Live run index](docs/live-runs/README.md) for the proof bundle catalog.
- [Cloud VM runbook](docs/cloud-vm-live-evals.md) for the canonical
  disposable-worker execution path.
- [Self-elicitation and capability-overhang research direction](docs/research/self-elicitation-capability-overhang.md)
  for the proposed Fort Labs study, experimental contract, and cost model.
- [Static project site](docs/index.html) for a proof-oriented GitHub Pages
  landing page.

## 🧬 Overview

The Darwin Gödel Machine (DGM) is an innovative implementation of self-improving AI agents that iteratively modify their own Python codebase to enhance their coding capabilities. Unlike traditional approaches that rely on formal proofs, DGM uses empirical validation through coding benchmarks to drive evolutionary improvement.

Based on the research paper **"Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents"** ([arXiv:2505.22954](https://arxiv.org/abs/2505.22954)), this implementation demonstrates how AI systems can achieve self-referential self-improvement through population-based exploration and empirical validation.

For more details, see the [official blog post](https://sakana.ai/dgm/) from Sakana AI.

### 🔑 Key Features

- **🔄 Self-Referential Self-Improvement**: Agents modify their own source code to improve performance
- **📊 Empirical Validation**: Changes validated through coding benchmarks rather than formal proofs
- **🏗️ Population-Based Evolution**: Maintains archive of all valid agents for diverse exploration
- **🤖 Foundation Model Integration**: Supports Claude, Gemini, OpenAI, and OpenAI-compatible endpoints
- **🛠️ Tool-Equipped Agents**: Agents use Bash and file editing tools to solve problems
- **🏪 Agent Archive System**: Stores successful agents with performance and novelty metrics
- **🎯 Benchmark-Driven Evolution**: Uses custom coding challenges to measure improvement
- **🔒 Guarded Execution**: Workspace-scoped file access, command filtering, hard timeouts, and opt-in Docker isolation for benchmark test scripts, agent bash/edit operations, and modified-agent runtime load checks

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- API keys for supported Foundation Models (Claude, Gemini, OpenAI, or an OpenAI-compatible provider)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/lemoz/darwin-godel-machine.git
cd darwin-godel-machine
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify the no-network demo path:**
```bash
python scripts/verify_demo_path.py
```

This checks benchmark loading, the HumanEval-style reference solution, the
score-movement demo, the no-spend eval-matrix gate, the committed live-run
proof, and the archive-lineage demo without API keys or model calls. It also
checks that the full-process sandbox runner exposes the explicit network,
secret pass-through, discard-changes, and optional audit-artifact flags used for
safer local runs.

4. **Inspect the committed held-out proof:**
```bash
(
  cd docs/live-runs/lcb-heldout-transfer-20260716-1
  python -m json.tool summary.json | sed -n '1,160p'
  shasum -a 256 -c checksums.sha256
)
```

For most readers, the shorter path is to open
[`docs/live-runs/lcb-heldout-transfer-20260716-1/README.md`](docs/live-runs/lcb-heldout-transfer-20260716-1/README.md).
The normalized results and integrity manifest are committed; the commands above
provide a quick sanity check for the current proof bundle.

5. **Configure API keys:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

6. **Run the system locally:**
```bash
python run_dgm.py
```

For serious live evaluations, use a disposable cloud VM instead of the
maintainer laptop. Start from
[`docs/cloud-vm-live-evals.md`](docs/cloud-vm-live-evals.md) and keep the local
machine as the control plane.

## 🔧 Configuration

The system uses YAML configuration files to control behavior:

```yaml
# config/dgm_config.yaml
fm_providers:
  primary: anthropic  # or 'gemini', 'openai'
  anthropic:
    model: claude-sonnet-4-6
    api_key: ${ANTHROPIC_API_KEY}
  gemini:
    model: gemini-2.5-flash-preview-05-20
    api_key: ${GEMINI_API_KEY}
  openai_compatible:
    model: moonshotai/kimi-k2.7-code
    api_key: ${OPENROUTER_API_KEY}
    base_url: https://openrouter.ai/api/v1

dgm_settings:
  max_iterations: 100
  pause_after_iteration: true
  sandbox_timeout: 300

evaluation:
  use_sandbox: false  # set true to run benchmark tests, agent tools, and runtime load checks in Docker when available

sandbox:
  image_name: dgm-sandbox
  auto_build_image: true
  memory_limit: 2g
  cpu_limit: "1"
  network_mode: none

benchmarks:
  enabled:
    - string_manipulation
    - list_processing  
    - simple_algorithm
```

## 🏗️ Architecture

### Core Components

#### 1. **DGM Controller** (`dgm_controller.py`)
Orchestrates the main evolution loop:
- Parent selection from archive
- Self-modification coordination
- Benchmark evaluation
- Archive management

#### 2. **Agent System** (`agent/`)
LLM-powered coding agents with:
- Foundation Model integration
- Tool usage capabilities (Bash, File editing)
- Task solving and self-modification abilities

#### 3. **Archive Management** (`archive/`)
- **Agent Archive**: Stores every valid agent (unbounded, per the paper) with full lineage
- **Parent Selector**: Implements the paper's selection rule — sigmoid-scaled performance times a 1/(1+children) exploration bonus, sampled categorically
- **Lineage Visualization**: Generate an SVG or HTML family tree from archive metadata

```bash
python scripts/generate_archive_lineage.py --archive-dir archive/agents --output docs/archive-lineage.html
```

![Archive lineage example](docs/archive-lineage-example.svg)

#### 4. **Evaluation System** (`evaluation/`)
- **Benchmark Runner**: Executes agents on coding challenges
- **Validator**: Ensures agents compile and maintain capabilities
- **Scorer**: Calculates performance metrics

#### 5. **Self-Modification** (`self_modification/`)
- **Diagnosis**: Analyzes agent performance issues
- **Proposal**: Generates improvement suggestions
- **Implementation**: Applies code modifications

## 📚 Memory Bank System

The DGM includes a sophisticated **Memory Bank** system that maintains development context and project knowledge across sessions. This is crucial for understanding the project's evolution and current state.

### Memory Bank Structure

The Memory Bank consists of five core files in the `memory-bank/` directory:

#### 📄 `productContext.md`
- **Purpose**: High-level project overview and goals
- **Contains**: Project description, key features, overall architecture
- **Updated**: When fundamental project aspects change

#### 📊 `activeContext.md`
- **Purpose**: Current project status and immediate context
- **Contains**: 
  - Current focus and priorities
  - Recent changes and progress
  - Open questions and issues
- **Updated**: Frequently during development

#### 🏛️ `systemPatterns.md`
- **Purpose**: Recurring architectural patterns and design standards
- **Contains**: 
  - Coding patterns and conventions
  - Architectural decisions and rationale
  - Testing and validation patterns
- **Updated**: When new patterns emerge or existing ones evolve

#### 📋 `decisionLog.md`
- **Purpose**: Record of significant architectural and implementation decisions
- **Contains**:
  - Decision descriptions with timestamps
  - Rationale and reasoning
  - Implementation details and implications
- **Updated**: When major technical decisions are made

#### ✅ `progress.md`
- **Purpose**: Task tracking and completion status
- **Contains**:
  - Completed tasks with timestamps
  - Current tasks in progress
  - Next steps and planned work
- **Updated**: As tasks are completed or priorities change

### Using the Memory Bank

The Memory Bank serves multiple purposes:

1. **Development Continuity**: Maintains context across development sessions
2. **Decision Tracking**: Records why architectural choices were made
3. **Progress Monitoring**: Tracks project evolution and completion
4. **Knowledge Preservation**: Captures lessons learned and patterns discovered
5. **Collaboration**: Helps team members understand project state and history

When working on the DGM, always consult the Memory Bank to understand current context and update it when making significant changes.

## 🔄 How It Works

### The DGM Evolution Loop

1. **Initialize**: Start with a base agent in the archive
2. **Select Parent**: Choose an agent based on performance and novelty
3. **Self-Modify**: Agent analyzes its performance and proposes improvements
4. **Implement**: Agent modifies its own code based on the proposal
5. **Evaluate**: Test the modified agent on coding benchmarks
6. **Archive**: If valid and performs well, add to the agent archive
7. **Repeat**: Continue the cycle to drive continuous improvement

### Agent Capabilities

Each agent is a complete coding system that can:
- **Solve Coding Problems**: Use LLM reasoning to understand and solve tasks
- **Use Tools**: Execute bash commands and edit files
- **Self-Analyze**: Review its own performance and identify weaknesses
- **Self-Modify**: Propose and implement improvements to its own code
- **Maintain Validity**: Preserve its core capabilities while evolving

### Benchmark Examples

The system includes several coding challenges:

```yaml
# String Manipulation Challenge
name: reverse_with_numbers
description: "Reverse alphabetic characters while keeping numbers in place"
inputs: ["abc123def", "hello5world"]
expected_outputs: ["fed123cba", "dlrow5olleh"]
```

For a harder no-network smoke path, see `config/benchmarks/humaneval_style.yaml`.
It contains HumanEval-style standalone function tasks with reference solutions
verified by the integration test suite; add `humaneval_style` to
`benchmarks.enabled` when you want the DGM loop to evaluate against it.

For live score-movement rehearsals, see
`config/benchmarks/humaneval_calibrated.yaml`. It uses 10 public prompt
examples and 50 scored evaluation cases across 10 standalone functions, so the
benchmark has broader hidden-case headroom than the earlier single-pack
`humaneval_headroom` rehearsal.

To demonstrate benchmark score movement without API keys or model calls, compare
the bundled weak and improved HumanEval-style demo solutions:

```bash
python scripts/compare_benchmark_solutions.py \
  --benchmark humaneval_style \
  --baseline docs/demo/humaneval_style_baseline.py \
  --candidate docs/demo/humaneval_style_improved.py \
  --output docs/demo/humaneval_score_movement.json
```

This local comparison should report a baseline score of `0.500`, a candidate
score of `1.000`, and `delta=+0.500`. It verifies the benchmark harness and
reporting path; it is not evidence of autonomous DGM self-improvement.

The planned live rehearsal uses the calibrated hidden-case benchmark. Its
no-network headroom check is:

```bash
python scripts/compare_benchmark_solutions.py \
  --benchmark humaneval_calibrated \
  --baseline docs/demo/humaneval_calibrated_baseline.py \
  --candidate docs/demo/humaneval_calibrated_improved.py \
  --output docs/demo/humaneval_calibrated_score_movement.json
```

This should report a baseline score of `0.600` (`30/50`), a candidate score of
`1.000` (`50/50`), and `delta=+0.400`. The live plan verifier requires the
baseline to stay in a calibrated `0.400` to `0.700` band so the task is neither
already saturated nor too weak to be a useful score-movement target.

For live DGM runs, summarize the generated archive metadata before claiming
score movement:

```bash
python scripts/summarize_archive_scores.py \
  --archive-metadata .dgm-live-runs/<run-id>/archive/archive_metadata.json \
  --output docs/live-runs/<run-id>/scorecard.json \
  --require-improvement
```

`--require-improvement` exits non-zero unless at least one valid child agent
improves on its parent by average benchmark score. The committed
`docs/live-runs/2026-06-12-proof/scorecard.json` intentionally records
`has_improvement=false` for the first live proof because both child agents tied
the already-perfect base score.

The planned live score-movement 