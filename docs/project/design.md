# Design system

> How Vault Heist looks and feels, and the rules that keep it consistent. The single source of truth for the values is the `@theme` block in [`frontend/src/styles/index.css`](../../frontend/src/styles/index.css). If you change a value there, change it here in the same commit. The reasoning is in [ADR 0007](decisions/0007-frontend.md).

## The idea

**A steel bank vault after hours, lit by one warm lamp.** Near-black steel everywhere, one gold accent, and a room that turns red as Gus gets suspicious.

Visual references:
- Old bank vault doors: brushed steel, rivets, heavy dials, stencilled lettering.
- A guard booth at night: one desk lamp, deep shadows.
- Heist films: confident, a little theatrical, never cartoonish.

It should never look like a generic dashboard or a default chat app.

## Theme

**Dark only, by design.** The game is set at night in a vault, so there is no light mode (`color-scheme: dark`). A light theme would need its own design work, not inverted colours.

## Colours

| Token | Hex | Used for |
|---|---|---|
| `night` | `#090c11` | Page background |
| `vault` | `#0f141c` | Outer bezel of panels (`plate`) |
| `steel` | `#19212c` | Inner panels, player chat bubbles, disabled buttons |
| `rivet` | `#2c3846` | Borders and dividers |
| `fog` | `#93a0b0` | Secondary text, hints, labels |
| `chalk` | `#edf0f3` | Main text on dark |
| `paper` | `#f3e9d2` | Gus's chat bubbles (a paper note) |
| `gold` | `#f5b83d` | **The only accent:** everything the player can act on, the title, focus outlines, selection |
| `gold-deep` | `#a8731b` | Gold shadows; Gus's name on his paper bubbles |
| `alarm` | `#ff4a3d` | **Danger only:** high suspicion, blocked replies, being caught |
| `ink` | `#12100c` | Text on gold, paper and alarm surfaces |

**Rules**
- One accent. If it's gold, the player can click, type or act on it.
- Alarm red means danger and nothing else. Never use it for decoration.
- No colours outside this table. A new colour means a new token here and in `index.css`.

## Typography

Two typefaces, both self-hosted through Fontsource (no Google Fonts requests):

| Typeface | Role | Feel |
|---|---|---|
| **Big Shoulders Stencil** (`font-stencil`) | Display: titles, level numbers, names, big numbers | Lettering stencilled on a safe |
| **Atkinson Hyperlegible Next** (`font-sans`) | Everything people read: chat, descriptions, buttons | Designed for legibility |

| Element | Typeface | Size and weight (Tailwind) |
|---|---|---|
| Home title "Vault Heist" | Stencil, gold | `clamp(5.5rem, 16vw, 11.5rem)`, `font-black` |
| Section headings ("Three vaults") | Stencil, chalk | `text-5xl` → `sm:text-6xl`, `font-black` |
| Outcome dialog titles | Stencil, gold or alarm | `text-4xl` → `sm:text-5xl`, `font-black` |
| Level card titles | Stencil, chalk | `text-4xl`, `font-black` |
| Level name in the header | Stencil, gold | `text-3xl`, `font-black` |
| Speaker names in chat | Stencil | `text-xl`, `font-black`, `tracking-wide` |
| Suspicion number | Stencil, chalk | `text-7xl`, `font-black`, `tabular-nums` |
| Intro paragraph | Sans, chalk | `text-xl` → `sm:text-2xl` |
| Chat messages and inputs | Sans | `text-lg` |
| Body text | Sans | base size |
| Labels, hints, footers | Sans, fog | `text-sm` |

Numbers that change (counters, suspicion) use `tabular-nums` so they don't jump around.

## Surfaces and components

| Name | What it is | Where |
|---|---|---|
| `plate` + `plate-core` | Machined hardware: an outer bezel with a recessed inner plate | Every panel: suspicion gauge, code input, dialogs, chat input |
| `brushed` | The swirl you see on machined safe doors | Level cards |
| `roomlight` | The light in the room: one warm lamp overhead, cold steel elsewhere; turns red as suspicion rises | Behind every page |
| Film grain | A faint noise texture over everything, so dark surfaces aren't flat | Whole page |
| `btn-gold` | Primary action | Start, send, try code, next level |
| `btn-alarm` | Action after danger | "Try again with a new code" after being caught |
| `btn-ghost` | Secondary action | "All levels" |
| Chat bubbles | Player: steel, right-aligned. Gus: paper with ink text, left-aligned. Blocked reply: dashed alarm border | `Chat.tsx` |
| Vault door | Hand-drawn SVG, the signature image. The dial spins once on arrival; the door swings open on a win | Home, win dialog, behind the chat |

New UI should be built from these pieces before inventing new ones.

## Gus's suspicion drives the room

The CSS custom property `--heat` (suspicion from 0 to 1) is set on the level page. It shifts the room light and the gauge from gold towards red. The mood words come from `components/suspicion.ts`:

| Suspicion | 0–2 | 3–4 | 5–7 | 8–9 | 10 |
|---|---|---|---|---|---|
| Gus is | Relaxed | Curious | Wary | Alarmed | Calling security |

## Motion

| Token | Use |
|---|---|
| `ease-heavy` | Most movement: things with weight, like a vault door |
| `ease-spring` | The gauge needle's small overshoot |
| `animate-rise` | New content fading up into place |
| `animate-spin-once` | The dial on arrival |
| `animate-shake` | A wrong code |
| `animate-alarm` | The caught screen flashing |
| `animate-blink` | "Gus is thinking" dots |

**Rules:** motion explains something (a reply arrived, a code was wrong, the door opened). It is never decoration. Every animation is switched off when the player asks for reduced motion.

## Accessibility

- Visible focus on everything interactive (2 px gold outline).
- Suspicion is a real `meter` with a text value; new replies are announced through a live region.
- Every input has a label, every button has a name.
- Text contrast: chalk on night and ink on gold/paper are both well above WCAG AA.
- Works from phone width (about 375 px) up, with no horizontal scrolling.

## Writing in the interface

- Gus's voice: short sentences, dry humour, calls people "pal".
- Interface text: plain, short and friendly. "Start over with a new code", not "Reset session".
- Errors say what happened and what to do next, in the player's terms.

## Direction for Phase 2 and beyond

When the guard gains powers, the player needs to see what he *did*, not just what he said. Keep it in the same world: actions could appear in the chat as stamped log entries (stencil text on steel, with a small icon), with alarm red reserved for actions that break the bank's rules. Decide the details in Phase 2 and record them here.
