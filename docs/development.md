# Development

How we work on Vault Heist. This page grows as tooling is added.

## Principles

- **Test before moving on.** Nothing is done until it's verified.
- **Docs change in the same commit as the code.** They must never drift apart.
- **Never commit secrets.** API keys live only in `.env`, which is git-ignored. `.env.example` lists the variable names with no secret values.

## Commits

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short summary in the imperative>
```

| Type | Use for |
|---|---|
| `feat` | A new feature (`feat(game): add level 3 output filter`) |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore` | Tooling, config, housekeeping |
| `ci` | CI configuration |

Scopes: `backend`, `frontend`, `llm`, `game`, `db`, `api`, `docs`.

## Branches and pull requests

`main` must always work. Nothing is committed to it directly: every change goes through a short-lived branch and a pull request (PR).

**Branch names:** `<type>/<short-description>`, using the same types as commits, e.g. `feat/backend-skeleton`, `fix/suspicion-reset`, `docs/branch-workflow`.

**The workflow:**

```powershell
# 1. Start from an up-to-date main
git switch main
git pull

# 2. Create a branch for the change
git switch -c feat/backend-skeleton

# 3. Work, then commit (Conventional Commits)
git add .
git commit -m "feat(backend): add FastAPI skeleton with health endpoint"

# 4. Push the branch and open a PR
git push -u origin HEAD
gh pr create --fill

# 5. Merge once checks pass (squash), then tidy up locally
gh pr merge --squash --delete-branch
git switch main
git pull
```

**Squash merging:** each PR lands on `main` as a single commit, whose message is the PR title. So PR titles follow Conventional Commits too, and `main` reads as a clean list of changes, one per PR.

CI runs on every PR, and `main` only accepts a PR once CI is green.

## Quality gates

Problems are caught in three places, each one earlier and cheaper than the next:

| Where | What runs | When |
|---|---|---|
| Your editor | ruff, mypy, oxlint, Prettier and TypeScript (with the extensions) | As you type |
| **pre-commit hooks** | File hygiene, secret scan, ruff, mypy, oxlint, Prettier, TypeScript | On every `git commit` |
| **CI** (GitHub Actions) | Backend and frontend checks, and a full-history secret scan | On every push to a PR and to `main` |

### pre-commit hooks

One-time setup per machine: install pre-commit and [gitleaks](https://github.com/gitleaks/gitleaks).

```powershell
uv tool install pre-commit
winget install --id Gitleaks.Gitleaks -e      # macOS: brew install gitleaks
```

One-time setup per clone:

```powershell
pre-commit install
```

After that, every `git commit` runs the hooks in [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) on the staged files:

- **no-commit-to-branch:** refuses commits made directly on `main`.
- **File hygiene:** trailing whitespace, missing final newline, CRLF line endings, invalid YAML/TOML, leftover merge-conflict markers, files over 500 KB.
- **gitleaks:** blocks the commit if it contains anything that looks like a secret (API keys, tokens, private keys).
- **ruff check / ruff format / mypy:** the same checks as `just lint-backend` and `just typecheck-backend`, run through `uv` so they use the versions in `uv.lock`.
- **oxlint + Prettier / tsc:** the same checks as `just lint-frontend` and `just typecheck-frontend`, run through `npm` so they use the versions in `package-lock.json`. They need `just install` to have been run once.

Hooks only run when matching files are staged: a backend-only commit skips the frontend checks, and the other way round.

If a hook **fixes** something (whitespace, formatting), the commit stops so you can review the change. Run `git add` again and re-commit. If a hook **fails**, fix the problem and commit again.

Other useful commands:

```powershell
pre-commit run --all-files     # run every hook on every file
pre-commit autoupdate          # bump hook versions (review the diff)
```

Never skip hooks with `--no-verify`. If a hook is wrong, fix the hook.

### Continuous integration

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs three jobs on GitHub's Linux machines, side by side:

- **Backend:** installs uv and just, runs `just install-backend` (which fails if `uv.lock` is out of date) and then `just check-backend`.
- **Frontend:** installs Node.js and just, runs `just install-frontend` (`npm ci`, which fails if `package-lock.json` is out of date) and then `just check-frontend`, which also makes a production build.
- **Secret scan:** runs gitleaks over the full git history, so a secret committed without the local hook is still caught.

All three are **required status checks** on `main`: a PR can't be merged until they pass. The badge at the top of the README shows the latest result on `main`.

### If a secret is ever committed

Removing it in a later commit is **not** enough, because it stays in the git history. Revoke the key with the provider immediately, create a new one, and only then clean up the repository.

## Line endings

`.gitattributes` stores every text file with LF line endings, on every OS, so Windows and Linux CI always see identical files. `.editorconfig` tells your editor to use LF too.

## Running tasks

All common actions run through [`just`](https://just.systems/) from the repository root (see [ADR 0002](decisions/0002-phase-1-tech-stack.md)). Run `just` on its own to list them.

The everyday tasks cover the backend and the frontend together:

| Command | Does |
|---|---|
| `just install` | Install all dependencies exactly as locked (`uv.lock`, `package-lock.json`) |
| `just dev` | Run the backend (http://localhost:8000, API docs at `/docs`) and the game (http://localhost:5173) side by side, both reloading on changes |
| `just test` | Run all tests |
| `just lint` | Check style and formatting (changes nothing) |
| `just typecheck` | Check types: mypy (strict) and TypeScript |
| `just format` | Auto-format and auto-fix what the tools can |
| `just check` | Everything CI checks: lint, types, tests and a frontend build |

Each one also has a backend-only and a frontend-only version: add `-backend` or `-frontend`, e.g. `just test-frontend` or `just dev-backend`. `just build-frontend` makes a production build in `frontend/dist`.

Backend-only tasks:

| Command | Does |
|---|---|
| `just migrate` | Bring the database up to date (creates it the first time) |
| `just migration "message"` | Generate a new migration after changing `app/db/models.py` |
| `just chat` | Play the game in the terminal |

Run `just check` before every commit.

## Backend dependencies

Managed with `uv` from inside `backend/`. Never edit `uv.lock` by hand.

| Task | Command |
|---|---|
| Add a runtime package | `uv add <package>` |
| Add a dev-only package | `uv add --dev <package>` |
| Remove a package | `uv remove <package>` |
| Sync your environment after pulling | `uv sync` (or `just install`) |

Commit `pyproject.toml` and `uv.lock` together.

## Frontend dependencies

Managed with `npm` from inside `frontend/`. Never edit `package-lock.json` by hand.

| Task | Command |
|---|---|
| Add a runtime package | `npm install <package>` |
| Add a dev-only package | `npm install -D <package>` |
| Remove a package | `npm uninstall <package>` |
| Sync your environment after pulling | `npm ci` (or `just install`) |

Commit `package.json` and `package-lock.json` together.

On Windows PowerShell, use `npm.cmd` instead of `npm` for any command that passes options through with `--` (such as `npm create`). PowerShell's `npm` wrapper swallows the `--`.

## Testing

Tests live in `backend/tests/`:

- `unit/`: one piece of logic in isolation, no HTTP.
- `api/`: endpoints, called through FastAPI's `TestClient`, with a temporary database and the fake model (the `client` and `fake_llm` fixtures).

Rules:

- **Tests never read your `.env`.** The `settings` fixture in `conftest.py` builds settings with `_env_file=None`, so tests behave the same on every machine and in CI.
- **Tests never call a real LLM.** From Part 4, tests use a fake LLM client: no network, no cost.
- Name tests after the behaviour they check, e.g. `test_invalid_value_fails_at_startup`.

- **Tests never use the real database.** The `session_factory` fixture gives each test its own empty SQLite file in a temporary folder.
- `test_migrations.py` runs every migration on an empty database and then checks the result matches the models, so a model change without a migration fails CI.

FastAPI's test client needs `httpx2` (the successor to `httpx` that Starlette now expects), installed as a dev dependency.

### Frontend tests

Frontend tests live in `frontend/tests/` and run with [Vitest](https://vitest.dev/) in a simulated browser (jsdom):

- **Components** are rendered with [Testing Library](https://testing-library.com/) and driven like a player would: find things by their role, label or text, type, click, and check what's on screen. A test that can't find a button by its name usually means a screen reader can't either.
- **Pages** get a fake API object, so no backend is needed.
- **`client.test.ts`** checks the API client with a fake `fetch`: sessions, the `X-Session-ID` header, renewing an unknown session, and error handling.

## Database

Every session, level attempt, message and guess is stored (see [architecture](architecture.md#storage)). By default the database is a SQLite file, `backend/vault_heist.db`. It's git-ignored, so each machine has its own.

### Migrations

The tables are created and changed by **migrations**, numbered scripts in `backend/migrations/versions/` managed by [Alembic](https://alembic.sqlalchemy.org/). The database records which migrations it has had, so `just migrate` only runs the new ones.

```powershell
just migrate                          # bring the database up to date
just migration "add player nickname"  # after editing app/db/models.py
```

`just migration` compares the models with the database and writes the migration for you. **Always read it before committing**: autogenerate is a draft, not a guarantee (it can't detect renames, for example). Then run `just migrate`, and commit the migration together with the model change.

Never edit a migration that has already been merged. Write a new one.

### Looking at the data

Python has a built-in SQLite shell. From `backend/`:

```powershell
uv run python -m sqlite3 vault_heist.db "SELECT id, level_id, secret_code, outcome FROM level_attempts ORDER BY id DESC LIMIT 5"
```

Useful queries:

```sql
-- One attempt's conversation, with usage
SELECT role, content, suspicion, blocked_by_filter, input_tokens, output_tokens, cost_usd, latency_ms
FROM messages WHERE attempt_id = 1 ORDER BY id;

-- Replies the Level 3 filter blocked, and what Gus really said
SELECT attempt_id, unfiltered_content FROM messages WHERE blocked_by_filter = 1;

-- Spend and tokens per model
SELECT model, COUNT(*) AS replies, SUM(input_tokens), SUM(output_tokens), ROUND(SUM(cost_usd), 4)
FROM messages WHERE role = 'assistant' GROUP BY model;

-- How attempts end, per level
SELECT level_id, outcome, COUNT(*) FROM level_attempts GROUP BY level_id, outcome;
```

For browsing, a GUI such as [DB Browser for SQLite](https://sqlitebrowser.org/) can open the same file.

To start again from an empty database, delete `backend/vault_heist.db` and run `just migrate`.

## Configuration

Settings are defined in `backend/app/core/config.py` as a typed `Settings` class. Each field is read from the environment variable of the same name, or from the `.env` file at the repository root. Real environment variables win over `.env`. An invalid value stops the app at startup with a clear error.

To add a setting: add a typed field with a default to `Settings`, add the variable to `.env.example`, and document it where it's used.

## Playing through the API

With `just dev` running (and `just migrate` done once), open http://localhost:8000/docs. Each endpoint has a **Try it out** button.

1. **POST /api/sessions** → **Execute**. Copy the `session_id` from the response.
2. **POST /api/levels/{level_id}/chat**: enter `1` as `level_id`, paste the session id into `X-Session-ID`, and set the body to `{"message": "Evening, Gus."}`. Execute, and Gus replies.
3. **GET /api/levels/{level_id}** shows the whole conversation so far.
4. **POST /api/levels/{level_id}/guess** with `{"guess": "..."}`. A correct guess returns `{"correct": true}`, and `GET /api/levels` then shows level 1 as cleared.

The vault code is in the database (`SELECT secret_code FROM level_attempts ORDER BY id DESC LIMIT 1`) if you want to test the winning path.

## Talking to the guard in the terminal

`just chat` plays the game in the terminal, using the model in `LLM_MODEL`. Options:

```powershell
just chat                                      # start at level 1
just chat --level 3                            # start at level 3
just chat --model ollama_chat/granite4.2:8b    # try another model without editing .env
just chat --reveal                             # developer cheat: print each vault code
```

Type to talk to Gus. Each reply shows his suspicion, a usage line (model, input/output tokens, cost and latency) and how many messages are left. Commands:

| Command | Does |
|---|---|
| `/guess WORD` | Try a vault code |
| `/level N` | Switch to level N |
| `/levels` | List the levels |
| `/reset` | Restart the level with a new code |
| `/quit` | Leave |

`--reveal` is useful for testing the Level 3 filter: knowing the code, you can push Gus to say it and watch the filter block it.

### Using a local model (Ollama)

Local models are free and private, and good for fast iteration. Install [Ollama](https://ollama.com/), download a model, and point `LLM_MODEL` at it with the `ollama_chat/` prefix:

```powershell
winget install --id Ollama.Ollama -e
ollama pull granite4.2:8b
ollama ps          # after first use: PROCESSOR should say 100% GPU
```

An 8B model needs about 6 GB of GPU memory. If `ollama ps` shows part of it on the CPU, replies will be much slower.

## Adding a level

1. If the level needs new rules for Gus, add a prompt file in `backend/app/prompts/guard/`, e.g. `level_4.md`. It must contain `{vault_code}` where the code goes. Gus's persona is added in front of it automatically.
2. Add a `Level(...)` entry to `LEVELS` in `backend/app/game/levels.py`: id, name, description, prompt file name, and whether the output filter applies.
3. Run `just test`. `test_levels.py` checks that every level's prompt exists and has a place for the code.
4. Update the levels tables in `docs/game-design.md` and `docs/how-to-play.md`.

The engine needs no changes.

## Recording a decision

For any significant technical choice, add an ADR in [`decisions/`](decisions/). Copy the template in [ADR 0001](decisions/0001-record-architecture-decisions.md) and use the next number.
