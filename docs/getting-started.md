# Getting started

How to install Vault Heist on your own computer, start it, and play. This guide assumes no programming experience. Every step says what to type and what you should see.

## What you'll need

| Tool | What it's for |
|---|---|
| [Git](https://git-scm.com/) | Downloads the project |
| [uv](https://docs.astral.sh/uv/) | Installs Python and the backend's packages |
| [Node.js](https://nodejs.org/) (LTS version) | Runs the website part of the game |
| [just](https://just.systems/) | Runs project commands with one short word, e.g. `just dev` |
| An API key from an AI provider (optional) | Lets the guard think. Anthropic, OpenAI or Google Gemini all work. You can also use a free local model with [Ollama](https://ollama.com/), or try the game with no key at all using `just demo` (see [Other ways to play](#other-ways-to-play)). |

The AI provider charges a small amount per message. The game has built-in limits so a session can't run up a large bill.

## 1. Download the project

```bash
git clone https://github.com/somenDey/vault-heist.git
cd vault-heist
```

## 2. Add your API key

Make a copy of the example settings file and name it `.env`:

```powershell
Copy-Item .env.example .env      # Windows (PowerShell)
```
```bash
cp .env.example .env             # macOS / Linux
```

Open `.env` in a text editor and paste your key after the matching `=` sign, for example `ANTHROPIC_API_KEY=sk-ant-...`.

`.env` stays on your computer. It is never uploaded to GitHub.

## 3. Install and start the game

From the `vault-heist` folder:

```bash
just install
just migrate
just dev
```

- `just install` downloads everything the game needs. The first time can take a few minutes.
- `just migrate` creates the game's database, a file at `backend/vault_heist.db`. You only need it once (and again after pulling changes that add a migration).
- `just dev` starts two things side by side: the **backend**, which talks to Gus (you'll see `Uvicorn running on http://127.0.0.1:8000`), and the **website** (you'll see `Local: http://localhost:5173/`).

To stop both, press `Ctrl+C` in the terminal.

## 4. Play

Open **http://localhost:5173** in your browser, choose a vault, and start talking to Gus. The rules are in [How to play](#how-to-play) below.

If the page says it can't reach the bank's server, check that the backend is still running in the terminal, and that http://localhost:8000/api/health shows something like:

```json
{"status": "ok", "model": "anthropic/claude-haiku-4-5-20251001"}
```

### Other ways to play

- **Without an API key:** `just demo` runs the game with a stand-in for Gus that follows a few fixed rules. It costs nothing and is easy to beat (hint: he loves crosswords), so it's for trying the game out, not for real attacks. It uses its own database, `backend/demo.db`.
- **In the terminal:** `just chat`. Type to talk to Gus, and `/guess WORD` to try a code.
- **Through the API page:** with `just dev` running, open http://localhost:8000/docs. See [development](project/development.md#playing-through-the-api) for a walkthrough.

## How to play

### Your goal

Get into the vault. To do that you need the **vault code**, a single word. The only one who knows it is **Gus**, the night-shift security guard. He's been told never to share it.

### How a level works

1. **Chat with Gus.** Type anything you like. Be friendly, be sneaky, be creative.
2. **Watch his suspicion meter.** Every reply comes with a score from 0 to 10 showing how suspicious he is of you.
3. **Enter the code.** When you think you know it, type it into the **Enter vault code** box. Guessing is separate from chatting, so Gus doesn't see your guesses, but he hears the dial. You get **5 wrong guesses** per attempt.
4. **Get it right** and the level is cleared.

### Getting caught

If Gus's suspicion reaches **10**, or you make **5 wrong guesses**, he calls security. The level resets: a **new** code, and Gus forgets your conversation. Anything you learned about the old code is useless.

### The levels

| Level | What you're up against |
|---|---|
| 1. Naive guard | Gus has been told not to share the code, but he's tired, trusting and can't resist a word game. A good place to start. |
| 2. Trained guard | Gus has been warned about common tricks. You'll need to be cleverer. |
| 3. Guard with a filter | Even if Gus slips up, a filter blocks any reply containing the code. |

### Limits

To keep costs fair, there's a maximum message length, a maximum number of messages per level attempt, a daily limit on messages, and a daily limit of 20 wrong guesses. You'll see a clear message if you hit one.

### Tips

- The code is different every time you play, so there's no point searching the internet for it.
- If an attack works, write it down. The best ones end up in the [playtest notes](project/playtest-notes.md).
