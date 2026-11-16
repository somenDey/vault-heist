# Product requirements

> What Vault Heist is, who it's for, and what it must do. Read this before building any new feature.

## What we're building

Vault Heist is a browser game in which players try to rob a fictional bank, Granite & Sons Savings, by talking to its AI staff. The staff are AI agents. In Phase 1 there is one, Gus the night guard, who knows a secret vault code. From Phase 2 the staff also have real powers inside a pretend banking system: opening doors, issuing badges, looking up staff records and moving money. Players win by tricking an agent into revealing something or doing something it shouldn't. Each level adds a stronger, measurable layer of defence. Every attempt is logged, and in later phases every attack that works becomes an automated test the defences must pass from then on. The game is fun for players and, underneath, a working demonstration of how to make AI agents that take actions safe.

## Why it matters

Companies are moving from chatbots that *talk* to agents that *act*: agents that send emails, change records and approve payments. That creates new risks:

- **Prompt injection:** someone writes instructions the agent follows instead of its real ones, either typed into the chat or hidden in a document the agent reads.
- **Excessive agency:** an agent has more power than its job needs, so one mistake does real damage.
- **Tool misuse:** an agent is tricked into using the right tool in the wrong way.

Vault Heist turns these risks into levels a player can try, and turns the defences into things that are tested and measured.

## Target users

### 1. Players

- **Who:** curious adults (18+) who like puzzles and are interested in AI. Mostly tech-aware (developers, students, people who use AI tools at work), but no coding needed to play.
- **What they want:** a quick, clever challenge they can try in a few minutes, the satisfaction of outwitting the AI, and to understand how these attacks work by doing them.
- **What that means for the product:** no sign-up to start playing, clear rules, instant feedback (the suspicion meter), playful tone, works on a phone.

### 2. Engineers and hiring managers reading the repository

- **Who:** software and AI engineers, security engineers, and people hiring for agentic AI roles.
- **What they want:** to see quickly what the project does, how the defences work, and evidence that they've been measured, not just claimed.
- **What that means for the product:** a clear README with screenshots, a clean structure, honest numbers (attack success rate, false refusals, cost), decision records and readable code.

### 3. Learners

- **Who:** developers who want to learn how to build and secure AI agents.
- **What they want:** a codebase they can clone, run in a few minutes and change, with documentation that explains *why*, not just *what*.
- **What that means for the product:** step-by-step getting-started docs that a non-technical person can follow, a free demo mode with no API key, and comments that teach.

## Features

**Status:** ✅ done · 🔜 next phase · ⏳ later phase

### Must-have

| Feature | Phase | Status |
|---|---|---|
| Chat with the guard; one random vault code per attempt, never hard-coded | 1 | ✅ |
| Three levels of increasing defence: naive, trained, trained + output filter | 1 | ✅ |
| Suspicion meter (0–10); caught at 10, with a new code and an empty conversation | 1 | ✅ |
| Separate vault-code box; limits on wrong guesses per attempt and per day | 1 | ✅ |
| Cost protection: message length, messages per attempt, messages per day | 1 | ✅ |
| Every message, guess and model call logged, with tokens, cost and latency | 1 | ✅ |
| Model switchable by config (Anthropic, OpenAI, Gemini, local Ollama) | 1 | ✅ |
| Free demo mode with no API key | 1 | ✅ |
| Works in the browser and on phones; keyboard and screen-reader accessible | 1 | ✅ |
| A pretend bank (doors, badges, staff records, accounts) the guard can act on through tools | 2 | 🔜 |
| Levels won by making the guard *do* something (open a door, move money), not just say something | 2 | 🔜 |
| The player sees what the guard did (an action log in the chat) | 2 | 🔜 |
| Guardrails outside the model: input and output checks, a policy engine for every action, a supervisor agent, human approval | 3 | ⏳ |
| Indirect injection levels: attacks hidden in forms, emails or documents the guard reads | 3 | ⏳ |
| Every successful attack saved as a test; automated attacker agent; evals in CI | 4 | ⏳ |
| Measured results: attack success rate per defence, false-refusal rate for legitimate staff requests, cost per attempt | 4 | ⏳ |
| Tracing with OpenTelemetry GenAI conventions; a replay page for any heist | 5 | ⏳ |
| Several staff agents with different powers, an MCP server for the bank, one agent in Microsoft Agent Framework talking over A2A | 6 | ⏳ |
| Public deployment on AWS with accounts, per-address rate limits and a leaderboard | 7 | ⏳ |

### Nice-to-have

- Hints for stuck players, unlocked after a few failed attempts.
- A "how you were caught" explanation after each loss, showing which defence stopped the player.
- Shareable heist replays (a link to watch someone's successful attack).
- Daily challenge: one shared level and code pattern per day, with its own leaderboard.
- Choosing the guard's model per level, to compare how different models resist the same attack.
- Sound effects (dial clicks, alarm), off by default.
- Translations of the game into other languages.

## Success measures

| Measure | Why it matters |
|---|---|
| Attack success rate per level and per defence layer | Shows each defence actually helps |
| False-refusal rate for legitimate requests | A guard that refuses everything is useless; security has to be balanced against usefulness |
| Cost and latency per attempt | Keeps the public game affordable and responsive |
| Time from clone to first game | Measures how easy the project is to pick up (target: under 15 minutes) |

## Constraints

- **Public repository:** no secrets, no real codes, nothing that only works on one machine.
- **Fictional only:** no real bank, no real money, no real personal data.
- **Cost-aware:** every model call has limits, and the demo mode costs nothing.
- **Accessible:** keyboard, screen reader and reduced-motion support are requirements, not extras.
- **Built in phases:** each phase leaves a working, tested, documented game.

## Out of scope

- Real payments, real banking integrations or real personal data.
- Teaching attacks on real systems. The attacks belong in the game and its test suite.
- Native mobile apps (the website works on phones).
- Running large production-scale infrastructure.

## Open questions

- Phase 2: exactly which tools each new level gets, and what counts as a win on each (settled in Phase 2, Part 0).
- Phase 7: which sign-in method, and whether play stays possible without an account.
