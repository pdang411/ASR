# ASR

> **AI Semantic Reference**

**ASR** is a production-ready **Model Context Protocol (MCP) server** that provides deterministic tools for AI assistants.

Instead of relying solely on language model memory, ASR gives AI clients access to structured services through MCP. By exposing reliable tools rather than generated answers, ASR helps build AI applications that are more consistent, testable, and easier to automate.

Built for developers, ASR is lightweight, extensible, and designed to integrate with any MCP-compatible client.

---

# Why ASR?

Large Language Models are excellent at reasoning, but they are not authoritative sources of truth.

ASR adds a deterministic layer between AI assistants and structured information. Rather than asking an LLM to remember everything, ASR exposes reliable tools that return predictable, machine-readable results.

The AI performs the reasoning.

**ASR provides the capabilities.**

---

# Features

* **MCP Native** — Built specifically for the Model Context Protocol.
* **Deterministic Responses** — Structured JSON with predictable schemas.
* **Model Independent** — Works with any MCP-compatible AI client.
* **OpenAI-Compatible** — Supports local or remote OpenAI-compatible LLMs through your AI client.
* **Modular Architecture** — Add new tools without changing the core server.
* **Developer First** — Clean, simple, and extensible design.

---

# Architecture

```text
                 AI Client
(OpenCode, Claude Desktop, VS Code)

              MCP (stdio)

                   │

             ASR MCP Server

                   │

           Tool Dispatcher

    ┌─────────┬──────────┬──────────┐
    │         │          │          │
 Modules   Search   Reference   Workflow

                   │

               ASR Core
```

ASR separates AI reasoning from tool execution. The AI client decides **when** to use a tool, while ASR executes the request and returns deterministic results.

---

# What ASR Provides

ASR is built around reusable MCP tools.

Examples include:

* Module discovery
* Documentation search
* Reference retrieval
* Workflow execution
* Project knowledge lookup
* Structured JSON responses
* Custom MCP tools
* Plugin-ready architecture

Every capability is exposed through MCP using consistent request and response formats.

---

# Core Principles

### MCP First

Every feature is designed as an MCP tool from the beginning.

### Deterministic

When a tool can answer a request, ASR returns structured data instead of relying on generated text.

### Modular

Each service is independent, making it easy to add new capabilities without modifying the core server.

### AI Friendly

ASR extends AI assistants with reliable capabilities while allowing the language model to focus on reasoning and decision making.

---

# Compatible Clients

ASR is designed to work with any MCP-compatible client, including:

* OpenCode
* Claude Desktop
* Visual Studio Code
* Custom AI Agents
* Future MCP-enabled applications

---

# Vision

ASR is designed to become a reusable MCP platform for AI applications.

Rather than embedding business logic inside a language model, ASR exposes reusable tools that any AI client can invoke through the Model Context Protocol.

The goal is simple:

* Reliable tools
* Deterministic results
* Clean architecture
* Reusable services
* AI that works with trusted capabilities instead of guesswork

---

# Project Status

ASR is under active development.

The initial release focuses on delivering a fast, reliable, and extensible MCP server with a growing collection of deterministic tools for AI assistants.

---

# License

MIT License
