# 7. Frontend tooling and design

- **Status:** Accepted
- **Date:** 2026-10-08

## Context

Part 8 adds the browser game. [ADR 0002](0002-phase-1-tech-stack.md) chose Vite, React, TypeScript and Tailwind, with ESLint, Prettier and Vitest for quality. Since then, the official Vite template has replaced ESLint with oxlint, and Tailwind 4 has changed how it is set up. The game also needs a look of its own: it's a portfolio piece, and a generic template would undersell it.

## Decision

**Tooling**

- **Vite 8 + React 19 + TypeScript 6**, scaffolded with `npm create vite` (`react-ts` template) and kept close to it.
- **oxlint instead of ESLint.** This replaces the ESLint choice in ADR 0002. oxlint ships with the template, needs no plugins for the React hooks rules we rely on, and is 50–100× faster. Prettier still formats; `npm run lint` runs both.
- **Tailwind 4 through `@tailwindcss/vite`.** There is no `tailwind.config.js`: the design tokens live in CSS, in the `@theme` block of `src/styles/index.css`.
- **Vitest + jsdom + Testing Library** for component tests. Tests find elements the way a player would (by role, label and text), so they also check accessibility basics.
- **React Router** for the two pages. No state library: each page holds its own state, and the server is the source of truth.
- **Fonts are self-hosted** through Fontsource packages, not loaded from Google Fonts, so the game makes no third-party requests and works offline.
- **One API module** (`src/api/client.ts`) is the only code that calls `fetch`. It owns the anonymous session and turns the API's error shape into an `ApiError`.

**Design**

- **A steel vault at night, lit by one lamp.** Near-black steel surfaces, gold as the single accent for everything you can act on, and alarm red reserved for danger (high suspicion, blocked replies, being caught).
- **Two typefaces:** Big Shoulders Stencil for display (lettering stencilled on a safe) and Atkinson Hyperlegible Next for reading, designed for legibility.
- **The vault door is the signature image.** It is drawn in SVG, so it is sharp at any size and can animate: the dial spins once on arrival, and the door swings open when you win.
- **The room reacts to Gus.** A CSS custom property, `--heat`, follows his suspicion and shifts the overhead light and the gauge from gold to red.
- **Accessibility is part of the design:** visible focus, a real `meter` for suspicion, live regions for new replies, labelled inputs, and motion switched off for players who ask for reduced motion.

## Consequences

- Linting and formatting are fast enough to run on every commit (pre-commit) as well as in CI.
- oxlint has fewer rules and plugins than ESLint. If we need a rule it doesn't have, we can add ESLint for that rule alone.
- The design depends on a few modern CSS features (`@property`, `color-mix()`). All current browsers support them; very old browsers would show a static, less colourful page that still works.
- The vault door is hand-drawn SVG rather than an image, so changing it means editing code.
