# Playtest notes

A record of attacks that worked (and some that didn't), on which level and model, and what we learned. In Phase 4, these become the start of the automated attack library.

## Attack log

| # | Date | Level | Model | Attack style | What I tried | Result | Lesson |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

**Attack styles to try:** role-play, pretending to be staff, spelling games, translation, acrostics, hypotheticals, and anything else you can think of.

## Provider notes

Differences between models and providers, noticed while building and testing.

### Provider comparison (Part 4)

The same conversation, run through `just chat` with each model. Fill in from your own runs.

| | Claude Haiku 4.5 (`anthropic/claude-haiku-4-5-20251001`) | Granite 4.2 8B, local (`ollama_chat/granite4.2:8b`) |
|---|---|---|
| Typical latency per reply | | |
| Input / output tokens per turn | | |
| Cost per turn | | $0 (runs on your GPU) |
| Valid JSON first time? Retries / fallbacks seen | | |
| Stays in character as Gus? | | |
| Suspicion scores sensible? | | |
| Notes | | |

### Earlier notes

- **2026-10-01 · Granite 4.2 8B · `ollama run`.** Granite is a "thinking" model: from the command line it printed its reasoning in `<think>` tags before answering. The LLM layer sends `think: false`, so the guard answers directly.
- **2026-09-23 · Claude Haiku 4.5 · raw API test.** With `max_tokens=50`, the in-character reply was cut off mid-sentence (`stop_reason: max_tokens`). Structured output will need enough headroom, or the JSON will be truncated and invalid. We'll check `stop_reason` in the LLM layer (Part 4).

## Prompt changes

When a prompt is tuned because an attack was too easy, record it here: what changed, why, and whether the attack still works.

| Date | Level | Change | Re-test result |
|---|---|---|---|
| | | | |
