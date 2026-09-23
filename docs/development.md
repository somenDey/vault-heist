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

## Branches

- `main` must always work.
- Until CI exists (Part 3), work is committed directly to `main`.
- From Part 3 onward: create a short-lived branch per change (e.g. `feat/level-3-filter`), open a pull request, and merge once CI is green.

## Line endings

`.gitattributes` stores every text file with LF line endings, on every OS, so Windows and Linux CI always see identical files. `.editorconfig` tells your editor to use LF too.

## Running tasks

All common actions will run through [`just`](https://just.systems/) (see [ADR 0002](decisions/0002-phase-1-tech-stack.md)):

| Command | Does | Available from |
|---|---|---|
| `just dev` | Run the app locally | Part 2 |
| `just test` | Run all tests | Part 2 |
| `just lint` | Lint and type-check | Part 2 |
| `just format` | Auto-format the code | Part 2 |

## Testing

_Added in Part 2._

## Adding a level

_Added in Part 5._

## Recording a decision

For any significant technical choice, add an ADR in [`decisions/`](decisions/). Copy the template in [ADR 0001](decisions/0001-record-architecture-decisions.md) and use the next number.
