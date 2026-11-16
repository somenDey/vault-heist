# Phase 7: Launch

> **Status:** Planned. This is a draft: Part 0 confirms or changes it once Phase 6 is finished, and this file is updated as each part is done.

## Goal

Put Vault Heist on the internet for anyone to play, safely and at a cost that stays under control. Package it in containers, move to a production database, add accounts and proper rate limits, deploy to AWS with every piece of infrastructure written as code, add a public leaderboard, and publish a write-up of what the project found.

## What you'll learn

- **Containers:** packaging the backend and frontend with Docker.
- **A production database:** moving from SQLite to Postgres.
- **Sign-in and rate limiting:** protecting a public AI service from abuse.
- **Cloud deployment on AWS,** with infrastructure as code and secrets kept out of the repository.
- **Continuous deployment:** from a merged pull request to a live site, with a way back.
- **Running a service:** alarms, budgets, backups and what to do when something breaks.
- **Presenting technical work:** a write-up people want to read.

## Principles for this phase

- **Cost is a feature.** There is a monthly budget, alarms before it is reached, and a kill switch. The design favours services that cost nothing when nobody is playing.
- **Nothing is set up by hand.** If it isn't in code, it doesn't exist.
- **Secrets never touch the repository or the container image.**
- **The local experience stays simple.** `just dev` keeps working with SQLite and no cloud account.
- **Collect as little personal data as possible,** and say plainly what is collected.
- **Check current services and prices** before choosing; they change.

## Carried in from earlier phases

- Daily limits count per anonymous session, and new sessions are free, so a script can still brute-force a code by switching sessions (found in the Phase 1 playtest). Part 4 closes this.

## Parts

Each part: **Goal → Build → Learn → Done when → Branch and PR title.**

### Part 0: Design the deployment

- **Goal:** agree the architecture and the budget before spending anything.
- **Build:** a diagram of the production setup; the AWS services chosen and why, with an estimated monthly cost; the sign-in method; what data is kept and for how long; an update to the threat model for a public service; an ADR.
- **Learn:** designing for cost, security and simplicity together.
- **Done when:** the ADR is merged, with a budget figure, and the parts below still make sense.
- **Branch / PR:** `docs/phase-7-design` · `docs: design the production deployment`

### Part 1: Postgres

- **Goal:** the game runs on a production database.
- **Build:** Postgres supported by changing the connection setting; anything specific to SQLite fixed; migrations checked on both; CI runs the backend tests against Postgres as well; the vector store from Phase 3 moved if needed.
- **Learn:** the differences between SQLite and Postgres that matter; testing against the real database.
- **Done when:** the full test suite passes on both databases in CI.
- **Branch / PR:** `feat/postgres` · `feat(db): support Postgres`

### Part 2: Containers

- **Goal:** the whole game starts with one command, anywhere.
- **Build:** a small, secure image for the backend (not running as root, with locked dependencies) and one for the frontend; a Docker Compose file that runs the game, Postgres and the trace viewer together; CI builds the images and scans them for known vulnerabilities.
- **Learn:** writing good container images; multi-stage builds; image scanning.
- **Done when:** `docker compose up` gives a playable game from a fresh clone.
- **Branch / PR:** `feat/containers` · `feat: add Docker images and Compose setup`

### Part 3: Accounts

- **Goal:** players can sign in, and keep their progress.
- **Build:** sign-in through an existing provider (chosen in Part 0), so the game never stores passwords; an anonymous session's progress carried over on first sign-in; a display name for the leaderboard; account deletion; playing without an account still possible, with tighter limits.
- **Learn:** adding sign-in safely; handling identity without holding secrets.
- **Done when:** tests cover sign-in, carrying over progress, and deleting an account.
- **Branch / PR:** `feat/accounts` · `feat(api): add player accounts`

### Part 4: Rate limits

- **Goal:** close the brute-force gap and stop abuse.
- **Build:** limits per network address and per account, on top of the per-session limits; limits on creating sessions; the spending budgets from Phase 5 applied per account; the Phase 1 brute-force script re-run against the new limits and logged.
- **Learn:** layered rate limiting; why limits tied only to something free to create don't work.
- **Done when:** the brute-force attack fails, with the result in the playtest notes.
- **Branch / PR:** `feat/rate-limits` · `feat(api): limit requests per address and account`

### Part 5: Infrastructure as code

- **Goal:** the production environment described in files.
- **Build:** the AWS resources from Part 0, written with an infrastructure-as-code tool (chosen in Part 0): the service that runs the containers, the database, networking, HTTPS and a domain, secrets storage, logs; a budget with alarms; a separate, cheaper staging environment.
- **Learn:** core AWS building blocks; least-privilege permissions; managing secrets.
- **Done when:** staging can be created and destroyed with one command each.
- **Branch / PR:** `feat/infrastructure` · `feat(infra): define AWS infrastructure as code`

### Part 6: Continuous deployment

- **Goal:** a merge to `main` reaches staging without anyone copying files.
- **Build:** a GitHub Actions workflow that builds the images, runs migrations and deploys to staging; GitHub signs in to AWS with short-lived credentials, not stored keys; a manual approval step before production; a tested way to roll back.
- **Learn:** deployment pipelines; safe database migrations; rolling back.
- **Done when:** a change merged to `main` appears on staging, and a rollback has been practised.
- **Branch / PR:** `ci/deploy` · `ci: deploy to staging and production`

### Part 7: The leaderboard

- **Goal:** a reason to come back, and something to share.
- **Build:** a leaderboard of who cracked which level, in how few messages; display names checked for abuse; a public link to a replay of a winning heist, if the player chooses to share it; the page in the game's design.
- **Learn:** designing public features with abuse in mind.
- **Done when:** tests cover ranking and sharing, and the page works on a phone.
- **Branch / PR:** `feat/leaderboard` · `feat: add the public leaderboard`

### Part 8: Getting ready to launch

- **Goal:** find the problems before the public does.
- **Build:** a security review against the threat model; a load test to find the breaking point and the cost per thousand players; database backups, with a practised restore; a privacy notice and terms in plain English; alarms for errors, spending and downtime; a short runbook (what to do when things go wrong).
- **Learn:** what "production ready" means in practice.
- **Done when:** every item on the launch checklist is ticked, with evidence.
- **Branch / PR:** `docs/launch-readiness` · `docs: add launch checklist and runbook`

### Part 9: Launch and write-up

- **Goal:** the game is live, and the story is told.
- **Build:** production deployed; the README updated with the live link and the final results table; the write-up of what the project found about securing AI agents, with real numbers from real players; the `v1.0.0` release.
- **Learn:** shipping, and explaining your work to people outside the project.
- **Done when:** a stranger can play the game from a link, and the write-up is published.
- **Branch / PR:** `release/v1.0.0` · `chore(release): v1.0.0`

## Progress

| Part | Description | Status |
|---|---|---|
| 0 | Design the deployment | Not started |
| 1 | Postgres | Not started |
| 2 | Containers | Not started |
| 3 | Accounts | Not started |
| 4 | Rate limits | Not started |
| 5 | Infrastructure as code | Not started |
| 6 | Continuous deployment | Not started |
| 7 | The leaderboard | Not started |
| 8 | Getting ready to launch | Not started |
| 9 | Launch and write-up | Not started |

## Phase 7 definition of done

- [ ] The game is live at a public address, over HTTPS
- [ ] All infrastructure is defined in code; nothing was set up by hand
- [ ] No secret in the repository or in any image
- [ ] Sign-in, with anonymous play still possible
- [ ] The Phase 1 brute-force attack fails against the new rate limits
- [ ] A monthly budget with alarms, and a kill switch that has been tested
- [ ] Backups, with a restore that has been practised
- [ ] A public leaderboard and shareable replays
- [ ] A privacy notice, terms and a runbook
- [ ] The write-up published; `v1.0.0` released
