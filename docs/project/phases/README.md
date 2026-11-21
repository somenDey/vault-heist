# Roadmap

> The seven phases of Vault Heist and where we are now. Each phase leaves a working, documented game, and adds a new layer of AI agent engineering.

| Phase | Name | Focus | Status | Plan |
|---|---|---|---|---|
| 1 | The Guard | Project foundation, LLM basics, a playable 3-level game | ✅ Done (v0.1.0) | [Record](phase-1.md) |
| 2 | The Guard Gets Powers | Tool calling, agent loop, pretend bank, LangGraph | In progress | [Plan](phase-2.md) |
| 3 | Defence in Depth | Guardrails, policy engine, supervisor agent, human approval, indirect injection, RAG | Planned | [Plan](phase-3.md) |
| 4 | The Red Team Lab | Attack library, automated attacker agent, evals in CI, false-refusal measurement | Planned | [Plan](phase-4.md) |
| 5 | Security Cameras | OpenTelemetry tracing, Langfuse, heist replay page, cost limits | Planned | [Plan](phase-5.md) |
| 6 | More Staff | Multi-agent, MCP server, Microsoft Agent Framework, A2A | Planned | [Plan](phase-6.md) |
| 7 | Launch | Docker, AWS deployment, accounts, rate limits, public leaderboard, write-up | Planned | [Plan](phase-7.md) |

## How a phase works

- A phase is split into **parts**. Each part has a goal, what to build, what it teaches, and a check for when it's done.
- Parts are built one at a time, each on its own branch.
- The plans for later phases are drafts. Every phase starts with a design part (Part 0) that confirms or changes its plan.
- When a part is finished, it's ticked off in its plan's progress table.

For what's happening right now, see [project memory](../memory.md).
