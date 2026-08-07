# ASR — AI Services Runtime

**ASR (AI Services Runtime)** is a lightweight, high-performance **Model Context Protocol (MCP) server and orchestration runtime** that provides deterministic AI services, structured tools, and intelligent workflow coordination for AI assistants.

Instead of relying solely on language model memory, ASR gives AI clients access to reliable services through MCP. By exposing deterministic tools rather than generated answers, ASR enables AI applications that are more consistent, testable, observable, and easier to automate.

ASR separates **AI reasoning** from **service execution**, allowing language models to focus on reasoning while ASR delivers deterministic capabilities, orchestration, and runtime intelligence.

Built for developers, ASR is lightweight, extensible, provider-agnostic, and designed to integrate with any MCP-compatible client.

---

# Why ASR?

Large Language Models are exceptional at reasoning, but they are not authoritative sources of truth and should not be responsible for business logic or system orchestration.

ASR provides a deterministic runtime between AI assistants and real-world services.

Rather than asking an LLM to remember everything, ASR exposes reliable MCP tools that return structured, machine-readable results.

The language model performs the reasoning.

**ASR provides the services, orchestration, execution, and operational intelligence.**

---

# Features

* **MCP Native** — Built specifically for the Model Context Protocol.
* **AI Services Runtime** — A reusable runtime for deterministic AI services.
* **Deterministic Responses** — Structured JSON with predictable schemas.
* **Model Independent** — Compatible with any MCP-enabled AI client.
* **Provider Agnostic** — Works with local or remote reasoning providers.
* **OpenAI-Compatible** — Supports OpenAI-compatible APIs through the AI client.
* **Smart Preemption** — Coordinates reasoning requests while minimizing unnecessary LLM usage.
* **AI.KB Working Memory** — Runtime knowledge, shared context, and execution state.
* **Parallel Task Execution** — Maximizes useful work across multiple agents.
* **Deterministic Routing** — Lightweight logic-gate decisions instead of additional AI reasoning.
* **Modular Architecture** — Add new capabilities without modifying the core runtime.
* **Developer First** — Clean, extensible, and easy to integrate.
* **Raspberry Pi First** — Optimized for constrained hardware while scaling naturally to desktop and cloud environments.

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
                ASR Runtime
                     │
                     ▼
             Executor Registry
                     │
                     ▼
                MCP Services
```

ASR separates reasoning from execution.

The AI client decides **what** needs to be solved.

ASR decides **how** it should be executed.

The language model focuses on reasoning while ASR manages routing, orchestration, context reuse, deterministic execution, and runtime coordination.

---

# Smart Preemption

Smart Preemption is ASR's deterministic orchestration engine.

Instead of allowing agents to invoke language models directly, agents submit **reasoning demands** to Smart Preemption.

Smart Preemption evaluates lightweight deterministic decision factors to determine the next best action.

Possible actions include:

* Continue execution
* Wait for dependencies
* Reuse AI.KB context
* Merge compatible reasoning requests
* Request LLM reasoning
* Complete the workflow

Design goals:

* Minimize token consumption
* Maximize useful LLM work
* Reuse previous reasoning
* Keep agents executing in parallel
* Prevent orchestration bottlenecks
* Maintain a constant-time hot path whenever possible

---

# AI.KB Working Memory

AI.KB is ASR's operational memory.

Rather than storing model weights, AI.KB maintains runtime knowledge that improves orchestration efficiency over time.

Examples include:

* Current task state
* Current agent state
* Shared context
* Dependency status
* Confidence values
* Previous results
* Runtime metrics
* Cache availability
* Workflow summaries
* Engineering rules
* Decision history
* Runtime performance metrics

AI.KB enables ASR to make better orchestration decisions without retraining the underlying language model.

---

# Core Principles

## MCP First

Every capability is designed as an MCP service from the beginning.

## Deterministic

Whenever a tool can answer a request, ASR returns structured data instead of generated text.

## Provider Agnostic

ASR works with any MCP-compatible client and any reasoning provider.

## Modular

Capabilities can be added independently without changing the core runtime.

## AI Friendly

ASR extends AI assistants with reliable capabilities while allowing language models to focus on reasoning.

## Raspberry Pi First

Every feature is designed to operate efficiently on constrained hardware and scale upward without changing the architecture.

---

# Smart Preemption Design Principles

* Constant-time hot path (O(1) where practical)
* Lightweight deterministic decision logic
* AI.KB before new reasoning
* Shared reasoning before duplicate reasoning
* Parallel execution whenever possible
* Runtime-aware orchestration
* Low memory footprint
* Low CPU overhead
* Minimized token consumption
* Never become the system bottleneck

---

# What ASR Provides

ASR exposes reusable AI services through MCP, including:

* Module discovery
* Documentation search
* Reference retrieval
* Workflow execution
* Project knowledge lookup
* Structured JSON responses
* AI.KB services
* Smart Preemption services
* Plugin-ready architecture
* Custom MCP tools

Every capability is available through consistent MCP request and response formats.

---

# Compatible Clients

ASR is designed to work with any MCP-compatible client, including:

* OpenCode
* Claude Desktop
* Visual Studio Code
* Custom AI agents
* Local AI runtimes
* Future MCP-enabled applications

---

# Project Vision

ASR is designed to become a reusable **AI Services Runtime** for modern AI applications.

Instead of embedding business logic inside language models, ASR exposes deterministic services that any AI client can invoke through MCP.

As the platform evolves, AI.KB, Smart Preemption, and runtime intelligence will continuously improve orchestration efficiency while preserving deterministic execution and clean system architecture.

The goal is simple:

* Reliable AI services
* Deterministic execution
* Efficient orchestration
* Parallel execution
* Lower token consumption
* Reusable capabilities
* Clean architecture
* Provider independence
* AI systems built on trusted services instead of guesswork

---

# Project Status

ASR is under active development.

Current development focuses on:

* Deterministic MCP services
* Smart Preemption
* AI.KB working memory
* Parallel agent coordination
* Runtime optimization
* Token efficiency
* Raspberry Pi deployment
* Desktop scalability
* Cloud scalability
* Progressive operational intelligence

---

# License

MIT License
