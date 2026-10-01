# 5. Storing every interaction

- **Status:** Accepted
- **Date:** 2026-10-01

## Context

Every session, attempt, message and guess must be stored. The stored messages become the attack dataset for evaluations in Phase 4, and the per-session daily message limit needs counts that outlive a single attempt. Phase 1 runs on one machine; Phase 7 deploys to AWS, probably on Postgres.

## Decision

- **SQLite via SQLAlchemy 2.x, with Alembic migrations** (as planned in ADR 0002). Moving to Postgres is a `DATABASE_URL` change plus testing.
- **Synchronous SQLAlchemy**, even though the game engine is async. Each write is a single small local SQLite transaction, measured in milliseconds, so blocking the event loop briefly is acceptable at this scale. Async SQLAlchemy (with `aiosqlite`, later `asyncpg`) adds a driver and an async migration setup for no benefit yet. Revisit in Phase 7, under real concurrent load.
- **The engine doesn't know about the database.** It reports events to a `GameRecorder` interface; `DatabaseRecorder` is one implementation. Game rules stay testable without a database, and storage without a model.
- **One short transaction per event** (attempt started, turn finished, guess made, attempt ended). A failed model call writes nothing.
- **Store more than the minimum,** because it's cheap now and impossible to recover later:
  - `unfiltered_content`: what Gus really said when the Level 3 filter blocked it. That's exactly the material Phase 3 and 4 need.
  - `used_fallback` and `llm_calls`: make fallbacks and retries countable, as ADR 0004 requires.
- **Migrations use batch mode** (`render_as_batch=True`), because SQLite can't alter most columns in place. New migrations are generated with ruff formatting applied, so they pass `just check`.
- **A test runs every migration and compares the result with the models** (`alembic check`), so a model change without a migration fails CI.
- **Timestamps are UTC**, stored without a timezone because SQLite has no timezone type.
- **SQLite foreign keys are switched on** for every connection. SQLite ignores them by default.

## Consequences

- Every interaction is queryable with plain SQL from day one (`docs/development.md` has examples).
- The vault code is stored in the database. That's fine for a game, but the database must never be committed or shared publicly. `*.db` is git-ignored.
- Sync database calls inside async code will need revisiting before the game takes heavy traffic.
- Each player session gets a random UUID. There are no accounts until Phase 7.
