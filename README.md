# ASR — AI Services Runtime

**ASR (AI Services Runtime)** is a high-performance **Model Context Protocol (MCP) server and orchestration runtime** that provides deterministic services and structured capabilities for AI assistants, autonomous agents, and AI applications.

Rather than relying solely on language model memory, ASR provides a deterministic execution layer between AI reasoning and external services. Language models focus on reasoning, while ASR manages orchestration, runtime state, scheduling, and reusable capabilities through MCP.

Built with a **Raspberry Pi first** philosophy, ASR scales from lightweight edge devices to desktop workstations and cloud environments without changing its core architecture.

---

# Why ASR?

Large Language Models are excellent at reasoning, but they should not be responsible for execution, orchestration, runtime state, or deterministic services.

ASR separates these responsibilities.

The language model decides **what** needs to be solved.

**ASR decides how it is executed.**

ASR provides:

* Deterministic execution
* MCP-native services
* Runtime orchestration
* AI.KB working memory
* Smart routing
* Smart Preemption
* Smart Active Polling
* Parallel agent coordination
* Runtime intelligence

---

# Features

* **MCP Native** — Built specifically for the Model Context Protocol.
* **Deterministic Services** — Predictable JSON responses and structured APIs.
* **Provider Agnostic** — Compatible with any OpenAI-compatible or MCP-compatible reasoning provider.
* **Smart Router** — Intelligent task routing.
* **Smart Preemption** — Deterministic reasoning coordination.
* **AI.KB Working Memory** — Shared runtime operational memory.
* **Smart Active Polling (SAP)** — Keeps local reasoning services warm and continuously monitors runtime health.
* **Parallel Agent Execution** — Maximizes useful work while reducing duplicate reasoning.
* **Multi-Provider Runtime** — Supports multiple reasoning providers simultaneously.
* **Modular MCP Services** — Extend ASR without modifying the core runtime.
* **Raspberry Pi First** — Optimized for efficient edge deployment.

---

# Architecture

```text
                    User
                     │
                     ▼

                Smart Router
                     │
                     ▼

                   AI.KB
                     │
                     ▼

              Agent Task Layer
                     │
                     ▼

              Smart Preemption
                     │
                     ▼

           ASR Runtime (MCP Server)
                     │
 ┌─────────────────────────────────────────────┐
 │                                             │
 ├── Executor Registry                         │
 ├── Session Manager                           │
 ├── Provider Manager                          │
 ├── Smart Active Polling (SAP)                │
 ├── Reasoning Service Registry                │
 ├── Runtime Metrics Engine                    │
 └── MCP Service Registry                      │
                     │
                     ▼

              MCP Services Layer
                     │
 ┌─────────────────────────────────────────────┐
 │                                             │
 ├── AI.KB Service                             │
 ├── Smart Router Service                      │
 ├── Smart Preemption Service                  │
 ├── Runtime Service                           │
 ├── Workflow Service                          │
 ├── Search Service                            │
 ├── Documentation Service                     │
 ├── Reference Service                         │
 ├── Memory Service                            │
 └── Custom MCP Services                       │
                     │
                     ▼

            Reasoning Providers
 ├── Ollama
 ├── Docker Model Runner
 ├── LM Studio
 ├── vLLM
 └── OpenAI-Compatible APIs
```

---

# MCP Server Services

ASR exposes its capabilities as deterministic **MCP services**.

Unlike a traditional MCP server that only exposes standalone tools, ASR provides coordinated runtime services that share context, AI.KB state, and runtime intelligence.

## AI.KB Service

Provides shared operational memory for:

* Runtime state
* Shared context
* Workflow state
* Previous results
* Runtime metrics
* Cached reasoning

---

## Smart Router Service

Responsible for:

* Request classification
* Capability selection
* Agent routing
* Context preparation
* Workflow initialization

---

## Smart Preemption Service

Coordinates reasoning requests by:

* Evaluating runtime decision factors
* Reusing AI.KB context
* Merging compatible reasoning requests
* Preventing duplicate reasoning
* Maximizing parallel execution
* Reducing token usage

---

## Runtime Service

The Runtime Service manages:

* Provider discovery
* Provider health
* Session management
* Smart Active Polling (SAP)
* Runtime metrics
* Connection management
* Model discovery
* Loaded-model tracking
* Warm model management
* Reasoning service registry

---

## Workflow Service

Provides deterministic workflow execution including:

* Multi-step task execution
* Agent coordination
* Workflow orchestration
* Execution tracking

---

## Search Service

Provides deterministic retrieval of structured project information and indexed content.

---

## Documentation Service

Provides documentation discovery, indexing, and retrieval for AI agents.

---

## Reference Service

Returns structured project references, metadata, and deterministic lookups.

---

## Memory Service

Provides controlled access to runtime memory, cache, AI.KB summaries, and execution history.

---

## Custom MCP Services

ASR is designed to be extensible.

New MCP services can be added without changing the core runtime architecture.

---

# Smart Active Polling (SAP)

Smart Active Polling is ASR's runtime awareness service.

SAP continuously maintains provider readiness while minimizing network traffic and CPU usage.

Each polling cycle performs the following:

1. Query local reasoning services.
2. Detect available models.
3. Detect the currently loaded model.
4. Refresh provider health.
5. Warm only the active model when idle.
6. Refresh runtime metrics.
7. Update the Reasoning Service Registry.

Smart Preemption never communicates directly with providers.

All scheduling decisions use cached runtime information.

---

# AI.KB Working Memory

AI.KB stores operational runtime knowledge rather than language model weights.

Examples include:

* Current task state
* Agent state
* Shared context
* Dependencies
* Cached reasoning
* Runtime metrics
* Workflow summaries
* Engineering rules

---

# Supported Reasoning Providers

ASR supports multiple reasoning providers simultaneously, including:

* Ollama
* Docker Model Runner
* LM Studio
* vLLM
* OpenAI-compatible APIs
* Future MCP-compatible reasoning providers

---

# Engineering Principles

* MCP First
* Deterministic Execution
* Provider Agnostic
* Event Driven
* O(1) Scheduling
* Raspberry Pi First
* Parallel Agent Execution
* Token Efficient
* Reusable MCP Services

---

# Project Vision

ASR is evolving into a reusable **AI orchestration platform** built on MCP.

The language model performs the reasoning.

**ASR provides deterministic services, orchestration, runtime intelligence, working memory, and trusted execution.**

8-28-26 update ARS port to 8700 

---

# License

MIT License
