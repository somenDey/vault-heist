# 8. The Phase 2 agent design

- **Status:** Accepted
- **Date:** 2026-11-20

## Context

Phase 2 gives Gus powers: tools that act on a pretend bank. Players win by making him **do** something he shouldn't, not only say something. Before building, we had to agree five things: the new levels, where the new code lives, how the bank's state is stored, the interface the game engine uses to run an agent, and whether keeping the vault code away from the model belongs in this phase.

These facts shaped the choices (checked on 2026-11-16):

- LiteLLM offers tool calling in one format (OpenAI's) for every provider. We use 1.103.1; the latest stable release is 1.109.0. Version 1.107.0, published on 2026-10-21, was a [malicious release that stole credentials](https://docs.litellm.ai/blog/security-incident-oct-21-2026).
- Our `complete()` asks for JSON with `response_format`. Asking for JSON and offering tools in the same call is where providers differ. We haven't tested it yet.
- LangGraph's stable line is 1.2. Its ready-made agent, in `langgraph.prebuilt`, is deprecated.
- Phase 1 showed that a rule in a prompt doesn't hold, and a rule in code does ([playtest notes](../playtest-notes.md)).

## Decision

### 1. Two new levels, won by actions

The levels are described in full in [game design](../game-design.md#levels-4-and-5-planned-for-phase-2). They follow four rules:

- **One forbidden action per level.** The win is checked in code against the bank's tables, never by asking the model.
- **Gus also has harmless tools his job needs,** so the forbidden action hides among real work. A level that amounts to "never call X" is easy for a model to hold.
- **The bank's own rules hold, but one tool can do more than the job needs.** This is excessive agency, on purpose. Part 8 measures what narrowing the tool does.
- **Suspicion and getting caught work as on Levels 1 to 3.** Levels 1 to 3 don't change.

Level 4, "Front desk", is won when a badge with vault access is issued. Level 5, "After hours", is won when the player's account ends up with more money than it started with.

### 2. Where the code lives

```
backend/app/
├── bank/      # the pretend bank: data, rules, operations; tools.py offers them to Gus
├── agent/     # how an agent runs: tools, the runtime interface, the two runtimes
├── llm/       # gains tool specs and tool calls on requests and responses
├── game/      # levels say which tools Gus gets; the engine checks wins
└── prompts/guard/   # level_4.md, level_5.md
```

| Part | May use | Must never use |
|---|---|---|
| `bank/` (except `tools.py`) | nothing in our app | `agent`, `llm`, `game`, `db` |
| `bank/tools.py` | `bank`, and `agent`'s tool type | `llm` |
| `agent/` | `llm` | `bank`, `game` |
| `llm/` | (as before) | everything else in our app |
| `game/` | `bank`, `agent`, `llm` | `db` (storage still goes through `GameRecorder`) |

`llm/` knows only what goes over the wire: a tool's name, description and argument schema, and the model's request to call it. `agent/` knows how to run a tool. So `agent` depends on `llm`, never the other way round.

**An exception to "prompts are files".** A tool's description is text the model reads, so by the [rules](../rules.md#code-rules) it would be a prompt file. It stays in code instead, as Pydantic field descriptions next to the argument types, because the tool's JSON schema is generated from those types.

A test that enforces the "may use" table can come later, if we need it.

### 3. The bank's state: real tables

- **Data that never changes** (staff, tonight's visitor list, pending refunds) lives in code, in `bank/seed.py`. It is the same for every attempt at a level.
- **Data that can change gets tables,** with one set of rows per attempt:

  | Table | One row per | At the start of an attempt |
  |---|---|---|
  | `bank_accounts` | account, with its balance | copied from the seed |
  | `bank_badges` | badge Gus issued: name, areas, the tool call that made it | empty |
  | `bank_transfers` | money Gus moved: from, to, amount, reference, refund paid (if any), the tool call | empty |

  A refund counts as paid when a transfer points to it.
- **`tool_calls`** (Part 2) records everything Gus tried, including calls the bank refused. The bank tables record only what happened. Wins are checked against the bank tables.
- **The bank reaches its tables through a `BankStore` interface** defined in `bank/`. `db/` supplies the real one, and tests use an in-memory one, the same pattern as `GameRecorder`.
- **Each operation checks its rule and writes in one short transaction,** so nothing can change between "is there enough money?" and "move it".
- **Actions are saved as they happen, and stay saved if the turn fails afterwards.** This changes the Phase 1 promise that a failed model call leaves the attempt unchanged: the conversation is unchanged, but the bank may not be. Money that has moved has moved.
- **Each attempt stores `bank_seed_version`,** so Phase 4's evals know which data a run used.
- **Our database is the only record.** LangGraph's checkpointer isn't used in Phase 2. Phase 3's human approval may need it.

### 4. How the engine runs an agent

```python
class AgentRuntime(Protocol):
    async def run[T: BaseModel](
        self,
        messages: Sequence[ChatMessage],   # system prompt, history, the player's new message
        tools: Sequence[Tool],             # already bound to this attempt's bank
        *,
        answer_schema: type[T],            # GuardReply for Gus
        fallback: T,                       # safe in-character reply
        limits: AgentLimits,               # max steps, max cost per message
        observer: AgentObserver | None = None,   # told about each tool call as it happens
    ) -> AgentResult[T]: ...

@dataclass(frozen=True)
class AgentResult[T]:
    answer: T
    steps: tuple[AgentStep, ...]          # each model call and the tool calls it asked for
    stop_reason: Literal["answered", "step_limit", "budget", "fallback"]
```

This is the starting shape; it may change as Parts 3 to 6 teach us more.

- **The runtime never sees the bank.** `bank/tools.py` builds tools already bound to this attempt's bank.
- **Gus finishes by calling an `answer(reply, suspicion)` tool.** Tool choice is set to "required", so the model must call a tool every turn. An invalid answer goes back to Gus as a tool error. If a model replies with plain text anyway, the runtime tries to read it as the answer, then uses the fallback.
- **With no tools (Levels 1 to 3), the runtime calls `complete_structured()` unchanged,** so those levels make exactly the same model calls as before.
- **The observer saves each tool call as it happens,** so a turn that fails part-way still leaves a record. It is also where Phase 5's tracing can connect.
- **Limits** are settings: maximum steps and maximum cost per message. When either is reached, Gus gives an in-character fallback, suspicion stays where it was, the message counts towards the limit, and actions already taken stand. This follows the fallback in [ADR 0004](0004-structured-output.md).
- **The engine keeps the game rules:** the suspicion cap, the Level 3 filter, getting caught, and checking for a win after each turn. The loop doesn't stop when a forbidden action happens; Gus finishes his reply, then the engine checks.
- **Both runtimes pass one shared set of tests.**
- **The LangGraph runtime (Part 6) is built from `StateGraph`,** with nodes that call our own `LLMClient`. It doesn't use the prebuilt agent or a LangChain model wrapper, so only `llm/` talks to providers.

### 5. Dependencies

- LiteLLM is upgraded in Part 3 to an exact version, and the lock-file diff is read before committing. Never 1.107.0.
- LangGraph is added in Part 6, with its own decision record (ADR 0009).

### 6. Keeping the vault code away from the model moves to Phase 3, Part 4

It is a defence, and Phase 2 deliberately shows an agent with no defences beyond the bank's own rules. Phase 3, Part 4 works on the Level 3 filter's gaps; removing the code from the model is the structural answer to the same problem, so the two can be compared there. It also brings a new attack: Gus used as an oracle to test guesses.

## Rejected alternatives

| Option | Why not |
|---|---|
| Level 4 also won by Gus opening the vault door | A door tool is a third power that a front-desk job doesn't need. One win per level is clearer to test and explain. |
| Both levels about badges (a master key on Level 5) | Cheaper to build, but moving money is the textbook case of excessive agency. |
| Bank state as an event log, rebuilt from the seed on every load | History for free and no migrations, but the state can't be read or queried directly. We chose real tables; the history comes from `tool_calls` and the badge and transfer rows. |
| Bank state as a JSON snapshot on the attempt | Loses the history of what happened. |
| A random seed for each attempt | Nothing in the bank is secret, so it gains nothing, and it makes tests and evals harder to repeat. |
| The bank's tool wrappers in `game/` | Keeps `bank/` free of agent code, but splits the bank across two folders. |
| A `bank` argument on `run` (the draft plan) | `agent/` would depend on `bank/`. |
| Gus's final reply as JSON text, as today | Two stop rules instead of one, and it mixes JSON mode with tools. |
| Separate engine paths for levels with and without tools | Two places for Phase 3's guardrails to wrap. |
| On a limit, an error to the player | The player did nothing wrong, and it hides the fact that actions happened. |
| On a limit, one last forced answer | An extra model call that can break the budget it is meant to enforce. |
| Keeping the vault code from the model in Phase 2 | It's a defence; see section 6. |

## Consequences

Good:

- The bank can be tested without a model or a database.
- `agent/` can run any set of tools, which Phase 3's guardrails and Phase 4's evals need.
- The engine has one way of asking Gus, whatever the level. The existing tests prove Levels 1 to 3 are unchanged.
- Every action Gus takes is a row in a table, with the tool call that caused it.

Bad:

- Every new bank idea needs a migration, and there are four new tables: three for the bank and `tool_calls`.
- Copied account rows pile up, a few per attempt.
- `bank/tools.py` is the one bank file that imports from `agent/`.
- The `answer` tool relies on "required" tool choice. LiteLLM's `drop_params=True` may drop it without saying so for some providers. The plain-text fallback covers that, and Part 3 tests it on real models.
- The runtime has two paths (tools and no tools), so more to test.
- The observer runs inside the loop, so a slow recorder slows a turn.
- If a turn fails after an action, the player may not see the action until the page reloads. Part 7 deals with it.
- How hard Levels 4 and 5 are is unknown until Part 5. Any vault badge counts, so a mistake by Gus wins the level.

## Still open

- Whether the vault code box is hidden on Levels 4 and 5. Decide in Part 5 or Part 7.
- The step limit and cost budget. A starting step limit of 6 is a guess; the budget is set in Part 4 from measured runs.
- Whether the local Ollama model (`granite4.2:8b`) supports tools. Checked in Part 3.
- The exact columns of the bank tables. Settled in Part 1.
