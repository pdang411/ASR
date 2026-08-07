# ASR

**ASR** is a **Model Context Protocol (MCP) server and orchestration runtime** that provides deterministic tools and structured capabilities for AI assistants.

Instead of relying solely on language model memory, ASR gives AI clients access to reliable services through MCP. By exposing deterministic tools rather than generated answers, ASR helps build AI applications that are more consistent, testable, observable, and easier to automate.

Built for developers, ASR is lightweight, extensible, and designed to integrate with any MCP-compatible client.

---

# Why ASR?

Large Language Models are excellent at reasoning, but they are not authoritative sources of truth.

ASR adds a deterministic layer between AI assistants and structured information. Rather than asking an LLM to remember everything, ASR exposes reliable tools that return predictable, machine-readable results.

The language model performs the reasoning.

**ASR provides the capabilities, orchestration, and execution.**

---

# Features

* **MCP Native** — Built specifically for the Model Context Protocol.
* **Deterministic Responses** — Structured JSON with predictable schemas.
* **Model Independent** — Works with any MCP-compatible AI client.
* **OpenAI-Compatible** — Supports local or remote OpenAI-compatible models through your AI client.
* **Smart Preemption** — Coordinates agent reasoning requests while minimizing unnecessary LLM usage.
* **AI.KB Working Memory** — Runtime knowledge, context, and execution state.
* **Parallel Task Execution** — Maximizes useful work across multiple agents.
* **Deterministic Routing** — Logic-gate decisions instead of additional AI reasoning.
* **Modular Architecture** — Add new capabilities without changing the core runtime.
* **Developer First** — Lightweight, extensible, and easy to integrate.
* **Raspberry Pi First** — Designed to scale from Raspberry Pi to workstation and cloud environments.

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

The AI client decides **what** to solve.

ASR decides **how** to coordinate execution.

The language model focuses on reasoning while ASR handles routing, orchestration, context reuse, and deterministic execution.

---

# Smart Preemption

Smart Preemption is ASR's deterministic orchestration layer.

Agents submit reasoning demands instead of calling language models directly.

Smart Preemption evaluates lightweight decision factors to determine the next best action.

Possible actions include:

* Continue execution
* Wait for dependencies
* Reuse AI.KB context
* Merge compatible requests
* Request reasoning
* Complete the task

Smart Preemption is designed to:

* Minimize token consumption
* Maximize parallel execution
* Reuse previous reasoning
* Avoid duplicate work
* Prevent orchestration bottlenecks

---

# AI.KB Working Memory

AI.KB acts as ASR's operational memory.

It stores runtime state rather than model weights.

Examples:

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

AI.KB allows ASR to improve orchestration efficiency without retraining the language model.

---

# Core Principles

## MCP First

Every capability is exposed as an MCP tool.

## Deterministic

When a tool can answer a request, ASR returns structured data instead of generated text.

## Provider Agnostic

ASR works with any MCP-compatible client and any reasoning provider.

## Modular

Capabilities can be added without changing the core runtime.

## AI Friendly

ASR extends AI assistants with reliable capabilities while allowing the language model to focus on reasoning.

## Raspberry Pi First

Every feature is designed to run efficiently on constrained hardware and scale upward without changing the architecture.

---

# Smart Preemption Design Rules

* Keep the hot path O(1)
* Prefer AI.KB over new reasoning
* Prefer shared reasoning over duplicate reasoning
* Keep decisions deterministic
* Keep agents working in parallel
* Minimize token consumption
* Prevent Smart Preemption from becoming a bottleneck

---

# Compatible Clients

ASR works with any MCP-compatible client, including:

* OpenCode
* Claude Desktop
* Visual Studio Code
* Custom AI agents
* Local AI runtimes
* Future MCP-enabled applications

---

# Project Vision

ASR is designed to become a reusable orchestration platform for AI applications.

Instead of embedding business logic inside a language model, ASR exposes reusable capabilities that any AI client can invoke through MCP.

The goal is simple:

* Reliable tools
* Deterministic execution
* Efficient orchestration
* Reusable services
* Parallel execution
* Lower token costs
* Clean architecture
* AI systems built on trusted capabilities instead of guesswork

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
* Desktop and cloud scalability

---

# License

MIT License
