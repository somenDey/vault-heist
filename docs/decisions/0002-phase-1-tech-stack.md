# 2. Phase 1 tech stack

- **Status:** Accepted
- **Date:** 2026-09-23

## Context

Phase 1 needs a web game backed by an LLM, built in a way that later phases (tool calling, guardrails, evals, tracing, deployment) can grow from without rewrites. The project is public, so it must be easy for others to clone, read and run. It's developed on Windows 11 and checked by CI on Linux.

## Decision

| Area | Choice | Why |
|---|---|---|
| Repo layout | Monorepo: `backend/`, `frontend/`, `docs/` | One place for the whole project; easy for readers to explore. |
| Backend | Python + FastAPI | The main AI agent ecosystem is Python. FastAPI gives typed request handling and automatic API docs. |
| Python version | 3.13, installed and pinned with uv | Current stable Python with broad library support. The pin keeps every machine and CI identical. |
| Python tooling | `uv` for Python, packages and virtual environments; `ruff` for linting and formatting; `mypy` for type-checking; `pytest` for tests | Fast, modern and widely adopted. One lockfile (`uv.lock`) gives reproducible installs. |
| LLM access | [LiteLLM](https://github.com/BerriAI/litellm), wrapped in our own small `LLMClient` interface | LiteLLM speaks to Claude, GPT, Gemini and local Ollama models through one API, so the model is a config setting. Our own interface keeps LiteLLM out of the rest of the code, and lets tests use a fake client. |
| Default model | A small, cheap model, set in `.env` (initially Claude Haiku 4.5) | Keeps playtesting cheap. Switching model is a `.env` change only. |
| Config | `pydantic-settings` reading `.env` | Typed and validated. A missing or invalid setting fails loudly at startup, not halfway through a game. |
| Database | SQLite via SQLAlchemy 2.x, with Alembic migrations | Zero setup for now. Moving to Postgres later (Phase 7) is a connection-string change. |
| Frontend | Vite + React + TypeScript + Tailwind | A simple single-page app; no server rendering needed. |
| Frontend quality | ESLint, Prettier, Vitest | The standard tools for this stack. |
| Automation | `pre-commit` hooks and GitHub Actions CI | Catch problems before they reach GitHub, and again on every push. |
| Task runner | **`just`** (a `justfile`), not `make` | See below. |
| Commits | [Conventional Commits](https://www.conventionalcommits.org/) | Readable history, and changelogs can be generated later. |
| License | MIT | Standard and permissive for a portfolio project. |

### Why `just` instead of `make`

The project is developed on Windows and tested on Linux. `make` isn't available on Windows by default, and Makefiles are full of shell quirks that differ between the two. [`just`](https://github.com/casey/just) is a command runner (not a build system) that installs natively on Windows, macOS and Linux, has clearer syntax and error messages, and can choose a shell per OS. The same `justfile` works on the developer's machine and in CI.

The project's structure diagram lists a `Makefile`; in this repository it is a `justfile` instead, with the same targets (`dev`, `test`, `lint`, `format`).

## Consequences

- Contributors need `uv`, Node.js and `just` installed. All three are single installs on every OS, documented in [getting started](../getting-started.md).
- Wrapping LiteLLM means a little more code up front, but provider details never leak into game logic, and tracing and tool calling can be added in one place later.
- SQLite limits us to a single server process. That's fine until deployment in Phase 7.
- Exact library versions are not recorded here. They are pinned in `uv.lock` and `package-lock.json`.
