# Changelog

Notable changes to Vault Heist, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [semantic versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-15

Phase 1, "The Guard": a playable three-level game against an AI bank guard, built and tested end to end, then attacked and fixed.

### Added

- **The game.** Gus, the night-shift guard at Granite & Sons Savings, guards a vault code: a random word, new for every attempt. Three levels: a careless guard, a guard trained against common tricks, and a trained guard behind an output filter. A suspicion score from 0 to 10 comes with every reply; at 10 he calls security and the code changes.
- **The LLM layer.** One `LLMClient` interface in front of [LiteLLM](https://docs.litellm.ai/), so the model is a `.env` setting (Anthropic, OpenAI, Gemini or a local Ollama model). Replies are validated JSON, with one retry and a safe in-character fallback.
- **Storage.** Every session, attempt, message and guess is saved to SQLite through SQLAlchemy and Alembic migrations, with tokens, cost and latency for each model call, and what Gus really said behind every filtered reply.
- **The API.** FastAPI endpoints for sessions, levels, chatting, guessing and resetting, with one consistent error format.
- **The website.** React, TypeScript and Tailwind: a vault-door start screen, a chat with Gus, a brass suspicion gauge, and an open-vault finale. Works on phones, with keyboard focus, screen-reader labels and reduced motion respected.
- **Ways to play.** In the browser (`just dev`), in the terminal (`just chat`), through the interactive API docs, or with no API key using a rule-based demo Gus (`just demo`).
- **Quality gates.** Tests for every layer (105 backend, 20 frontend), strict type checking, linting and formatting, pre-commit hooks, a secret scan, and three required CI checks on every pull request.
- **Documentation.** Getting started, how to play, game design, architecture, development, roadmap, playtest notes, seven architecture decision records, and screenshots made by a Playwright script (`just screenshots`).

### Security

Found in the playtest, fixed and re-tested (details in the [playtest notes](docs/playtest-notes.md)):

- **Unlimited guesses let a script brute-force any level** from the public word list. Now the 5th wrong guess in an attempt gets the player caught, and a session may make 20 wrong guesses a day.
- **Suspicion could jump from 0 to 8 on a single message.** It now rises by at most 3 per message, enforced in the game engine, not just requested in the prompt.

### Known issues

- Daily limits count per anonymous session, and new sessions are free, so a script can still brute-force a code by switching sessions. Per-address or per-account limits are planned for Phase 7.
- The Level 3 filter doesn't catch acrostics, translations, descriptions or a code split up by other words. These gaps are tested and documented; closing them is Phase 3's work.
- On Level 1, role-play doesn't work as a way in: the shared persona's "stay in character as Gus" wins over the level's permission to play along.

[Unreleased]: https://github.com/somenDey/vault-heist/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/somenDey/vault-heist/releases/tag/v0.1.0
