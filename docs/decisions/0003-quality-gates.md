# 3. Quality gates: pre-commit hooks and CI

- **Status:** Accepted
- **Date:** 2026-10-01

## Context

The project needs problems caught before they reach `main`: style and type errors, failing tests, and above all, leaked API keys. This is a public repository that handles paid API keys, so one leaked key costs real money.

Two design questions came up:

1. **How should the hooks run ruff and mypy?** The usual approach uses each tool's own pre-commit mirror, which installs a separate copy of the tool. That copy can drift from the version in `uv.lock`. For mypy it's worse: the mirror runs in an isolated environment without FastAPI or Pydantic, so strict type-checking of our code fails or has to be weakened.
2. **Which secret scanner?** It needs to run both locally (before a commit exists) and in CI (over the full history).

## Decision

- **pre-commit** runs on every commit, with:
  - general hygiene hooks from `pre-commit-hooks`, including `no-commit-to-branch` for `main`;
  - **gitleaks** for secrets, run from a locally installed gitleaks binary;
  - **local hooks** that run ruff and mypy through `uv run --directory backend`, so they use exactly the versions in `uv.lock` and the settings in `pyproject.toml`.
- **GitHub Actions CI** runs on every PR and push to `main`, with two jobs:
  - **Backend:** `just install` then `just check`, the same command developers run locally;
  - **Secret scan:** `gitleaks-action` over the full git history. It's free for personal accounts.
- Both CI jobs are required status checks in the `protect-main` ruleset.
- Tests run in CI, not in the pre-commit hooks, to keep commits fast.

## Consequences

- One source of truth for tool versions (`uv.lock`) and settings (`pyproject.toml`): the hooks, `just check` and CI can't disagree.
- Contributors need `uv` and `gitleaks` on their PATH for the hooks to work. We tried gitleaks' own pre-commit hook first, which builds gitleaks from source by downloading the Go toolchain. On the development machine that download arrived corrupted, and its `gitleaks-system` variant passes file names that the gitleaks CLI rejects. A locally installed binary (one `winget`/`brew` command) called from a local hook avoids both problems.
- Hook versions are pinned and need occasional bumping with `pre-commit autoupdate`.
- gitleaks-action would need a (free) licence key if the repository ever moves to a GitHub organisation.
