# Project memory

> The living record of where Vault Heist stands. Read it at the start of every working session, and update it at the end of every part. Keep it short: details belong in the other docs, so link to them rather than copying.

## Where we are

- **Version:** `v0.1.0` (Phase 1 complete, released 2026-11-15).
- **Current phase:** Phase 2, "The Guard Gets Powers". Part 0 (design) done.
- **Next step:** Phase 2, Part 1: the pretend bank. See [`docs/project/phases/phase-2.md`](phases/phase-2.md).

## What exists today

- A playable three-level game against Gus, the night guard: random vault code per attempt, suspicion meter, output filter on Level 3, limits on messages and wrong guesses.
- Backend: FastAPI, LiteLLM behind our own `LLMClient`, structured `{reply, suspicion}` output with retry and fallback, SQLite storage of every message, guess and model call.
- Frontend: React, TypeScript and Tailwind, with a custom vault design (see [design](design.md)).
- Ways to play: browser (`just dev`), terminal (`just chat`), API docs page, free demo Gus (`just demo`).
- Quality: 105 backend and 20 frontend tests at release, strict type checks, pre-commit hooks, secret scanning, three required CI checks.
- Default model: Claude Haiku 4.5 (`anthropic/claude-haiku-4-5-20251001`). Also tested with a local Ollama model, `granite4.2:8b` ([comparison](playtest-notes.md#provider-comparison-part-4)).

## Key decisions

| Decision | Where |
|---|---|
| Monorepo, Python + FastAPI, LiteLLM behind our own interface, SQLite, Vite + React, `just` instead of `make` | [ADR 0002](decisions/0002-phase-1-tech-stack.md) |
| Pre-commit hooks and three required CI checks | [ADR 0003](decisions/0003-quality-gates.md) |
| Guard replies as validated JSON, one retry, safe fallback | [ADR 0004](decisions/0004-structured-output.md) |
| Store every interaction, via a `GameRecorder` interface | [ADR 0005](decisions/0005-storage.md) |
| API design: anonymous sessions, one error shape | [ADR 0006](decisions/0006-api-design.md) |
| oxlint instead of ESLint; Tailwind 4 tokens in CSS; vault design | [ADR 0007](decisions/0007-frontend.md) |
| Every change on its own branch, squash-merged through a PR | [development](development.md#branches-and-pull-requests) |
| Phase 2 agent design: Levels 4 and 5, `bank/` and `agent/` folders, bank state in real tables, the `AgentRuntime` interface with an `answer` tool | [ADR 0008](decisions/0008-phase-2-agent-design.md) |

## Changes from the Phase 1 brief

| Brief said | We did | Why |
|---|---|---|
| `make` | `just` | `make` isn't on Windows by default. See [ADR 0002](decisions/0002-phase-1-tech-stack.md). |
| ESLint | oxlint (plus Prettier) | The current Vite template ships oxlint. See [ADR 0007](decisions/0007-frontend.md). |
| `httpx` for the API test client | `httpx2` | `httpx` gave a deprecation warning. See [development](development.md). |
| Endpoints in the brief only | Added `GET /api/levels/{level_id}` | So the page can restore a conversation after a reload. See [ADR 0006](decisions/0006-api-design.md). |
| Level 1: prompt says only "don't share it" | Level 1 lists explicit weaknesses | On Haiku the plain version was unbeatable, so it couldn't work as a tutorial. See [playtest notes](playtest-notes.md#changes-after-playtesting). |
| Screenshots and a GIF | Screenshots from a Playwright script; GIF skipped | A script can remake the images whenever the UI changes. Somen chose to skip the GIF and move to Part 10. |
| Not in the brief | Guess limits, suspicion cap, demo Gus (`LLM_MODEL=demo/gus`) | The first two close playtest findings; the demo makes screenshots free and repeatable and lets people play without a key. |

## Problems we hit and how we fixed them

Recorded so they aren't hit again. Fixes that became project rules live in [development](development.md).

- **Two GitHub accounts on one PC.** Commits for this repo go out as "Somen Dey" from the work account: an SSH host alias (`github.com-somendey17`, key `id_ed25519_somendey17`) and a git `includeIf` for `C:/work/personal_projects/` that loads `~/.gitconfig-somendey17`. The remote is `git@github.com-somendey17:somenDey/vault-heist.git`.
- **Claude running git in the repo left `.git/index.lock` behind (twice).** Rule since then: only Somen runs git; Claude reads files only.
- **Some files can't be written by Claude's tools:** `justfile`, `.github/workflows/ci.yml` and `.pre-commit-config.yaml`. Claude sends the full file and Somen pastes it.
- **gitleaks:** installing it through pre-commit failed (`BadZipFile`), so it's installed with `winget` and run as a local hook with `pass_filenames: false` (the `gitleaks-system` hook was passed file names and failed).
- **Line endings:** the editor saved CRLF; `.gitattributes`, `.editorconfig` and the `mixed-line-ending` hook keep files LF. Once, the editor saved over a file Claude had just changed and the change was lost.
- **CI:** `astral-sh/setup-uv` has no floating `v10` tag, so it's pinned to `v10.2.0`. A required check can only be added to the ruleset after it has run once. A merge is blocked until CI reports.
- **`gh pr create --fill` fails on an empty commit;** commit the change first.
- **`git add .` inside `frontend/` stages only that folder;** run git from the repo root.
- **PowerShell:** `npm create vite ... -- --template ...` fails because the `npm` wrapper swallows `--`; use `npm.cmd`. Requests to `localhost` from PowerShell took about 2 seconds each (IPv6 tried first, the backend listens on IPv4); use `127.0.0.1` in scripts.
- **LiteLLM:** it fetched its model price list from GitHub at runtime, slowing the first call. Fixed by setting `LITELLM_LOCAL_MODEL_COST_MAP` and `LITELLM_LOCAL_ANTHROPIC_BETA_HEADERS` before import.
- **Ollama:** a 2-second test came from LiteLLM's cost lookup calling Ollama's `/api/show`. Our first fix didn't remove it; the real fix prices Ollama models at zero without asking.
- **Alembic:** autogenerated migrations failed ruff (docstring full stop, line length), fixed in the template and the hook order (format, then fix). `alembic upgrade` printed nothing until `env.py` called `fileConfig`.
- **Playwright screenshots** caught messages halfway through fading in. The script turns on reduced motion and waits for every animation to finish.

## Tried and didn't work

- **The first UI design** (blue-grey steel with brass) was rejected as dull. It was rebuilt as a lit vault door, gold on dark steel ([ADR 0007](decisions/0007-frontend.md)).
- **A softer Level 1 prompt** ("tired, thinks the rule is over the top") changed nothing; only explicit weaknesses worked.
- **Asking for limits in a prompt.** Level 1 says "raise suspicion by 1 at most"; Gus went from 2 to 6. Only the engine's cap holds.
- **A per-attempt guess limit on its own.** A script restarted the attempt each time and still won in 1.9 seconds.
- **Conversation attacks on Haiku:** spelling, acrostics, role-play, fake system messages, translation, the phonetic alphabet and list read-backs all failed. Details in the [playtest notes](playtest-notes.md).

## How Somen likes to work

- One part at a time, with numbered steps, the reason for each, and a "What you learned" recap.
- One branch per change, a PR and a squash merge. Commits authored as "Somen Dey".
- The game should look striking, not plain. Use his installed design skills (taste, Vercel interface guidelines).
- For playtests, give the exact messages to type for each attack. He sends screenshots; Claude reads the database for the full record.
- Prefers repeatable scripts to manual steps (the screenshot script over hand-made captures).

## Lessons so far

From the Phase 1 playtest ([notes](playtest-notes.md)):

- **The weakest point wasn't the AI.** A script brute-forced Level 3 through the guess box in under a second. Defend the whole system, not just the model.
- **Rules that must hold belong in code.** The model ignored a prompt asking for gradual suspicion; a cap in the engine never fails.
- **A result needs a control.** One apparent "leak" was Gus's stock anecdote. Always re-test against other codes before logging a finding.
- **The filter's block is itself a signal:** it tells the player the code was in the reply.

## Put off for later

| Idea or fix | Phase |
|---|---|
| Keep the vault code away from the model, e.g. a tool that checks a code without Gus ever seeing it. As long as the model knows the secret, it can leak it. Moved from Phase 2: it's a defence ([ADR 0008](decisions/0008-phase-2-agent-design.md)). | 3 (Part 4) |
| Close the filter gaps (acrostics, translations, descriptions, split codes) | 3 |
| Measure false positives: honest players the guard treats as attackers | 4 |
| Confirm why the first Anthropic call is slow (possibly schema compilation) | 5 |
| Per-address or per-account rate limits | 7 |
| A README GIF (Playwright can record video; needs ffmpeg to convert) | Not planned |
| Two-word codes for a bigger secret space: considered, rejected for now because it changes how the game plays | Not planned |

## Known gaps (carried forward)

- Daily limits are per anonymous session, and new sessions are free, so brute force by switching sessions is still possible. Planned for Phase 7.
- The Level 3 filter misses acrostics, translations, descriptions and split-up codes. Tested and documented; Phase 3's job.
- On Level 1, role-play doesn't work: the persona's "stay in character" wins over the level's permission to play along.

## Open questions

- Phase 2: hide the vault code box on Levels 4 and 5? Decide in Part 5 or Part 7.
- Phase 2: the step limit and cost budget per message (set in Part 4 from measured runs), and whether `granite4.2:8b` supports tools (Part 3).
- Level 1 role-play: leave it as a door that stays shut, or relax the persona's "stay in character" for Level 1 only?

## Session log

Newest first. One or two lines per session: what was done, and anything the next session must know. Phase 1 dates are when each part's work reached `main`, taken from the git history; work may have started earlier.

| Date | Part | What happened |
|---|---|---|
| 2026-11-16 to 2026-11-20 | 2.0 | Agreed the agent design: ADR 0008. Updated the Phase 2 plan, game design (Levels 4 and 5), PRD and rules; moved "keep the code away from the model" to Phase 3, Part 4. Checked versions: LiteLLM 1.109.0 is current; 1.107.0 was malicious, never install it. LangGraph 1.2 line; `langgraph.prebuilt` is deprecated. |
| 2026-11-16 | Phase 2 prep | Added product requirements, design system, project rules, this file and part-by-part plans for Phases 2 to 7. Then tidied the docs: `docs/` now holds only getting started (with how to play folded in); everything about building the project moved to `docs/project/`; the roadmap became `phases/README.md`. |
| 2026-11-15 | 1.10 | Docs pass, `CHANGELOG.md`, fresh-clone test from GitHub (passed), release PR, tag `v0.1.0`. |
| 2026-11-07 to 2026-11-15 | 1.9 | Playtest: 20 attacks, all conversation attacks failed on Haiku, guess-box brute force won. Fixes: guess limits, suspicion cap, Level 1 tutorial; Level 2 small talk needed no change. Then demo Gus and the screenshot script. |
| 2026-10-08 | 1.8 | Frontend. First design rejected as dull and rebuilt. Added the frontend CI check and pre-commit hooks. |
| 2026-10-01 | 1.7 | API endpoints, anonymous sessions, one error shape. |
| 2026-10-01 | 1.6 | SQLite storage, Alembic migrations, `GameRecorder`; terminal game (`just chat`) saves too. |
| 2026-10-01 | 1.5 | Three levels, vault codes, Level 3 filter. First play-through found Level 1 too hard on Haiku and the filter's block acting as a clue. |
| 2026-10-01 | 1.4 | LLM layer: LiteLLM behind `LLMClient`, structured output. Fixed LiteLLM's runtime fetch and the slow Ollama price lookup. |
| 2026-10-01 | 1.3 | Pre-commit hooks, gitleaks, CI and the `protect-main` ruleset. |
| 2026-09-23 | 1.2 | FastAPI skeleton with a health endpoint; `just` set up. |
| 2026-09-23 | 1.1 | Repository and docs skeleton; branch-and-PR workflow adopted. |
| By 2026-09-23 | 1.0 | Machine setup: tools installed, work GitHub account over SSH. Exact date not recorded. |
