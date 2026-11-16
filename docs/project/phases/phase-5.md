# Phase 5: Security Cameras

> **Status:** Planned. This is a draft: Part 0 confirms or changes it once Phase 4 is finished, and this file is updated as each part is done.

## Goal

Make everything the guard does visible. Trace every request from the player's message through each model call, tool call and guardrail check, using the industry standard. Then turn that record into a feature: a "CCTV" page where anyone can replay a heist step by step and see which defence stopped it, or didn't. Add hard limits on spending, ready for the public launch.

## What you'll learn

- **Observability** (being able to see what a running system is doing) for AI agents: traces, spans and metrics.
- **OpenTelemetry** and its conventions for generative AI, the vendor-neutral standard.
- **A tracing tool for LLM apps** (Langfuse), run locally in Docker.
- **Cost and latency monitoring,** and enforcing budgets in code.
- **Privacy in logs:** what should never be recorded.
- **Explaining an agent's behaviour** to a person through a replay.

## Principles for this phase

- **Instrument against the standard, not a vendor.** Tracing code uses OpenTelemetry; the tool that displays traces can be swapped by changing a setting.
- **Tracing is optional.** The game runs the same with tracing switched off, and tests don't need a tracing server.
- **No secrets in traces.** API keys are never recorded. The vault code of an attempt in progress is never shown to a player.
- **One place to instrument.** Model calls are traced inside the LLM layer, tools inside the tool runner, checks inside the guardrail pipeline.
- **The database stays the record of the game.** Traces are for understanding and debugging; the replay page is built from the game's own tables.

## Parts

Each part: **Goal → Build → Learn → Done when → Branch and PR title.**

### Part 0: Design the tracing

- **Goal:** agree what is traced, how, and what is left out.
- **Build:** the span tree for one player message; which attributes are recorded (check the current OpenTelemetry generative AI conventions and how stable they are); what is redacted; the choice of tracing tool; an ADR.
- **Learn:** the vocabulary: trace, span, attribute, exporter, collector.
- **Done when:** the ADR is merged, and the parts below still make sense.
- **Branch / PR:** `docs/phase-5-design` · `docs: design tracing and replay`

### Part 1: OpenTelemetry tracing

- **Goal:** one trace per player message, covering everything that happened.
- **Build:** spans for the request, the agent run, each model call, each tool call and each guardrail check, with the standard attributes (model, tokens, tool name) and our own (level, attempt, check result); output to the console to start with; tests using an in-memory exporter.
- **Learn:** instrumenting code by hand; how context passes from one span to the next.
- **Done when:** tests check the shape of the span tree, and a real game prints a complete trace.
- **Branch / PR:** `feat/otel-tracing` · `feat(backend): trace requests with OpenTelemetry`

### Part 2: A trace viewer

- **Goal:** look at traces in a proper tool.
- **Build:** Langfuse running locally through Docker Compose (check the current version and how it accepts OpenTelemetry data); the backend sends traces to it when a setting is on; setup steps in the docs; a `just` task to start and stop it.
- **Learn:** running supporting services in Docker; reading a trace to debug an agent.
- **Done when:** a heist played locally appears in the viewer as one trace, with every step.
- **Branch / PR:** `feat/trace-viewer` · `feat(backend): send traces to Langfuse`

### Part 3: Cost and latency

- **Goal:** know what the game costs and how fast it is.
- **Build:** measures of tokens, cost and response time by level, model and step; a `just stats` report from the database; the slowest and most expensive steps found and written up.
- **Learn:** where time and money go in an agent, and which changes help most.
- **Done when:** the report runs, and its findings are in the docs.
- **Branch / PR:** `feat/cost-latency-stats` · `feat(backend): report cost and latency`

### Part 4: Spending limits

- **Goal:** the game cannot run up a bill.
- **Build:** a spending budget per session and a daily budget for the whole game, both enforced in code before a model call; a friendly "the bank is closed for today" state for players; a kill switch setting that turns off real model calls and falls back to the demo guard.
- **Learn:** protecting an AI service from cost overruns and abuse.
- **Done when:** tests cover each limit and the kill switch.
- **Branch / PR:** `feat/spending-limits` · `feat(game): enforce spending budgets`

### Part 5: The replay data

- **Goal:** the full story of one attempt, in order.
- **Build:** an API endpoint that returns the timeline of a finished attempt: messages, the guard's actions, each check and its result, and what was blocked; attempts in progress can't be replayed, so the code stays secret; only the player's own attempts for now.
- **Learn:** designing an API for explaining what an agent did.
- **Done when:** API tests cover a won attempt, a caught attempt, and a refused request for an attempt in progress.
- **Branch / PR:** `feat/replay-api` · `feat(api): add the heist replay timeline`

### Part 6: The CCTV page

- **Goal:** watch a heist back.
- **Build:** a replay page in the game's style: step forward and back through the attempt; each step shows what the player said, what Gus said, what he did, and which defence acted; blocked steps are marked clearly; a "Watch the replay" button after a win or a capture; works with a keyboard and on a phone.
- **Learn:** making an agent's reasoning and the defences understandable to people.
- **Done when:** component tests pass, and the page is added to the screenshots.
- **Branch / PR:** `feat/replay-page` · `feat(frontend): add the heist replay page`

### Part 7: Production logging

- **Goal:** be ready to run this in public.
- **Build:** a request id on every log line and every error response; logs as JSON in production; errors that say enough to debug without revealing secrets or player messages where they shouldn't; a health check that reports whether the database and the model are reachable.
- **Learn:** the logging basics every production service needs.
- **Done when:** tests check the request id, and a forced error can be followed from the response to the log to the trace.
- **Branch / PR:** `feat/production-logging` · `feat(backend): add request ids and health checks`

### Part 8: Documentation and `v0.5.0`

- **Goal:** Phase 5 formally complete.
- **Build:** update the README (with a replay screenshot), architecture, development (how to run the trace viewer), roadmap, PRD statuses and project memory; changelog and release.
- **Done when:** someone can start the trace viewer and watch a replay from the docs alone, and `v0.5.0` is published.
- **Branch / PR:** `release/v0.5.0` · `chore(release): v0.5.0`

## Progress

| Part | Description | Status |
|---|---|---|
| 0 | Design the tracing | Not started |
| 1 | OpenTelemetry tracing | Not started |
| 2 | A trace viewer | Not started |
| 3 | Cost and latency | Not started |
| 4 | Spending limits | Not started |
| 5 | The replay data | Not started |
| 6 | The CCTV page | Not started |
| 7 | Production logging | Not started |
| 8 | Documentation and `v0.5.0` | Not started |

## Phase 5 definition of done

- [ ] One trace per player message, covering model calls, tool calls and guardrail checks
- [ ] Traces follow the OpenTelemetry conventions and can be sent to a viewer by changing a setting
- [ ] No API key in any trace or log; the code of an attempt in progress is never exposed
- [ ] Spending budgets and a kill switch, enforced in code and tested
- [ ] A replay page for finished attempts, showing which defence acted at each step
- [ ] Request ids, JSON logs and a real health check
- [ ] All docs updated; `v0.5.0` released
