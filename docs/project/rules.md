# Project rules

> What to use, what to avoid, and how to write. These rules apply to every change to Vault Heist, whoever (or whatever) makes it. This page is the short list. The how-to behind each rule is in [development](development.md), and the look of the game is in [design](design.md).

## How we work

- **One part at a time.** Each phase is split into parts (see the [phase plans](phases/README.md)). A part is done only when its "Done when" checks pass.
- **Plan before building.** Agree what will be built, and why, before writing code.
- **Test before moving on.** Run `just check` before every commit.
- **Docs change in the same commit as the code.**
- **Stay in the current phase.** Leave clean seams for later phases, but don't build ahead.
- **Check current versions** of a library, tool or model before adopting it. This field moves fast.
- **Smallest change that does the job.** Improve in a separate step.
- **Never commit to `main`.** One branch per part, Conventional Commits, a pull request, squash merge. The steps are in [development](development.md#branches-and-pull-requests).

## Code rules

- **Game rules live in `backend/app/game/`.** API routes stay thin: they turn a web request into a function call and back.
- **Only `backend/app/llm/` talks to model providers.** Everything else uses the `LLMClient` interface.
- **Prompts are files** in `backend/app/prompts/`. **Levels are data** in `backend/app/game/levels.py`. Tool descriptions are the one exception: they live in code, next to the tool's argument types ([ADR 0008](decisions/0008-phase-2-agent-design.md)).
- **The bank uses nothing else in the app, and the agent never uses the bank or the game.** The full "may use" table is in [ADR 0008](decisions/0008-phase-2-agent-design.md#2-where-the-code-lives).
- **Storage goes through `GameRecorder`.** The game engine never touches the database directly.
- **Rules that must hold are enforced in code, not only in prompts.** The playtest proved it: the model ignored a prompt rule that a one-line cap in the engine never breaks.
- **Wins and rule checks are decided in code,** never by asking the model.
- **Only `frontend/src/api/client.ts` calls the backend.** The server is the source of truth; pages show what it returns.
- **Types everywhere.** Python has type hints and passes `mypy`; TypeScript has no `any`.
- **Every public function and every file says what it's for,** in a docstring or a top-of-file comment.
- **If new code doesn't clearly fit an existing folder, stop and agree a home for it first.** The folders are listed in [architecture](architecture.md#repository-layout).

## What to use

| Area | Use |
|---|---|
| Backend | Python 3.13, `uv`, FastAPI, Pydantic, SQLAlchemy + Alembic, LiteLLM (behind `LLMClient`), structlog |
| Backend quality | `ruff`, `mypy` (strict), `pytest` |
| Frontend | Vite, React, TypeScript, Tailwind (design tokens in `src/styles/index.css`), React Router |
| Frontend quality | oxlint, Prettier, Vitest + Testing Library |
| Tasks | `just` (run `just` to list every task) |
| Tests | `FakeLLMClient` for scripted model replies, and the fixtures in `backend/tests/conftest.py` |

## What to avoid

- Calling a real LLM, reading `.env`, or using the real database in tests.
- Secrets anywhere except `.env`. Never print or log an API key.
- Hard-coded vault codes. Codes are always random, because the repository is public.
- Importing a provider's library (`anthropic`, `openai`, ...) outside `backend/app/llm/`.
- Game logic in routes or in React components.
- Adding a dependency without agreeing it first. A significant one also needs a [decision record](decisions/).
- ESLint (we use oxlint), `tailwind.config.js` (tokens live in CSS), a state library such as Redux, `make` (we use `just`).
- Editing `uv.lock` or `package-lock.json` by hand, or changing a database migration that is already merged.
- Colours, fonts or spacing outside the [design](design.md) tokens. Gold is the only accent; red means danger.
- Loading fonts or scripts from another website.
- A screen that can't be used with a keyboard, a screen reader or a phone.
- Dead code, commented-out code, and TODOs with no issue.
- `--no-verify`, force-pushing, or rewriting merged history.

## Writing rules

Everything written in this repository follows these rules: documentation, code comments, commit messages, pull requests and the words in the game itself.

### Who we write for

Write for a curious reader who is **not** a programmer, and make sure an engineer still finds it precise. If a non-technical person can follow the page and a senior engineer finds nothing wrong in it, it's right.

### Plain English

- Short sentences, one idea each. Aim for under 25 words.
- Common words: "use" not "utilise", "start" not "initialise", "about" not "approximately".
- Active voice: "The engine checks the limit", not "The limit is checked by the engine".
- Say what something **does** before how it works.
- Explain a technical term the first time it appears on a page, in a few words: "a migration (a numbered script that changes the database)".
- Use the same word for the same thing every time. Our words: *level*, *attempt*, *vault code*, *suspicion*, *guard*, *player*, *session*, *part*, *phase*.
- No filler ("simply", "just", "obviously", "easy") and no hype ("powerful", "robust", "seamless", "cutting-edge").
- British spelling: colour, defence, behaviour, organise.
- Be honest about limits. A known gap is written down, not hidden.

### Structure

- Every page starts with one or two sentences saying what it covers and who it's for.
- Headings say what the section contains ("Running the tests", not "Overview").
- Steps a person follows are a numbered list, one action per step, with the result they should see.
- Use a table when comparing things across the same properties. Use a list for three or more parallel items. Use paragraphs for reasoning.
- Give an example whenever a rule could be read two ways.
- Link to the page that owns a fact; don't copy the fact. Each fact has one home:

| Fact | Home |
|---|---|
| What the product is and who it's for | [prd](prd.md) |
| How the pieces connect | [architecture](architecture.md) |
| How the game plays | [game-design](game-design.md) |
| How it looks | [design](design.md) |
| How to work on it | [development](development.md) |
| What to use and avoid, and how to write | This page |
| Where the project stands | [project memory](memory.md) |
| Why a choice was made | [decisions](decisions/) |
| What is planned | [roadmap and phase plans](phases/README.md) |
| What has been tried against the guard | [playtest-notes](playtest-notes.md) |
| What changed in each release | [CHANGELOG](../../CHANGELOG.md) |

### Formatting

- Commands, file names, settings and code go in `backticks`. Commands a reader will run go in a fenced block, in PowerShell syntax, with nothing else on the line.
- **Bold** for the one thing in a paragraph the reader must not miss. No italics for emphasis.
- Names: **Vault Heist**, **Gus**, **Granite & Sons Savings**. "Level 3", "Phase 2" and "Part 4" take a capital when numbered; "the level" and "the phase" don't.
- Dates are `2026-11-16`. Money in the game is in pounds. Times are UTC unless stated.
- Numbers are measured, never estimated. If a number isn't measured yet, say so.
- Diagrams are Mermaid, in the Markdown file, so they are versioned with the text.
- Every image has alt text that says what it shows.

### Code comments and docstrings

- A comment explains **why**, or what a reader couldn't guess. It never repeats the code.
- Every module starts with a one-line docstring (Python) or comment (TypeScript) saying what it is.
- When code closes a hole found in a playtest, say which attack (e.g. "attack #21 in the playtest notes").

### Commits and pull requests

- The summary is in the imperative and under 72 characters: `feat(game): limit wrong guesses per attempt`.
- A PR description says **what** changed, **why**, and **how it was tested**, in that order.

### Decision records, changelog and playtest notes

- **ADR:** one decision per record, using the template in [ADR 0001](decisions/0001-record-architecture-decisions.md): context, decision, consequences. Include what was rejected and why. Never rewrite an accepted ADR; write a new one that replaces it.
- **Changelog:** written for a person using the game, not for a developer. Player-visible changes go under **Unreleased** as they are made.
- **Playtest notes:** one row per attack: date, level, model, what was tried, the result, the lesson. Record failures too. Re-test against a different code before calling something a leak.

### Words in the game

- Gus: short sentences, dry humour, calls people "pal". He never breaks character.
- Interface text: plain, short and friendly. "Start over with a new code", not "Reset session".
- An error says what happened and what the player can do next, in the player's words. Never show an error code or a stack trace.

### Before you call a page finished

- [ ] Could someone who has never seen the project follow it?
- [ ] Is every command copied from a terminal where it worked?
- [ ] Does every link open?
- [ ] Is each fact stated once, in its home?
- [ ] Is the page listed in the [docs index](../README.md)?

## Definition of done for a part

- [ ] Tests added or updated, and `just check` passes
- [ ] Docs updated in the same commit, including [project memory](memory.md) and the phase plan's progress table
- [ ] Committed on its own branch with a Conventional Commit message
- [ ] Pull request merged with all CI checks green
