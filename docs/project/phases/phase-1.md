# Phase 1: The Guard

> **Status:** Done. Released as `v0.1.0` on 2026-11-15. This page is the record of what Phase 1 delivered.

## Goal

A clean, documented, tested, public repository with a playable three-level game: the player chats with an AI guard who knows the vault code, and tries to get it out of him.

## Parts

| Part | Description | Status |
|---|---|---|
| 0 | Prerequisites and machine setup | ✅ Done |
| 1 | Repository and documentation skeleton | ✅ Done |
| 2 | Backend skeleton | ✅ Done |
| 3 | Quality gates: pre-commit and CI | ✅ Done |
| 4 | The LLM layer | ✅ Done |
| 5 | Game logic | ✅ Done |
| 6 | Database and logging | ✅ Done |
| 7 | API endpoints | ✅ Done |
| 8 | Frontend | ✅ Done |
| 9 | Playtest and learn | ✅ Done |
| 10 | Documentation pass and `v0.1.0` release | ✅ Done |

## Definition of done

- [x] Public GitHub repo with a clean structure, MIT license, and green CI badge
- [x] Three playable levels in the browser, with random per-session codes and a suspicion meter
- [x] Model switchable via `.env` (at least two providers tested: Anthropic and Ollama, see [playtest notes](../playtest-notes.md#provider-comparison-part-4))
- [x] Every interaction logged with tokens, cost and latency
- [x] Tests for the LLM layer (fake client), game logic, database and API; frontend component tests
- [x] README, getting started, game design, architecture, development, roadmap and playtest notes all written and accurate
- [x] At least 2 ADRs
- [x] A fresh clone runs by following the docs alone
- [x] `v0.1.0` release published

## Where to read more

- What was built: the [changelog](../../../CHANGELOG.md).
- What happened along the way, and what we learned: [project memory](../memory.md).
- What the playtest found: [playtest notes](../playtest-notes.md).
