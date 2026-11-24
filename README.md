# Sendora AI systems: the hub

Seven free, MIT licensed AI systems a business can run, plus the shared base they are built on. Each system is its own repo. This hub holds the start here guide, the shared base, and the way the tools are compared.

Status: the shared base (version 1.2.0) and all seven systems are built and tested locally. None of the repos is published yet. Nothing here has been run against live vendor accounts.

## Start here

1. Read `docs/00-BUSINESS-BASICS.md`: company and EIN, domain and DNS, website, mailboxes, and texting registration. This is what most people skip and what makes the systems work in real life.
2. Pick a system from the table below. Each one runs with made up data and no accounts in about five minutes.
3. Read `docs/TOOLS-SCOREBOARD.md` for every tool the systems name, scored, with the open source alternative where one is close, and `docs/COMPARISON-METHOD.md` for how the scores are made.

## The seven systems (names from a public search, not a legal clearance)

| System | What it does | Planned repo | State |
| --- | --- | --- | --- |
| Pipecairn | Lead to signed deal: outreach, replies, pipeline, proposals | `https://github.com/onittindwani-ai/pipecairn` | not yet published |
| Ringlark | AI SDR setup: inbound and outbound calls and follow ups | `https://github.com/onittindwani-ai/ringlark` | not yet published |
| Booklantern | Finance back office: invoices, collections, reconciliation, cash forecast | `https://github.com/onittindwani-ai/booklantern` | not yet published |
| Deskfern | Support and success desk with cited answers | `https://github.com/onittindwani-ai/deskfern` | not yet published |
| Lorefern | Company brain: ask anything, meetings to tasks, weekly review | `https://github.com/onittindwani-ai/lorefern` | not yet published |
| Penlark | Content in your own voice, with approval before anything is published | `https://github.com/onittindwani-ai/penlark` | not yet published |
| Slatehire | Hiring and onboarding pipeline with evidence and a human decision | `https://github.com/onittindwani-ai/slatehire` | not yet published |

The links above do not work until each repo is published. This hub will be published as `https://github.com/onittindwani-ai/sendora-ai-systems`.

Every system ships the same things: guides 00 to 15, a five minute demo with no accounts, scored tool comparisons, deploy guides for Vercel, Railway and Hetzner, prompts for Claude Code and Codex, seed data with an answer key, and its own honest limits page. Every system also copies the same base, listed in `docs/BASE-VERSIONS.md`.

## What is in this repo

- `packages/core-py`: the shared API foundation (safety, audit, approvals, events, costs, model wrapper, jobs, auth, adapters, evals).
- `packages/ui-kit`: the shared design system and components.
- `packages/ARCHITECTURE.md`: the written contract of the base.
- `demo/`: a small app that shows the UI kit working, with screenshots in `demo/screenshots`.
- `tools/`: `sync_base.py` copies the base into a system repo, `check_base_copies.py` fails when a copy differs.
- `docs/`: business basics, comparison method, the combined tools scoreboard, base versions, system repo layout, facts and sources.
- `tools/demo_all.sh` starts all seven systems in demo mode on your computer (`start`, `stop`, `restart`, `status`, optionally with system names). Web on ports 3001 to 3007, API on 8001 to 8007, sign in with owner@example.test and demo-password-1 (demo data). It installs what is missing (uv or python3.12, pnpm) and keeps logs in `.demo-logs/`.
- `tools/combine_scores.py` rebuilds the scoreboard from the system repos, and `tools/consistency_pass.py` scans all eight repos for dashes, local paths, private links and broken links.

## Run the checks

```
cd packages/core-py && uv venv --python 3.12 .venv && uv pip install -p .venv/bin/python -e ".[dev]" && .venv/bin/python -m pytest --cov
pnpm install && pnpm --filter @sendora/ui-kit test
pnpm --filter demo build && pnpm --filter demo e2e   # needs Google Chrome installed
python3 -m unittest discover -s tools/tests
```

## Safe by default

Every system starts in draft mode with a kill switch. Nothing is sent, called, posted or paid until you switch to live mode on purpose. Text from outside (emails, tickets, resumes) is treated as data and never as instructions. Anything not run against the real vendor is marked UNVERIFIED in `docs/FACTS-AND-SOURCES.md`.

## Licence

MIT. See `LICENSE`.
