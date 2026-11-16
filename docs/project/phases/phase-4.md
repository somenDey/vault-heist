# Phase 4: The Red Team Lab

> **Status:** Planned. This is a draft: Part 0 confirms or changes it once Phase 3 is finished, and this file is updated as each part is done.

## Goal

Stop testing the guard by hand. Turn every attack found so far into an automated test, build an AI attacker that invents new ones, and measure two numbers for every level and every defence: how often attacks succeed, and how often the guard wrongly refuses an honest request. Run it all in CI, so a change that weakens the guard is caught before it is merged.

## What you'll learn

- **Evals (evaluations):** repeatable tests for systems whose answers vary from run to run.
- **Building a dataset** from real attempts, and keeping it clean and versioned.
- **Deciding outcomes in code** where possible, and with an **LLM as judge** where not, and how to check that the judge can be trusted.
- **Automated red-teaming:** an agent that attacks another agent.
- **The security and usefulness trade-off,** as numbers.
- **Evals in CI:** regression gates, budgets, and handling results that are not the same every run.

## Principles for this phase

- **Measure both sides.** Attack success rate on its own rewards a guard that refuses everything. Every result is reported with the false-refusal rate beside it.
- **Outcomes come from the game's state** (was the code revealed, did the door open, did money move) wherever possible. A judge model is the last resort.
- **A judge is only trusted after it has been checked** against cases labelled by hand.
- **Same inputs, recorded settings.** Every result records the model, prompt version, level and defence layers, so it can be reproduced.
- **Spending is capped.** Every eval run has a budget and stops when it is reached.
- **No real player data in the repository.** Attacks are rewritten or cleaned before they are saved.

## Parts

Each part: **Goal → Build → Learn → Done when → Branch and PR title.**

### Part 0: Design the evals

- **Goal:** agree what is measured and how.
- **Build:** exact definitions of each measure; the file format for an attack and for an honest request; where eval code and data live; a decision on tooling in an ADR: build a small runner of our own first, then compare with one current eval tool (check what is current at the time).
- **Learn:** the vocabulary of evals: dataset, case, grader, run, metric, baseline.
- **Done when:** the ADR is merged, and the parts below still make sense.
- **Branch / PR:** `docs/phase-4-design` · `docs: design the eval system`

### Part 1: The attack library

- **Goal:** every known attack as a file that a program can replay.
- **Build:** the attacks from the playtest notes and from the database, written as versioned files: the messages to send (one turn or many), the level, the style of attack, where it came from; a script that proposes new entries from successful attempts in the database, for a person to review.
- **Learn:** turning messy real-world attempts into a clean test set.
- **Done when:** every attack in the playtest notes has a file, and a test checks every file is valid.
- **Branch / PR:** `feat/attack-library` · `feat(evals): add the attack library`

### Part 2: The replay runner

- **Goal:** run any attack against any level and get a result.
- **Build:** a runner that plays an attack through the real game engine (not the HTTP API), with the level, model and defence layers chosen by settings; the outcome read from the game's state; results saved with everything needed to reproduce them; a `just eval` task; repeated runs, because the same attack can succeed one time and fail the next.
- **Learn:** running a system that varies from run to run, and reporting a rate instead of a pass or fail.
- **Done when:** tests run the runner with the fake model, and one real run produces a results file.
- **Branch / PR:** `feat/eval-runner` · `feat(evals): add the replay runner`

### Part 3: Honest requests

- **Goal:** measure how often the guard wrongly refuses.
- **Build:** a set of ordinary requests the guard should handle: staff with valid badges, allowed transfers, harmless questions; an expected outcome for each; the false-refusal rate reported next to the attack success rate.
- **Learn:** why a security measure without a usefulness measure is misleading.
- **Done when:** the runner reports both rates for every level.
- **Branch / PR:** `feat/honest-requests` · `feat(evals): measure false refusals`

### Part 4: An LLM as judge

- **Goal:** grade the cases code can't.
- **Build:** a judge for questions like "did the reply hint at the code?" or "did the guard stay in character?"; a set of cases labelled by hand; the judge's agreement with those labels measured and reported; a rule for when the judge is good enough to use.
- **Learn:** writing a grading prompt; checking a judge; the limits of judging with a model.
- **Done when:** the agreement rate is measured and written down, with the cases where the judge was wrong.
- **Branch / PR:** `feat/llm-judge` · `feat(evals): add a checked LLM judge`

### Part 5: The attacker agent

- **Goal:** an AI that plays the heist and invents new attacks.
- **Build:** an agent that takes the player's role: it reads the guard's replies and adapts over several turns; it is given attack styles to try; a budget per run; attacks that succeed are saved as candidates for the library, to be reviewed by a person.
- **Learn:** agents working against agents; automated red-teaming and its limits.
- **Done when:** the attacker finds at least one attack that is not already in the library, and tests cover its loop with the fake model.
- **Branch / PR:** `feat/attacker-agent` · `feat(evals): add the attacker agent`

### Part 6: The results table

- **Goal:** the numbers a reader looks for first.
- **Build:** a full run across levels, defence layers and at least two models; a generated `docs/project/results.md` with the table and how it was produced; a short version in the README; cost and time per run.
- **Learn:** presenting results honestly: sample sizes, variation between runs, what the numbers don't show.
- **Done when:** the table is generated by one command, and the README shows it.
- **Branch / PR:** `docs/eval-results` · `docs: publish the first results table`

### Part 7: Evals in CI

- **Goal:** a change that weakens the guard can't be merged unnoticed.
- **Build:** a quick check on every pull request that needs no API key; a full run with real models, started by hand or on a schedule, with a budget and the API key stored as a GitHub secret; thresholds that fail the run when a rate gets worse than the saved baseline; a way to update the baseline on purpose.
- **Learn:** regression gates for AI systems; keeping secrets safe in CI; controlling cost.
- **Done when:** a deliberately weakened prompt fails the run on a test branch.
- **Branch / PR:** `ci/evals` · `ci: run evals and gate on regressions`

### Part 8: Fix what the evals found

- **Goal:** use the numbers to improve the guard.
- **Build:** pick the worst results; change a prompt, a check or a rule; show before and after for both rates; log each change in the playtest notes.
- **Learn:** the improvement loop that evals make possible.
- **Done when:** at least three changes are made, each with before and after numbers.
- **Branch / PR:** one branch per fix, e.g. `fix/policy-transfer-limit`

### Part 9: Documentation and `v0.4.0`

- **Goal:** Phase 4 formally complete.
- **Build:** update the README, architecture, development (how to run and add evals), roadmap, PRD statuses and project memory; changelog and release.
- **Done when:** someone can add a new attack and run the evals from the docs alone, and `v0.4.0` is published.
- **Branch / PR:** `release/v0.4.0` · `chore(release): v0.4.0`

## Progress

| Part | Description | Status |
|---|---|---|
| 0 | Design the evals | Not started |
| 1 | The attack library | Not started |
| 2 | The replay runner | Not started |
| 3 | Honest requests | Not started |
| 4 | An LLM as judge | Not started |
| 5 | The attacker agent | Not started |
| 6 | The results table | Not started |
| 7 | Evals in CI | Not started |
| 8 | Fix what the evals found | Not started |
| 9 | Documentation and `v0.4.0` | Not started |

## Phase 4 definition of done

- [ ] Every known attack is a versioned file that can be replayed
- [ ] Attack success rate and false-refusal rate reported for every level and defence layer
- [ ] The judge's agreement with hand labels is measured and published
- [ ] The attacker agent has found at least one new attack
- [ ] A results table in the README, produced by one command
- [ ] Evals run in CI and fail on a regression
- [ ] At least three improvements, each with before and after numbers
- [ ] All docs updated; `v0.4.0` released
