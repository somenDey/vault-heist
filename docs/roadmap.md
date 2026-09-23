# Roadmap

Vault Heist is built in seven phases. Each phase leaves a working, documented game, and each one adds a new layer of real-world AI agent engineering.

| Phase | Name | Focus | Status |
|---|---|---|---|
| 1 | The Guard | Project foundation, LLM basics, a playable 3-level game | 🚧 In progress |
| 2 | The Guard Gets Powers | Tool calling, agent loop, mock bank backend, LangGraph | Planned |
| 3 | Defence in Depth | Guardrails, policy engine, supervisor agent, human approval, indirect injection, RAG | Planned |
| 4 | The Red Team Lab | Attack library, automated attacker agent, evals in CI, false-refusal measurement | Planned |
| 5 | Security Cameras | OpenTelemetry GenAI tracing, Langfuse, heist replay page, cost limits | Planned |
| 6 | More Staff | Multi-agent, MCP server, Microsoft Agent Framework, A2A | Planned |
| 7 | Launch | Docker, AWS deployment, auth, public leaderboard, write-up | Planned |

## Phase 1 progress

| Part | Description | Status |
|---|---|---|
| 0 | Prerequisites and machine setup | ✅ Done |
| 1 | Repository and documentation skeleton | ✅ Done |
| 2 | Backend skeleton | ⏳ Next |
| 3 | Quality gates: pre-commit and CI | |
| 4 | The LLM layer | |
| 5 | Game logic | |
| 6 | Database and logging | |
| 7 | API endpoints | |
| 8 | Frontend | |
| 9 | Playtest and learn | |
| 10 | Documentation pass and `v0.1.0` release | |

## Phase 1 definition of done

- [ ] Public GitHub repo with a clean structure, MIT license, and green CI badge
- [ ] Three playable levels in the browser, with random per-session codes and a suspicion meter
- [ ] Model switchable via `.env` (at least two providers tested)
- [ ] Every interaction logged with tokens, cost and latency
- [ ] Tests for the LLM layer (fake client), game logic, database and API; frontend component tests
- [ ] README, getting-started, how-to-play, game design, architecture, development, roadmap and playtest notes all written and accurate
- [x] At least 2 ADRs
- [ ] A fresh clone runs by following the docs alone
- [ ] `v0.1.0` release published
