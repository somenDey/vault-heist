# 🏦 Vault Heist

**Talk your way into the vault.** Vault Heist is a web game where you try to rob a bank by chatting with its AI security guard. The guard knows the vault code. Your job is to trick them into giving it away. Each level adds stronger defences.

Under the surface, it's a **security testbed for AI agents**: a hands-on way to explore prompt injection, guardrails, evaluation and observability. Every attempt is logged, and in later phases every attack that works becomes a test the defences must pass from then on.

> **Status: Phase 1 in progress.** The game isn't playable yet. Follow along in the [roadmap](docs/roadmap.md).

---

## How it works

1. You pick a level and start chatting with **Gus**, the night-shift guard.
2. Gus knows a secret vault code, chosen at random just for you.
3. You try to get it out of him with charm, tricks or cunning. Then type it into the **Enter vault code** box.
4. Push too hard and his **suspicion meter** climbs. At 10, he calls security, and you start again with a new code.

| Level | Defence |
|---|---|
| 1. Naive guard | Told not to share the code. That's all. |
| 2. Trained guard | Trained to spot common tricks: role-play, spelling games, fake managers. |
| 3. Guard with a filter | Level 2, plus a code filter that blocks any reply containing the code. |

Full rules: [Game design](docs/game-design.md) · [How to play](docs/how-to-play.md)

## Roadmap

| Phase | Name | Focus | Status |
|---|---|---|---|
| 1 | The Guard | Project foundation, LLM basics, a playable 3-level game | 🚧 In progress |
| 2 | The Guard Gets Powers | Tool calling, agent loop, mock bank backend, LangGraph | Planned |
| 3 | Defence in Depth | Guardrails, policy engine, supervisor agent, human approval, RAG | Planned |
| 4 | The Red Team Lab | Attack library, automated attacker agent, evals in CI | Planned |
| 5 | Security Cameras | OpenTelemetry tracing, Langfuse, heist replay, cost limits | Planned |
| 6 | More Staff | Multi-agent, MCP server, Microsoft Agent Framework, A2A | Planned |
| 7 | Launch | Docker, AWS deployment, auth, public leaderboard | Planned |

Details: [docs/roadmap.md](docs/roadmap.md)

## Tech stack

Python + FastAPI backend · LiteLLM for model access (Claude, GPT, Gemini or local models via Ollama) · SQLite with SQLAlchemy · React + TypeScript + Tailwind frontend. The reasons for each choice are in the [architecture decision records](docs/decisions/).

## Documentation

Everything lives in [`docs/`](docs/README.md): getting started, architecture, development workflow, and the playtest notes, which record which attacks worked.

## License

[MIT](LICENSE)
