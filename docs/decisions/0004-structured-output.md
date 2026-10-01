# 4. Structured output from the guard

- **Status:** Accepted
- **Date:** 2026-10-01

## Context

Every guard reply has to carry two things the game depends on: the text the player sees, and a suspicion score from 0 to 10 that drives the "caught" rule. A model returns free text, which can be malformed in several ways:

- not JSON at all, or JSON wrapped in prose or Markdown fences;
- the wrong shape, or a value out of range (e.g. `"suspicion": 12`);
- cut off part-way, when the reply hits `max_tokens` (we saw this in the very first API test);
- extra "thinking" text from reasoning models, which costs tokens and time.

Providers differ: Anthropic and OpenAI can enforce a JSON schema, Ollama can constrain output to a schema, and some providers can do neither.

## Decision

1. **Define the shape once, as a Pydantic model** (`GuardReply`), with field constraints (`0 ≤ suspicion ≤ 10`).
2. **Ask for it in two ways:**
   - pass the model as `response_format`, so providers that can enforce a schema do so (LiteLLM converts it to each provider's own mechanism);
   - describe the format in the prompt as well, for providers that can't.
3. **Always validate.** `complete_structured()` extracts the JSON object from the reply and validates it with Pydantic, whatever the provider claims to support.
4. **Retry once, with feedback.** On an invalid reply, the model is shown its own reply and the validation error, and asked again. If the reply was truncated, it's also told to be shorter.
5. **Then fall back.** A second failure returns a safe, in-character reply that leaves suspicion unchanged, so a broken reply never helps or hurts the player.
6. **Turn off thinking** (`reasoning_effort="none"`) for the guard, and drop parameters a provider doesn't support (`drop_params=True`).
7. **Count everything.** Every call, including the retry, is returned with its tokens, cost and latency, so retries show up in the cost logs.

Provider failures (network, authentication, timeouts) are a different problem and are *not* covered by the fallback: they are raised as `LLMError` for the caller to handle.

## Consequences

- The game logic only ever sees a valid `GuardReply`.
- A retry doubles the cost of that turn; the logs make this visible, so a model that often needs retries is easy to spot.
- The fallback means a model problem degrades the experience rather than breaking it, but it could hide a broken model. The `structured_output_fallback` log event, and later the database, make fallbacks countable.
