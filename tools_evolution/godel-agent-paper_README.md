# Awesome RSI (Recursive Self-Improvement) [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

Recursive Self-Improvement (RSI) refers to processes in which AI systems improve their own capabilities and can also improve the mechanisms that generate subsequent improvements.

Recent progress in self-training, agent memory, harness optimization, embodied self-improvement, automated AI research, self-modifying coding agents, and evolutionary search has made RSI increasingly relevant as an empirical research direction rather than only a theoretical idea.

Awesome RSI collects and organizes important work across these areas, including model-level self-improvement, context and memory evolution, harness and scaffold evolution, embodied and physical self-improvement, multi-agent systems, automated AI research, benchmarks, and safety.

Not every work listed here demonstrates RSI in the strict sense. Some represent bounded self-improvement or enabling techniques that may contribute to more complete recursive systems.

If you are new to the topic, start with Fundamentals & Getting Started. If you already know the basics, explore the sections most relevant to your interests.

This is a community-maintained and evolving list. Contributions, missing papers, new benchmarks, frameworks, and suggestions for improving the taxonomy are very welcome.

The taxonomy is organizational rather than mutually exclusive; many systems span multiple layers and mechanisms.

## Contents

- [Scope & Terminology](#scope--terminology)
- [Fundamentals & Getting Started](#fundamentals--getting-started)
- [Model-level RSI](#model-level-rsi)
  - [Self-Training & Self-Reward](#self-training--self-reward)
  - [Synthetic Data & Self-Distillation](#synthetic-data--self-distillation)
  - [Self-Play & Iterative Fine-tuning](#self-play--iterative-fine-tuning)
  - [Self-Taught Reasoning](#self-taught-reasoning)
- [Harness-level RSI](#harness-level-rsi)
  - [Prompt & Program Optimization](#prompt--program-optimization)
  - [Context & Memory Evolution](#context--memory-evolution)
  - [Harness & Scaffold Evolution](#harness--scaffold-evolution)
  - [Extensible Harness Substrates](#extensible-harness-substrates)
  - [Self-Verification & Self-Correction — Enabling Foundations](#self-verification--self-correction--enabling-foundations)
  - [Self-Evolving Agent Frameworks](#self-evolving-agent-frameworks)
- [Multi-Agent Self-Improvement](#multi-agent-self-improvement)
  - [Co-Evolution](#co-evolution)
  - [Inference-time Debate](#inference-time-debate)
- [Coding / Software-Engineering Self-Improvement](#coding--software-engineering-self-improvement)
  - [Self-Modifying Coding Agents](#self-modifying-coding-agents)
  - [Iterative Repair & Training](#iterative-repair--training)
- [Automated AI R&D](#automated-ai-rd)
- [Embodied & Physical Self-Improvement](#embodied--physical-self-improvement)
- [Evolutionary & Open-Ended RSI](#evolutionary--open-ended-rsi)
- [Safety, Alignment & Theory](#safety-alignment--theory)
  - [Supporting Safety Foundations](#supporting-safety-foundations)
- [Introspection & Self-Modeling](#introspection--self-modeling)
- [Benchmarks & Evaluations](#benchmarks--evaluations)
  - [Direct RSI & Self-Improvement Evaluations](#direct-rsi--self-improvement-evaluations)
  - [Frontier Lab Self-Improvement & AI R&D Evaluation Frameworks](#frontier-lab-self-improvement--ai-rd-evaluation-frameworks)
  - [AI R&D Capability Proxies](#ai-rd-capability-proxies)
  - [Agent Capability Proxies](#agent-capability-proxies)
- [Frameworks & Tools](#frameworks--tools)
  - [Self-Modifying / Self-Evolving Systems](#self-modifying--self-evolving-systems)
  - [Harness / Memory / Skill Evolution](#harness--memory--skill-evolution)
  - [Automated Search / AI R&D](#automated-search--ai-rd)
- [Blog Posts & Discussions](#blog-posts--discussions)
- [Talks & Videos](#talks--videos)
- [Related Awesome Lists](#related-awesome-lists)

## Scope & Terminology

For this list, we use the following operational distinctions:

**Self-refinement** — improves the current output without a persistent change to the system.

**Persistent self-improvement** — changes to weights, memory, skills, prompts, harness, or code that carry into the next round.

**Recursive self-improvement** — the mechanism that produces improvements is itself the object of improvement.

**RSI substrate** — exposes an agent's own structure as a modifiable object, but does not necessarily form an automatic self-improvement loop by default.

## Fundamentals & Getting Started

Foundational papers, formal treatments, and surveys that establish the vocabulary and core questions of RSI.

- [A Survey of Self-Evolving Agents: On Path to Artificial Super Intelligence](https://arxiv.org/abs/2507.21046) - Surveys what, when, and how foundation-model agents can evolve across models, memory, tools, and architectures. (TMLR 2026)
- [Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops](https://arxiv.org/abs/2607.07663) - Surveys recent self-improvement work by update target and loop closure while separating bounded refinement from open-ended RSI. (arXiv 2026)
- [Self-evolving Embodied AI](https://arxiv.org/abs/2602.04411) - Defines the self-evolving embodied AI paradigm across memory self-updating, task self-switching, environment self-prediction, embodiment self-adaptation, and model self-evolution, and systematically reviews work on each component. (arXiv 2026)
- [Self-Improvements in Modern Agentic Systems: A Survey](https://arxiv.org/abs/2607.13104) - Unifies self-improving agents through a system-level view of foundation-model and scaffold updates. (arXiv 2026)
- [A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and Lifelong Agentic Systems](https://arxiv.org/abs/2508.07407) - Organizes agent evolution around feedback loops, update targets, domain applications, evaluation, and safety. (arXiv 2025)
- [A Survey on Self-Evolution of Large Language Models](https://arxiv.org/abs/2404.14387) - Presents a four-stage taxonomy of experience acquisition, refinement, updating, and evaluation for self-evolving LLMs. (arXiv 2024)
- [A Formulation of Recursive Self-Improvement and Its Possible Efficiency](https://arxiv.org/abs/1805.06610) - Gives a formal definition of a restricted RSI system and analyzes when efficient recursive improvement is computable. (arXiv 2018)
- [From Seed AI to Technological Singularity via Recursively Self-Improving Software](https://arxiv.org/abs/1502.06512) - Defines RSI software, surveys prior approaches, and proposes convergence concepts and computational limits. (arXiv 2015)
- [The Singularity: A Philosophical Analysis](https://consc.net/papers/singularity.pdf) - Develops a rigorous philosophical case for an intelligence explosion and examines its assumptions and consequences. (Journal of Consciousness Studies 2010)
- [Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements](https://arxiv.org/abs/cs/0309048) - Defines a fully self-referential machine that rewrites itself after proving a modification improves expected utility. (Artificial General Intelligence book 2006)
- [Optimal Ordered Problem Solver](https://arxiv.org/abs/cs/0207097) - Introduces an asymptotically optimal program-search system that reuses solutions to accelerate later problem solving. (Machine Learning 2004)
- [Evolutionary Principles in Self-Referential Learning, or on Learning How to Learn: The Meta-Meta-... Hook](https://people.idsia.ch/~juergen/diploma1987ocr.pdf) - Describes early meta-evolution and self-referential learning mechanisms that recursively improve learning methods. (Diploma thesis 1987)
- [Speculations Concerning the First Ultraintelligent Machine](https://www.sciencedirect.com/science/article/pii/S0065245808604180) - Introduces the intelligence-explosion argument in which a machine capable of improving machine design triggers accelerating capability gains. (Advances in Computers 1965)

## Model-level RSI

Methods that improve model weights or training behavior through self-generated feedback, data, or reasoning, including canonical enabling methods later reused in persistent self-improvement loops.

### Self-Training & Self-Reward

- [EvoLM: Self-Evolving Language Models through Co-Evolved Discriminative Rubrics](https://arxiv.org/abs/2605.03871) - Alternately trains one model to generate discriminative rubrics and improve its policy from rubric-conditioned rewards without human annotations or external reward models. (arXiv 2026)
- [RLAIF vs. RLHF: Scaling Reinforcement Learning from Human Feedback with AI Feedback](https://arxiv.org/abs/2309.00267) - Studies reinforcement learning from AI-generated preferences as a scalable alternative to direct human feedback. (ICML 2024)
- [Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models](https://arxiv.org/abs/2401.01335) - Iteratively improves one language model through self-play preference learning without additional human annotations. (ICML 2024)
- [Self-Rewarding Language Models](https://arxiv.org/abs/2401.10020) - Trains language models to generate and judge their own instruction-following data over repeated alignment rounds. (ICML 2024)

### Synthetic Data & Self-Distillation

- [Recursive Synthesis for Long-Horizon Terminal Tasks](https://arxiv.org/abs/2608.05466) - Treats accepted tasks as seeds for the next round, generating increasingly difficult terminal tasks used for SFT and PPO as enabling work rather than strict RSI. (arXiv 2026)
- [Beyond Human Data: Scaling Self-Training for Problem-Solving with Language Models](https://arxiv.org/abs/2312.06585) - Iteratively samples, filters, and retrains on model-generated solutions to scale self-training beyond human demonstrations. (TMLR 2024)
- [Self-Alignment with Instruction Backtranslation](https://arxiv.org/abs/2308.06259) - Generates instructions for unlabeled model-written documents and fine-tunes on the resulting synthetic instruction-response pairs. (ICLR 2024)
- [Large Language Models Can Self-Improve](https://arxiv.org/abs/2210.11610) - Uses high-confidence model-generated answers as pseudo-labels for iterative fine-tuning on reasoning tasks. (EMNLP 2023)
- [Self-Instruct: Aligning Language Models with Self-Generated Instructions](https://arxiv.org/abs/2212.10560) - Bootstraps instruction-following data from a model's own generations and filters it before fine-tuning. (ACL 2023)

### Self-Play & Iterative Fine-tuning

- [Learning to Self-Evolve](https://arxiv.org/abs/2603.18620) - Uses reinforcement learning to teach models how to edit their own contexts for stronger performance on future tasks. (arXiv 2026)
- [SERPO: Self-Evolving Rubric Policy Optimization for Open-Ended Test-Time Reinforcement Learning](https://arxiv.org/abs/2607.26873) - Co-evolves response evidence, query-specific rubrics, and policy parameters in a closed test-time reinforcement-learning loop. (arXiv 2026)
- [Teaching LLMs to Self-Evolve: Cultivating Core Meta-Skills with Reinforcement Learning](https://arxiv.org/abs/2607.21971) - Trains MetaEvolve's reflection and feedback-driven refinement skills before applying inference-time evolutionary search to open-ended optimization. (arXiv 2026)
- [TEMPO: Scaling Test-time Training for Large Reasoning Models](https://arxiv.org/abs/2604.19295) - Interleaves model-parameter updates on unlabeled test questions with periodic critic recalibration on labeled data to sustain test-time improvement. (arXiv 2026)
- [Meta-Rewarding Language Models: Self-Improving Alignment with LLM-as-a-Meta-Judge](https://arxiv.org/abs/2407.19594) - Lets a language model judge its own judgments and iteratively improve both evaluation and instruction-following ability. (EMNLP 2025)
- [Self-Adapting Language Models](https://arxiv.org/abs/2506.10943) - Introduces SEAL, which generates its own update data and fine-tuning directives to adapt model weights to new tasks. (NeurIPS 2025)
- [Self-Improvement in Language Models: The Sharpening Mechanism](https://arxiv.org/abs/2412.01951) - Formalizes self-improvement as amortizing a model's verifier-guided search into a sharper post-trained policy. (ICLR 2025)
- [Self-Play Preference Optimization for Language Model Alignment](https://arxiv.org/abs/2405.00675) - Frames alignment as a two-player game and iteratively updates a policy toward a preference-model Nash equilibrium. (ICLR 2025)
- [SELF: Self-Evolution with Language Feedback](https://arxiv.org/abs/2310.00533) - Repeats self-feedback, response refinement, filtering, and fine-tuning so an LLM progressively improves on unlabeled instructions. (arXiv 2023)

### Self-Taught Reasoning

- [rStar-Math: Small LLMs Can Master Math Reasoning with Self-Evolved Deep Thinking](https://arxiv.org/abs/2501.04519) - Couples Monte Carlo tree search with self-evolved training data and a process preference model to improve mathematical reasoning. (ICML 2025)
- [Quiet-STaR: Language Models Can Teach Themselves to Think Before Speaking](https://arxiv.org/abs/2403.09629) - Trains language models to generate useful internal rationales throughout arbitrary text rather than only on question-answer tasks. (COLM 2024)
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) - Alternates rationale generation, answer filtering, rationalization, and fine-tuning to bootstrap reasoning ability. (NeurIPS 2022)

## Harness-level RSI

Methods that improve prompts, memory, verification, tools, or agent policies around a model.

### Prompt & Program Optimization

- [Automated Design of Agentic Systems](https://arxiv.org/abs/2408.08435) - Uses a meta-agent to invent and iteratively improve agent architectures represented as executable code. (ICLR 2025)
- [TextGrad: Automatic "Differentiation" via Text](https://arxiv.org/abs/2406.07496) - Backpropagates textual feedback through compound AI systems to optimize prompts, code, and other textual variables. (Nature 2025)
- [Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models](https://arxiv.org/abs/2310.04406) - Combines Monte Carlo tree search, model-based value estimates, environment feedback, and self-reflection without updating base weights. (ICML 2024)
- [Large Language Models as Optimizers](https://arxiv.org/abs/2309.03409) - Introduces OPRO, which iteratively proposes and evaluates natural-language solutions and prompts from a history of scored attempts. (ICLR 2024)
- [Promptbreeder: Self-Referential Self-Improvement Via Prompt Evolution](https://arxiv.org/abs/2309.16797) - Evolves both task prompts and the mutation prompts that generate future prompt improvements. (ICML 2024)
- [Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation](https://arxiv.org/abs/2310.02304) - Demonstrates an LLM-written scaffolding program that improves the program responsible for making further improv