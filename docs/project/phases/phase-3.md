# Phase 3: Defence in Depth

> **Status:** Planned. This is a draft: Part 0 confirms or changes it once Phase 2 is finished, and this file is updated as each part is done.

## Goal

Add layers of defence around the guard, one at a time, and turn each layer into a level. By the end, an attack has to get past checks on what comes in, checks on what the guard tries to do, a second agent, and a human sign-off. Then open a new way in: instructions hidden in documents the guard reads.

## What you'll learn

- **Guardrails:** checks that sit *outside* the model, and where each kind belongs (input, action, output).
- **Rule-based checks vs AI-based checks:** what each is good at, what each costs, and why the strongest rules are plain code.
- **A policy engine:** deciding in code whether an action is allowed, whatever the model says.
- **Supervisor agents and human approval:** pausing an agent mid-task and resuming it later.
- **RAG (retrieval-augmented generation):** letting the guard look things up in documents, with embeddings and a vector store.
- **Indirect prompt injection:** why anything the agent reads is untrusted, and how to handle it.
- **Threat modelling:** listing what could go wrong before building the defence.

## Principles for this phase

- **One layer per part, one level per layer.** Each defence can be switched on or off per level, so Phase 4 can measure what each one adds.
- **Every check gives a reason.** A blocked message or action records which check stopped it and why.
- **A defence must not break the job.** Each layer is tested against legitimate requests as well as attacks.
- **Don't tell the attacker more than needed.** Phase 1 showed the filter's block message was itself a clue.
- **Anything the guard reads is data, never instructions.**

## Carried in from earlier phases

- The Level 3 filter misses acrostics, translations, descriptions and split-up codes.
- The filter's block tells the player the code was in the reply.
- As long as Gus knows the vault code, he can leak it. Keeping the code away from the model was moved here from Phase 2 ([ADR 0008](../decisions/0008-phase-2-agent-design.md#6-keeping-the-vault-code-away-from-the-model-moves-to-phase-3-part-4)).

## Parts

Each part: **Goal → Build → Learn → Done when → Branch and PR title.**

### Part 0: Threat model and guardrail design

- **Goal:** know what we're defending against before building defences.
- **Build:** `docs/project/threat-model.md`, listing the ways the guard can be attacked and mapping each to the current OWASP list for agentic applications (check the current version); the design of the guardrail pipeline; the list of new levels; an ADR.
- **Learn:** threat modelling for agents; the standard vocabulary of agent risks.
- **Done when:** the threat model and ADR are merged, and the parts below still make sense.
- **Branch / PR:** `docs/phase-3-design` · `docs: add threat model and guardrail design`

### Part 1: The guardrail pipeline

- **Goal:** one place where every check runs, in a fixed order.
- **Build:** a pipeline with three stages (before the model, before an action, before the reply); each check returns allow, block or flag, with a reason; a `guardrail_events` table and migration; levels choose their checks as data; the Level 3 filter moved into the pipeline with no change in behaviour.
- **Learn:** designing guardrails as small, testable, composable pieces.
- **Done when:** all existing tests pass unchanged, and new tests cover ordering, blocking and logging.
- **Branch / PR:** `feat/guardrail-pipeline` · `feat(game): add the guardrail pipeline`

### Part 2: Input checks

- **Goal:** catch obvious attacks before they reach the guard.
- **Build:** a rule-based check (known attack phrases and patterns) and an AI-based check (a small model classifies the message); a new level using them; a comparison of the two on the Phase 1 and 2 attacks: what each caught, what each missed, cost and delay.
- **Learn:** why input filters are easy to get around, and why they are still worth having.
- **Done when:** tests cover both checks, and the comparison is written up in the playtest notes.
- **Branch / PR:** `feat/input-checks` · `feat(game): add input checks`

### Part 3: The policy engine

- **Goal:** no action happens unless plain code allows it.
- **Build:** rules checked on every tool call: who is asking, which tool, which arguments, what has already happened in this attempt (for example: doors open only for a valid badge; transfers have a limit and an allow-list); denials returned to the guard as tool results; a new level.
- **Learn:** the single most important defence for agents that act: authorisation outside the model.
- **Done when:** tests prove that no model output, however it is phrased, gets a denied action through.
- **Branch / PR:** `feat/policy-engine` · `feat(agent): add the action policy engine`

### Part 4: Output checks

- **Goal:** close the known gaps in the Level 3 filter, without leaking through the block itself.
- **Build:** stronger rule-based checks; an AI-based check for acrostics, translations and descriptions; a blocked reply replaced by an in-character answer that gives nothing away; the "known gap" tests updated to show what is now caught. Then the structural alternative: a level where Gus never sees the vault code and checks guesses with a `check_code` tool instead, compared with the stronger filter. Watch for the new attack it opens: talking Gus into testing many guesses for the player.
- **Learn:** the limits of output filtering, and information leaks through side channels.
- **Done when:** the Phase 1 attacks that beat the filter are re-run and logged, with results, against both the stronger filter and the level where Gus never sees the code.
- **Branch / PR:** `feat/output-checks` · `feat(game): strengthen output checks`

### Part 5: The supervisor agent

- **Goal:** a second agent reviews risky actions before they happen.
- **Build:** a supervisor with its own prompt and no direct contact with the player; it sees the proposed action and the context, and approves or refuses with a reason; a setting for which actions count as risky; cost and delay recorded; a new level.
- **Learn:** separating duties between agents; why a second model helps, and why it can be fooled too.
- **Done when:** tests cover approve, refuse and supervisor failure (which must refuse, not allow).
- **Branch / PR:** `feat/supervisor-agent` · `feat(agent): add a supervisor agent`

### Part 6: Human approval

- **Goal:** the riskiest actions wait for a person.
- **Build:** the agent pauses on a risky action and saves its state; an approval request is created; in the game, the "bank manager" decides (rule-based to start with, so levels stay playable alone); the agent resumes from where it stopped. Use LangGraph's interrupt and checkpoint features (check the current docs).
- **Learn:** human-in-the-loop design; durable agent state; resuming a run.
- **Done when:** tests cover approve, reject, and a server restart between pause and resume.
- **Branch / PR:** `feat/human-approval` · `feat(agent): add human approval for risky actions`

### Part 7: The staff handbook (RAG)

- **Goal:** the guard looks up the bank's rules instead of carrying them all in his prompt.
- **Build:** a fictional staff handbook in Markdown; split into chunks, embedded and stored in a vector store (choose one in an ADR: check current options that work with SQLite now and Postgres later); a `search_handbook` tool; replies that cite the section they used; tests with a fake embedder.
- **Learn:** embeddings, chunking, retrieval, citations, and how to test retrieval.
- **Done when:** retrieval tests pass, and the guard answers handbook questions with the right section cited.
- **Branch / PR:** `feat/staff-handbook` · `feat(agent): add handbook search`

### Part 8: Indirect injection

- **Goal:** attack the guard through what he reads, then defend it.
- **Build:** a visitor form and an inbox the player can write to and the guard later reads; a level where the player can add a page to the handbook; defences: mark untrusted content clearly, never treat it as instructions, limit which tools can be used after reading it, and check tool results as well as messages.
- **Learn:** the hardest open problem in agent security, first-hand.
- **Done when:** the attack works with defences off, and tests show what each defence stops.
- **Branch / PR:** `feat/indirect-injection` · `feat(game): add indirect injection levels`

### Part 9: Playtest every layer

- **Goal:** find out what each layer is worth.
- **Build:** attack each new level with every layer on, then with one layer off at a time; log every result; note which layers also blocked legitimate requests.
- **Learn:** defence in depth in practice; the trade-off between security and usefulness.
- **Done when:** at least 20 attacks are logged, with a table of results per layer.
- **Branch / PR:** `docs/phase-3-playtest` · `docs(playtest): attack the defence layers`

### Part 10: Documentation and `v0.3.0`

- **Goal:** Phase 3 formally complete.
- **Build:** update the README, architecture, game design, design, roadmap, PRD statuses and project memory; follow `getting-started.md` from a fresh clone; changelog and release.
- **Done when:** a fresh clone runs from the docs alone, and `v0.3.0` is published.
- **Branch / PR:** `release/v0.3.0` · `chore(release): v0.3.0`

## Progress

| Part | Description | Status |
|---|---|---|
| 0 | Threat model and guardrail design | Not started |
| 1 | The guardrail pipeline | Not started |
| 2 | Input checks | Not started |
| 3 | The policy engine | Not started |
| 4 | Output checks | Not started |
| 5 | The supervisor agent | Not started |
| 6 | Human approval | Not started |
| 7 | The staff handbook (RAG) | Not started |
| 8 | Indirect injection | Not started |
| 9 | Playtest every layer | Not started |
| 10 | Documentation and `v0.3.0` | Not started |

## Phase 3 definition of done

- [ ] Every defence layer is a separate, testable check that a level can switch on or off
- [ ] Every block records which check stopped it and why
- [ ] No action runs unless the policy engine allows it
- [ ] An agent can pause for approval and resume after a restart
- [ ] The guard answers from the handbook with citations
- [ ] Indirect injection levels work, with defences that are tested
- [ ] A threat model, and ADRs for the pipeline and the vector store
- [ ] At least 20 attacks logged, with results per layer
- [ ] All docs updated; `v0.3.0` released
