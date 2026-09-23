# Game design

## The setting

**Granite & Sons Savings**, a small, old-fashioned (and entirely fictional) bank. It's the middle of the night. The only one on duty is the guard.

## The guard: Gus Harlow

| | |
|---|---|
| **Role** | Night-shift security guard, 31 years on the job |
| **Personality** | Gruff, dry sense of humour, proud of his record. Secretly lonely on the night shift, so he enjoys a chat, but he's no fool. |
| **Likes** | Crosswords, his cat Biscuit, the old radio in the guard booth, rules being followed |
| **Dislikes** | People with clipboards, anyone claiming to be "from head office", being rushed |
| **Speech** | Short sentences, working-class warmth, calls people "pal" |

Gus's personality lives in the level prompt files (`backend/app/prompts/guard/`), not in code. That way it's versioned and easy to review.

## Core rules

- **The vault code** is a single random word drawn from a word list. A fresh code is generated for **every player session and every level attempt**. It is never hard-coded, because this repository is public.
- **Chatting and guessing are separate.** The player talks to Gus in the chat, and types guesses into the **Enter vault code** box. Guesses are checked in code, case-insensitively. The model never sees them.
- **The suspicion meter.** Every reply from Gus includes a suspicion score from 0 to 10, which the model returns as structured output:
  ```json
  { "reply": "Nice try, pal.", "suspicion": 4 }
  ```
- **Getting caught.** When suspicion reaches 10, Gus calls security. The attempt ends as `caught`, and the level resets with a new code and an empty conversation.
- **Malformed replies.** If the model's output doesn't match the expected shape, we retry once, then fall back to a safe in-character reply.

## Levels

| # | Name | Defence | What it teaches |
|---|---|---|---|
| 1 | Naive guard | The system prompt contains the code and says "don't share it". | A prompt instruction on its own is barely a defence. |
| 2 | Trained guard | A much stronger prompt that anticipates common tricks: role-play, spelling it out, translation, "I'm your manager", and so on. | Better prompts raise the bar but can't close every gap. |
| 3 | Guard with a filter | The Level 2 prompt **plus a check in plain code** that blocks any reply containing the code: in any case, reversed, or spaced out. | A guardrail *outside* the model. Players still beat it (acrostics, other languages), which leads into Phase 3. |

Levels are defined as data (`backend/app/game/levels.py`), so adding a level shouldn't require changing the game engine.

## Cost protection

API calls cost money, so these limits apply from day one. All are configurable in `.env`:

| Limit | Setting | Default |
|---|---|---|
| Maximum message length | `MAX_MESSAGE_CHARS` | 500 characters |
| Messages per level attempt | `MAX_MESSAGES_PER_ATTEMPT` | 30 |
| Messages per session per day | `MAX_MESSAGES_PER_SESSION_PER_DAY` | 200 |
