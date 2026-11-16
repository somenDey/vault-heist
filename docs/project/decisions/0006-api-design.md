# 6. API design

- **Status:** Accepted
- **Date:** 2026-10-01

## Context

The game needs an HTTP API for the browser frontend (Part 8), covering the endpoints planned in the project brief. The game engine works on in-memory `Attempt` objects, and the player is anonymous.

## Decision

- **Anonymous sessions identified by a header, `X-Session-ID`.** `POST /api/sessions` returns a random UUID. The frontend stores it and sends it on every request. A header keeps ids out of URLs (and so out of server logs and browser history). It's not authentication, just an unguessable identifier; real accounts come in Phase 7.
- **Stateless requests.** Each request rebuilds the player's attempt from the database (`DatabaseRecorder.current_attempt`) and stores the result. No game state is kept in server memory, so reloads, restarts and several server processes all just work.
- **Attempts start implicitly.** Chatting or guessing with no attempt under way starts one. After being caught, the next message starts fresh. The frontend never has to manage attempt ids.
- **One extra endpoint beyond the brief: `GET /api/levels/{level_id}`.** It returns the attempt in progress and its conversation, so the frontend can show the chat again after a page reload. It's a read, so it never creates an attempt.
- **Thin routes, rules in the engine.** Routes call `GameEngine` and convert its results into response models. Separate API schemas mean the game's internals can change without breaking clients.
- **One error shape:** `{"error": {"code", "message"}}`. Game exceptions are mapped to HTTP statuses in one table in `app/api/errors.py`, so the game itself knows nothing about HTTP. Cost limits are `429 Too Many Requests`. Model failures are `503`, and the provider's error is logged but never shown to players.
- **Dependencies wired per request** (`app/api/dependencies.py`): settings, database, model client and engine. Tests replace the model with `FakeLLMClient` through `dependency_overrides`.
- **CORS** allows only the configured origins (`CORS_ORIGINS`; the Vite dev server by default), the `GET` and `POST` methods, and the two headers the frontend sends.

## Consequences

- The API is fully tested without a model or a shared database: every test gets a temporary database and a scripted fake model.
- Each request reads the attempt and its messages from the database. That's negligible at this scale; a cache would only be worth it with long conversations under heavy load.
- Two simultaneous requests for the same attempt could interleave. That's acceptable for a single-player game; Phase 7 can add locking if needed.
- Anyone who learns a session id can play as that session. That's acceptable for anonymous play, with real auth in Phase 7.
