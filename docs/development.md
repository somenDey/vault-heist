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
| Your editor | ruff and mypy (with the extensions) | As you type |
| **pre-commit hooks** | File hygiene, secret scan, ruff, mypy | On every `git commit` |
| **CI** (GitHub Actions) | `just check` (lint, types, tests) and a full-history secret scan | On every push to a PR and to `main` |

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
- **ruff check / ruff format / mypy:** the same checks as `just lint` and `just typecheck`, run through `uv` so they use the versions in `uv.lock`.

If a hook **fixes** something (whitespace, formatting), the commit stops so you can review the change. Run `git add` again and re-commit. If a hook **fails**, fix the problem and commit again.

Other useful commands:

```powershell
pre-commit run --all-files     # run every hook on every file
pre-commit autoupdate          # bump hook versions (review the diff)
```

Never skip hooks with `--no-verify`. If a hook is wrong, fix the hook.

### Continuous integration

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs two jobs on GitHub's Linux machines:

- **Backend:** installs uv and just, runs `just install` (which fails if `uv.lock` is out of date) and then `just check`.
- **Secret scan:** runs gitleaks over the full git history, so a secret committed without the local hook is still caught.

Both are **required status checks** on `main`: a PR can't be merged until both pass. The badge at the top of the README shows the latest result on `main`.

### If a secret is ever committed

Removing it in a later commit is **not** enough, because it stays in the git history. Revoke the key with the provider immediately, create a new one, and only then clean up the repository.

## Line endings

`.gitattributes` stores every text file with LF line endings, on every OS, so Windows and Linux CI always see identical files. `.editorconfig` tells your editor to use LF too.

## Running tasks

All common actions run through [`just`](https://just.systems/) from the repository root (see [ADR 0002](decisions/0002-phase-1-tech-stack.md)). Run `just` on its own to list them.

| Command | Does |
|---|---|
| `just install` | Install backend dependencies exactly as locked in `uv.lock` |
| `just dev` | Run the backend with auto-reload at http://localhost:8000 (API docs at `/docs`) |
| `just test` | Run all tests |
| `just lint` | Check style and formatting with ruff (changes nothing) |
| `just typecheck` | Check types with mypy (strict mode) |
| `just format` | Auto-format and auto-fix what ruff can |
| `just check` | Everything CI checks: lint, types and tests |

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

## Testing

Tests live in `backend/tests/`:

- `unit/`: one piece of logic in isolation, no HTTP.
- `api/`: endpoints, called through FastAPI's `TestClient`.

Rules:

- **Tests never read your `.env`.** The `settings` fixture in `conftest.py` builds settings with `_env_file=None`, so tests behave the same on every machine and in CI.
- **Tests never call a real LLM.** From Part 4, tests use a fake LLM client: no network, no cost.
- Name tests after the behaviour they check, e.g. `test_invalid_value_fails_at_startup`.

FastAPI's test client needs `httpx2` (the successor to `httpx` that Starlette now expects), installed as a dev dependency.

## Configuration

Settings are defined in `backend/app/core/config.py` as a typed `Settings` class. Each field is read from the environment variable of the same name, or from the `.env` file at the repository root. Real environment variables win over `.env`. An invalid value stops the app at startup with a clear error.

To add a setting: add a typed field with a default to `Settings`, add the variable to `.env.example`, and document it where it's used.

## Adding a level

_Added in Part 5._

## Recording a decision

For any significant technical choice, add an ADR in [`decisions/`](decisions/). Copy the template in [ADR 0001](decisions/0001-record-architecture-decisions.md) and use the next number.
