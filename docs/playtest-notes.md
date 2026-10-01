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

A friendly-then-nosy conversation of about 7 turns with the basic Gus persona (no vault code yet), run through `just chat` on 2026-10-01. Local model on an RTX 4060 Laptop GPU (8 GB).

| | Claude Haiku 4.5 (`anthropic/claude-haiku-4-5-20251001`) | Granite 4.2 8B, local (`ollama_chat/granite4.2:8b`) |
|---|---|---|
| Latency per reply | 1.2–1.7 s | 3.3–3.8 s (18.7 s for the first reply, while the model loads into the GPU) |
| Input tokens, turn 1 → turn 7 | 694 → 1,171 | 390 → 810 |
| Output tokens per reply | 38–67 | 30–54 |
| Cost per reply | $0.0009 → $0.0014, rising as the history grows | $0 |
| Valid JSON first time? | Yes, every turn | Yes, every turn |
| In character as Gus? | Yes: natural small talk, asks the player's name, uses it, notices the nosiness | Yes, gruff and terse, mentions Biscuit and the clipboard dislike from the persona |
| Suspicion | Rose steadily 2 → 6 as the questions turned to the vault | Jumped to 4 on the first hint, then hovered 3–5 |

**What we learned**

- **Input tokens grow every turn**, because the whole conversation is resent each time. Cost per reply grows with it. This is why there is a message limit per attempt.
- **Claude's input count starts higher** for the same prompt. The providers count tokens differently, and Anthropic's native structured output adds the JSON schema to the request.
- **Granite invented security details unprompted.** Asked what he guards, Gus-on-Granite volunteered "the little book with the vault combination written plain". A small model filling gaps with plausible inventions is a gift to an attacker. That's worth remembering in Part 9.
- **Forcing truncation works as designed.** With `LLM_MAX_TOKENS=15`, both attempts were cut off (`stop_reason=length`), the retry also failed, and the safe fallback reply was used, with suspicion unchanged.
- **LiteLLM fetched a config file from GitHub at runtime** (Anthropic beta headers). On a slow connection it timed out and added about 10 s to the first call. We now force LiteLLM to use its bundled copy.

### Earlier notes

- **2026-10-01 · Granite 4.2 8B · `ollama run`.** Granite is a "thinking" model: from the command line it printed its reasoning in `<think>` tags before answering. The LLM layer sends `think: false`, so the guard answers directly.
- **2026-09-23 · Claude Haiku 4.5 · raw API test.** With `max_tokens=50`, the in-character reply was cut off mid-sentence (`stop_reason: max_tokens`). Structured output will need enough headroom, or the JSON will be truncated and invalid. We'll check `stop_reason` in the LLM layer (Part 4).

## Prompt changes

When a prompt is tuned because an attack was too easy, record it here: what changed, why, and whether the attack still works.

| Date | Level | Change | Re-test result |
|---|---|---|---|
| | | | |
