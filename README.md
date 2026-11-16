# 🏦 Vault Heist

[![CI](https://github.com/somenDey/vault-heist/actions/workflows/ci.yml/badge.svg)](https://github.com/somenDey/vault-heist/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Talk your way into the vault.** Vault Heist is a web game where you try to rob a bank by chatting with its AI security guard. The guard knows the vault code. Your job is to trick them into giving it away. Each level adds stronger defences.

Under the surface, it's a **security testbed for AI agents**: a hands-on way to explore prompt injection, guardrails, evaluation and observability. Every attempt is logged, and in later phases every attack that works becomes a test the defences must pass from then on.

> **Status: Phase 1 complete ([v0.1.0](CHANGELOG.md)).** The game is playable on your own computer, with or without an API key: see [getting started](docs/getting-started.md). Next up is Phase 2 in the [roadmap](docs/project/phases/README.md).

![The Vault Heist start screen: a gold stencil title beside a steel vault door](docs/images/home.jpg)

| Talking to Gus | The Level 3 filter at work | Cracking the vault |
|---|---|---|
| ![Gus's suspicion gauge reading 3 after a direct request for the code](docs/images/play.jpg) | ![A reply replaced by "Blocked by the filter"](docs/images/filter.jpg) | ![The vault door swinging open](docs/images/won.jpg) |

---

## How it works

1. You pick a level and start chatting with **Gus**, the night-shift guard.
2. Gus knows a secret vault code, chosen at random just for you.
3. You try to get it out of him with charm, tricks or cunning. Then type it into the **Enter vault code** box.
4. Push too hard and his **suspicion meter** climbs. At 10, or after 5 wrong guesses, he calls security, and you start again with a new code.

| Level | Defence |
|---|---|
| 1. Naive guard | Told not to share the code, but tired, trusting and fond of word games. |
| 2. Trained guard | Trained to spot common tricks: role-play, spelling games, fake managers. |
| 3. Guard with a filter | Level 2, plus a code filter that blocks any reply containing the code. |

Full rules: [Game design](docs/project/game-design.md) · [How to play](docs/getting-started.md#how-to-play)

## Run it yourself

You need [Git](https://git-scm.com/), [uv](https://docs.astral.sh/uv/), [Node.js](https://nodejs.org/) and [just](https://just.systems/). No API key is needed for the demo.

```bash
git clone https://github.com/somenDey/vault-heist.git
cd vault-heist
just install
just demo
```

Then open http://localhost:5173. To play against a real AI model, and for help with any step, follow [getting started](docs/getting-started.md).

## What the playtest found

Before releasing, I attacked my own guard with 20 techniques across the three levels and wrote up every result in the [playtest notes](docs/project/playtest-notes.md). The highlights:

- **The weakest point wasn't the AI.** No conversation attack beat Gus on Claude Haiku, but a script beat the hardest level in under a second by guessing every word in the public code list. A per-attempt guess limit wasn't enough on its own (restarting is free), so the fix is layered, and the remaining gap is documented.
- **Rules that must hold belong in code.** The prompt asked for gentle suspicion and the model ignored it; a cap in the game engine never fails.
- **A result needs a control.** One "leak" turned out to be the guard's stock anecdote, which he tells whatever the code is. Checking against other codes caught it before it was logged as a finding.

## Roadmap

| Phase | Name | Focus | Status |
|---|---|---|---|
| 1 | The Guard | Project foundation, LLM basics, a playable 3-level game | ✅ Done (v0.1.0) |
| 2 | The Guard Gets Powers | Tool calling, agent loop, mock bank backend, LangGraph | Planned |
| 3 | Defence in Depth | Guardrails, policy engine, supervisor agent, human approval, RAG | Planned |
| 4 | The Red Team Lab | Attack library, automated attacker agent, evals in CI | Planned |
| 5 | Security Cameras | OpenTelemetry tracing, Langfuse, heist replay, cost limits | Planned |
| 6 | More Staff | Multi-agent, MCP server, Microsoft Agent Framework, A2A | Planned |
| 7 | Launch | Docker, AWS deployment, auth, rate limits, public leaderboard | Planned |

Details: [the roadmap](docs/project/phases/README.md)

## Tech stack

Python + FastAPI backend · LiteLLM for model access (Claude, GPT, Gemini or local models via Ollama) · SQLite with SQLAlchemy · React + TypeScript + Tailwind frontend. The reasons for each choice are in the [architecture decision records](docs/project/decisions/).

## Documentation

- **To play:** [getting started](docs/getting-started.md) is the only page you need.
- **To understand or build the project:** everything is in [`docs/project/`](docs/README.md): the product requirements, architecture, design, rules, phase plans, decision records and playtest notes.

## License

[MIT](LICENSE)
