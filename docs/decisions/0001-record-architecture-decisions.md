# 1. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-09-23

## Context

This project will make many technical choices over seven phases: frameworks, libraries, data design, security approaches. Months later, the code shows *what* was chosen but not *why*, or what else was considered. Without that, it's hard to know whether a decision still holds when circumstances change, and readers of this public repository can't follow the reasoning.

## Decision

We record every significant decision as an **Architecture Decision Record (ADR)**, following the format described by [Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

- ADRs live in `docs/decisions/`, named `NNNN-short-title.md` and numbered in order.
- Each ADR is short: context, decision, consequences.
- An accepted ADR is not edited to change its decision. If a decision changes, we write a new ADR and mark the old one `Superseded by NNNN`.
- An ADR is added in the same commit as the change it describes.

A decision is "significant" if it's hard to reverse, affects the project's structure, or someone would reasonably ask "why did you do it this way?"

## Consequences

- The reasoning behind the project is visible to anyone reading the repo, including future me.
- Writing an ADR takes a few minutes per decision, and forces the alternatives to be thought through.
- The history of decisions is kept, including ones that turned out wrong.

## Template

```markdown
# N. Title

- **Status:** Proposed | Accepted | Superseded by NNNN
- **Date:** YYYY-MM-DD

## Context
What is the problem, and what forces are at play?

## Decision
What we decided to do.

## Consequences
What becomes easier or harder as a result, good and bad.
```
