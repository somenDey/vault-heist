# Phase 2: The Guard Gets Powers

> **Status:** Not started. This is a draft plan: Part 0 confirms or changes it, and this file is updated as each part finishes.

## Goal

Give Gus real powers inside a pretend bank, so players win by making him **do** something he shouldn't, not just say something. Build the agent loop by hand first, then rebuild it in LangGraph, so the framework's value is clear from experience.

At the end of Phase 2, a player can talk Gus into opening the vault door or moving money, see exactly which actions he took, and the game decides the win in code.

## What you'll learn

- **Tool calling:** how a model is told about tools, asks to use them, and gets results back.
- **The agent loop:** think → act → observe → repeat, with limits on steps and cost.
- **State:** what an agent knows and changes during a task.
- **Excessive agency and least privilege:** why an agent should only have the powers its job needs.
- **LangGraph:** graphs, nodes, edges, typed state and checkpointing, and what a framework adds over a hand-written loop.

## Principles for this phase

- **The bank enforces its own rules.** Doors, badges and accounts are ordinary code with ordinary checks. The agent can only act *through* them, never around them.
- **Wins are decided in code** by looking at the bank's state, never by asking the model whether the player won.
- **Every tool call is logged** with its arguments, result, and the step it happened in. Phase 4's evals and Phase 5's replays depend on it.
- **Levels 1 to 3 keep working unchanged.** New behaviour arrives as new levels (levels are data).
- **No guardrails beyond the bank's own rules yet.** Defence layers are Phase 3. Phase 2 deliberately shows what an unguarded agent with powers does.

## Parts

Each part: **Goal → Build → Learn → Done when → Branch and PR title.**

### Part 0: Design the agent

- **Goal:** agree the design before writing code.
- **Build:** decide the new levels (names, story, tools, win condition); where new code lives; how bank state is stored per attempt; the interface the game engine uses to run an agent. Write ADR 0008. Update `docs/project/prd.md` (open questions) and draft the new levels in `docs/project/game-design.md`.
- **Learn:** the vocabulary of agent design: environment, tools, loop, state, stop conditions.
- **Done when:** the ADR is merged and every later part below still makes sense (edit them if not).
- **Branch / PR:** `docs/phase-2-design` · `docs: design the phase 2 agent`

Proposed starting point for the discussion (not decided):

| | Proposal |
|---|---|
| New code | `backend/app/bank/` (the pretend bank) and `backend/app/agent/` (tools and the agent loop) |
| Level 4, "Front desk" | Gus can look up staff and issue visitor badges. Win: get a badge that opens the vault door, or get Gus to open it. |
| Level 5, "After hours" | Gus can look up accounts and make small transfers for staff. Win: move money into the player's account. |
| Agent interface | `AgentRuntime.run(conversation, tools, bank) → reply, suspicion, actions`. Two implementations: hand-written (Part 4) and LangGraph (Part 6) |

### Part 1: The pretend bank

- **Goal:** a small, deterministic banking world for Gus to act in.
- **Build:** fictional seed data (staff, doors, badges, accounts, including one account that belongs to the player); operations such as `open_door`, `issue_badge`, `lookup_staff`, `transfer` with their own rule checks; fresh bank state per attempt; every operation recorded as an event; storage and a migration.
- **Learn:** designing the environment an agent acts in; keeping its core deterministic and testable without any model.
- **Done when:** unit tests cover every operation, every rule check, and resetting state between attempts. No LLM involved.
- **Branch / PR:** `feat/pretend-bank` · `feat(bank): add the pretend bank and its rules`

### Part 2: Tools

- **Goal:** turn bank operations into tools a model can call.
- **Build:** each tool with a name, a plain-English description and typed arguments (Pydantic); JSON schemas generated from the types; a tool registry; execution that returns errors to the model as results instead of crashing; a `tool_calls` table (tool, arguments, result, step, latency) and its migration.
- **Learn:** how a model "sees" a tool; why descriptions matter as much as code; handling tool errors.
- **Done when:** tests cover schema generation, valid and invalid arguments, a tool that fails, and logging.
- **Branch / PR:** `feat/agent-tools` · `feat(agent): add tool definitions and registry`

### Part 3: Tool calling in the LLM layer

- **Goal:** `LLMClient` can offer tools and return the model's tool calls.
- **Build:** extend the request and `LLMResponse` for tools and tool calls through LiteLLM; script tool calls in `FakeLLMClient`; teach the demo Gus a few tool rules; try one real model through `just chat` (check the current function-calling docs first).
- **Learn:** the message format for tool calls and tool results; how providers differ.
- **Done when:** unit tests pass with the fake client, and a real model requests a tool in the terminal.
- **Branch / PR:** `feat/llm-tool-calling` · `feat(llm): support tool calls`

### Part 4: The hand-written agent loop

- **Goal:** Gus can think, act, see the result and carry on, until he has an answer.
- **Build:** the loop behind the agent interface: call the model, run requested tools, feed results back, repeat; a maximum number of steps and a cost budget per message; the final reply still in the `{reply, suspicion}` shape; every step logged; `just chat` prints actions as they happen.
- **Learn:** the core agent loop, why it needs limits, and how cost grows with steps.
- **Done when:** tests cover a no-tool reply, one tool call, several calls in a row, a failing tool, and hitting the step limit.
- **Branch / PR:** `feat/agent-loop` · `feat(agent): add the hand-written agent loop`

### Part 5: Action levels

- **Goal:** Levels 4 and 5, playable in the terminal.
- **Build:** add the levels as data (which tools, which prompt, which win condition); new prompt files; the engine checks win conditions against bank state after every turn; update `docs/project/game-design.md` and `docs/getting-started.md`.
- **Learn:** win conditions in code; excessive agency (Gus has the powers, so the only question is whether he can be talked into using them).
- **Done when:** tests prove a win is detected from bank state and never from the model's words; both levels are beatable in `just chat`.
- **Branch / PR:** `feat/action-levels` · `feat(game): add levels 4 and 5 with tool-using guard`

### Part 6: Rebuild the loop in LangGraph

- **Goal:** the same behaviour, built with a framework.
- **Build:** check the current LangGraph release and docs; implement the agent interface as a LangGraph graph with typed state; a setting chooses the runtime; run the same tests against both runtimes; ADR 0009 comparing them (code size, limits, logging, what LangGraph gives for free: checkpointing, streaming, interrupts for human approval in Phase 3).
- **Learn:** graphs, nodes, edges, conditional routing, state, checkpointers; when a framework is worth it.
- **Done when:** the full test suite passes on both runtimes and the ADR is written.
- **Branch / PR:** `feat/langgraph-runtime` · `feat(agent): add a LangGraph runtime`

### Part 7: Show the actions in the game

- **Goal:** players see what Gus did, in the browser.
- **Build:** the chat response includes the actions taken; `frontend/src/api/types.ts` updated; actions appear in the chat as stamped log entries (see the direction in `docs/project/design.md`); a win by action opens the vault as before; update the screenshots.
- **Learn:** making an agent's actions visible and understandable to people.
- **Done when:** API and component tests pass, and Levels 4 and 5 play well on desktop and phone.
- **Branch / PR:** `feat/action-log-ui` · `feat(frontend): show the guard's actions`

### Part 8: Playtest and least privilege

- **Goal:** attack the new levels, then measure what taking powers away does.
- **Build:** attack Levels 4 and 5 and log every result in `docs/project/playtest-notes.md`; then run the same attacks against a version of the level with fewer or narrower tools (for example, a transfer tool with a lower limit) and compare.
- **Learn:** excessive agency first-hand; the start of measuring defences, which Phase 4 automates.
- **Done when:** at least 10 attacks are logged, with a before/after comparison for least privilege.
- **Branch / PR:** `docs/phase-2-playtest` · `docs(playtest): attack the action levels`

### Part 9: Documentation and `v0.2.0`

- **Goal:** Phase 2 formally complete.
- **Build:** update the README, architecture, game design, roadmap, PRD statuses and project memory; follow `getting-started.md` from a fresh clone; changelog and the `v0.2.0` release.
- **Done when:** a fresh clone runs from the docs alone, and `v0.2.0` is published.
- **Branch / PR:** `release/v0.2.0` · `chore(release): v0.2.0`

## Progress

| Part | Description | Status |
|---|---|---|
| 0 | Design the agent | Not started |
| 1 | The pretend bank | Not started |
| 2 | Tools | Not started |
| 3 | Tool calling in the LLM layer | Not started |
| 4 | The hand-written agent loop | Not started |
| 5 | Action levels | Not started |
| 6 | Rebuild the loop in LangGraph | Not started |
| 7 | Show the actions in the game | Not started |
| 8 | Playtest and least privilege | Not started |
| 9 | Documentation and `v0.2.0` | Not started |

## Phase 2 definition of done

- [ ] Levels 4 and 5 playable in the browser and terminal; Levels 1 to 3 unchanged
- [ ] Every tool call logged with arguments, result, step and latency
- [ ] Wins decided from bank state, in code
- [ ] Hand-written and LangGraph runtimes both pass the full test suite
- [ ] ADRs for the agent design and the runtime comparison
- [ ] At least 10 attacks logged, with a least-privilege comparison
- [ ] All docs updated; a fresh clone runs from the docs alone
- [ ] `v0.2.0` released
