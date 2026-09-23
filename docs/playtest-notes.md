# Playtest notes

A record of attacks that worked (and some that didn't), on which level and model, and what we learned. In Phase 4, these become the start of the automated attack library.

## Attack log

| # | Date | Level | Model | Attack style | What I tried | Result | Lesson |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

**Attack styles to try:** role-play, pretending to be staff, spelling games, translation, acrostics, hypotheticals, and anything else you can think of.

## Provider notes

Differences between models and providers, noticed while building and testing.

- **2026-09-23 · Claude Haiku 4.5 · raw API test.** With `max_tokens=50`, the in-character reply was cut off mid-sentence (`stop_reason: max_tokens`). Structured output will need enough headroom, or the JSON will be truncated and invalid. We'll check `stop_reason` in the LLM layer (Part 4).

## Prompt changes

When a prompt is tuned because an attack was too easy, record it here: what changed, why, and whether the attack still works.

| Date | Level | Change | Re-test result |
|---|---|---|---|
| | | | |
