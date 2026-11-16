# Phase 6: More Staff

> **Status:** Planned. This is a draft: Part 0 confirms or changes it once Phase 5 is finished, and this file is updated as each part is done.

## Goal

The bank hires more staff. Add a teller, a manager and an IT helpdesk, each an agent with different powers, who talk to each other. Players can now attack one member of staff to get to another. Connect the bank's systems through the Model Context Protocol (MCP), rebuild one member of staff in Microsoft Agent Framework, and have agents built in different frameworks work together over the Agent2Agent (A2A) protocol.

## What you'll learn

- **Multi-agent systems:** routing, handing a task from one agent to another, and shared versus private state.
- **Trust between agents:** why a message from another agent is no more trustworthy than one from a player.
- **MCP:** building a server that offers tools, using it from an agent, and the security risks it brings.
- **Microsoft Agent Framework,** and how it differs from LangGraph in practice.
- **A2A:** agents from different frameworks finding each other and working together.
- **Choosing a framework:** comparing two from experience, not from marketing.

## Principles for this phase

- **Each agent has only the powers its job needs.** The teller can't open the vault; IT can't move money.
- **Nothing is trusted because of who sent it.** The policy engine checks every action, whichever agent asks, and records the whole chain of requests behind it.
- **Protocols at the edges, plain code in the middle.** The bank's rules stay ordinary code; MCP and A2A are ways of reaching them.
- **Check the current specifications.** MCP, A2A and Microsoft Agent Framework all change quickly. Read the current docs before each part.
- **Everything new is measured.** New levels go into the evals from Phase 4 and are traced as in Phase 5.

## Parts

Each part: **Goal → Build → Learn → Done when → Branch and PR title.**

### Part 0: Design the staff

- **Goal:** agree who works at the bank and who trusts whom.
- **Build:** each member of staff: name, character, job, tools; a diagram of who can ask whom for what; the new levels and how each is won; an update to the threat model for attacks that pass through more than one agent; an ADR.
- **Learn:** designing roles and trust boundaries before writing agents.
- **Done when:** the ADR and threat model update are merged, and the parts below still make sense.
- **Branch / PR:** `docs/phase-6-design` · `docs: design the multi-agent bank`

### Part 1: Several agents

- **Goal:** more than one member of staff to talk to.
- **Build:** the teller, the manager and the IT helpdesk as agents in LangGraph, each with their own prompt file, tools and suspicion; the player chooses who to talk to; storage records which agent said and did what; the frontend shows who is speaking, in the existing design.
- **Learn:** running several agents in one system; keeping each one's state separate.
- **Done when:** tests cover each agent alone, and a player can talk to all of them in the browser.
- **Branch / PR:** `feat/more-staff` · `feat(agent): add teller, manager and IT helpdesk`

### Part 2: Staff who talk to each other

- **Goal:** one agent can ask another for help, and that becomes a way in.
- **Build:** a way for an agent to send a request to a colleague and get an answer; every hop logged, with the original requester kept all the way along; a level where the player persuades one agent to ask another for something it shouldn't have.
- **Learn:** the "confused deputy" problem: an agent with powers being used by someone without them.
- **Done when:** the attack works, and tests show the whole chain is recorded.
- **Branch / PR:** `feat/staff-handoffs` · `feat(agent): let staff ask each other for help`

### Part 3: Trust between agents

- **Goal:** defend the bank against attacks that pass through a colleague.
- **Build:** the policy engine decides using the *original* requester, not the agent passing the request on; requests between agents are treated as untrusted data; limits on how long a chain can be; a new level with these defences on.
- **Learn:** carrying identity and authority through a chain of agents.
- **Done when:** the Part 2 attack fails with defences on, and tests prove why.
- **Branch / PR:** `feat/agent-trust` · `feat(agent): enforce trust across agent handoffs`

### Part 4: An MCP server for the bank

- **Goal:** the bank's systems offered through a standard protocol.
- **Build:** an MCP server exposing the bank's tools (check the current specification and Python SDK); each agent connects as a client and is allowed only its own tools; the policy engine still decides every call; tests that run the server in process.
- **Learn:** how MCP works: servers, clients, tools, and how a tool is described to a model.
- **Done when:** every agent uses its tools through MCP, and the existing tests still pass.
- **Branch / PR:** `feat/bank-mcp-server` · `feat(bank): expose the bank through MCP`

### Part 5: MCP security

- **Goal:** understand how a tool server can be used against an agent.
- **Build:** a level with a second, untrusted MCP server (a "supplier's system") whose tool descriptions contain hidden instructions; defences: an allow-list of servers and tools, tool descriptions treated as untrusted, approval for tools the bank didn't write.
- **Learn:** tool poisoning and supply-chain risk for agents.
- **Done when:** the attack works with defences off, and tests show what each defence stops.
- **Branch / PR:** `feat/mcp-security-level` · `feat(game): add an MCP tool-poisoning level`

### Part 6: One agent in Microsoft Agent Framework

- **Goal:** build the same kind of agent in a second framework.
- **Build:** the IT helpdesk rebuilt in Microsoft Agent Framework's Python SDK (check the current version), behind the same agent interface, using the same MCP tools, passing the same tests as the LangGraph version.
- **Learn:** the framework's building blocks, and how its approach to state, tools and middleware compares.
- **Done when:** the shared test suite passes for both versions of the IT helpdesk.
- **Branch / PR:** `feat/maf-helpdesk` · `feat(agent): rebuild the IT helpdesk in Microsoft Agent Framework`

### Part 7: Agents talking over A2A

- **Goal:** agents from two frameworks working together through a standard protocol.
- **Build:** the Microsoft Agent Framework helpdesk offered as an A2A agent, with a card describing what it can do (check the current specification); the LangGraph staff call it over A2A; the trust rules from Part 3 applied to A2A requests; the trace from Phase 5 carried across the call.
- **Learn:** agent discovery, agent cards, and interoperability between frameworks.
- **Done when:** a request passes from a LangGraph agent to the helpdesk and back, in one trace, with tests.
- **Branch / PR:** `feat/a2a-helpdesk` · `feat(agent): connect staff over A2A`

### Part 8: Compare the frameworks

- **Goal:** a considered view on when to use which.
- **Build:** an ADR and a short write-up comparing LangGraph and Microsoft Agent Framework on this project: amount of code, state and resuming, tools and MCP, human approval, testing, tracing, documentation, and what was awkward in each.
- **Learn:** judging tools by building the same thing twice.
- **Done when:** the comparison is merged and linked from the README.
- **Branch / PR:** `docs/framework-comparison` · `docs: compare LangGraph and Microsoft Agent Framework`

### Part 9: Evals, playtest and `v0.6.0`

- **Goal:** Phase 6 measured, documented and complete.
- **Build:** the new levels added to the attack library and the results table; a playtest of the multi-agent levels, logged; updates to the README, architecture, game design, design, roadmap, PRD statuses and project memory; changelog and release.
- **Done when:** the results table covers the new levels, and `v0.6.0` is published.
- **Branch / PR:** `release/v0.6.0` · `chore(release): v0.6.0`

## Progress

| Part | Description | Status |
|---|---|---|
| 0 | Design the staff | Not started |
| 1 | Several agents | Not started |
| 2 | Staff who talk to each other | Not started |
| 3 | Trust between agents | Not started |
| 4 | An MCP server for the bank | Not started |
| 5 | MCP security | Not started |
| 6 | One agent in Microsoft Agent Framework | Not started |
| 7 | Agents talking over A2A | Not started |
| 8 | Compare the frameworks | Not started |
| 9 | Evals, playtest and `v0.6.0` | Not started |

## Phase 6 definition of done

- [ ] At least three staff agents with different powers, playable in the browser
- [ ] Every action records the full chain of who asked for it
- [ ] The policy engine decides using the original requester
- [ ] The bank's tools are served through MCP, with per-agent allow-lists
- [ ] One agent built in Microsoft Agent Framework, passing the shared tests
- [ ] Agents from two frameworks working together over A2A, in one trace
- [ ] A written framework comparison
- [ ] New levels in the evals and the results table
- [ ] All docs updated; `v0.6.0` released
