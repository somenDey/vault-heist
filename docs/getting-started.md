# Getting started

> **Work in progress.** The game can't be run yet. This page grows with each part of Phase 1, and by the end it will take you from nothing to playing in your browser.

This guide assumes no programming experience. Every step says what to type and what you should see.

## What you'll need

| Tool | What it's for |
|---|---|
| [Git](https://git-scm.com/) | Downloads the project |
| [uv](https://docs.astral.sh/uv/) | Installs Python and the backend's packages |
| [Node.js](https://nodejs.org/) (LTS version) | Runs the website part of the game |
| [just](https://just.systems/) | Runs project commands with one short word, e.g. `just dev` |
| An API key from an AI provider | Lets the guard think. Anthropic, OpenAI or Google Gemini all work. You can also use a free local model with [Ollama](https://ollama.com/). |

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

## 3. Install and start the backend

From the `vault-heist` folder:

```bash
just install
just dev
```

`just install` downloads everything the backend needs (the first time can take a minute). `just dev` starts it. You should see a line ending in `Uvicorn running on http://127.0.0.1:8000`.

Check it's working by opening http://localhost:8000/api/health in your browser. You should see something like:

```json
{"status": "ok", "model": "anthropic/claude-haiku-4-5-20251001"}
```

To stop the backend, press `Ctrl+C` in the terminal.

## 4. Play

_Coming soon, once the game and the website are built._
