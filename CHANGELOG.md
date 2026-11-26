# Changelog

## 1.2.8 (base)

- Documentation and demo label updates.

## 1.2.7 (base)

- core-py: `/ready` answers only `{"status": "not_ready"}` on a failure and writes the cause to the log. SQLite connections wait up to 30 seconds for a write lock (the default 5 seconds turned two busy writers into `database is locked` in CI and on small servers).

## 1.2.6 (base)

- core-py: a model that is not in the price table is priced at the highest known price, so `LLM_BUDGET_USD` still trips (it was free before). The `ANTHROPIC_BASE_URL` check compares the host: `http://localhost.evil.net` no longer counts as local.

## 1.2.5 (base)

- core-py: the app refuses to start with an example or short `SESSION_SECRET` whenever an owner password is set, also while `DEMO_MODE` is on (an owner token could be forged with the public example secret). `/health` answers only `{"status": "ok"}` and no longer names the mode or the kill switch. `verify_audit_chain` reads the log in batches (optionally only the newest rows) instead of loading all of it. `session_secret` is left out of the text of the settings (`repr=False`).

## 1.2.4 (base)

- core-py: `make_engine` sets `hide_parameters`, so an error from the database never prints the values of the failed statement (names, amounts, pasted text). `Worker.run_once` rolls back before it records a failed job, so a job that broke its own transaction is still marked failed with its error.

## 1.2.3 (base)

- core-py: an empty value in the environment or in `.env` counts as not set (`env_ignore_empty`). `cp .env.example .env` left lines such as `CALCOM_EVENT_TYPE_ID=` that crashed the API at start in two systems (found by the Docker job in CI).

## 1.2.2 (base)

- core-py: the app refuses to start when `DEMO_MODE` is off and `SESSION_SECRET` is under 32 characters or an example value (anyone who has read the public code could otherwise sign in as the owner), and when `DEMO_MODE` is on with a Postgres database unless `ALLOW_DEMO_SERVER=true`. `demo_shortcuts` is false as soon as an owner password hash exists. The interactive docs and the schema list are served only in a demo.
- core-py: a request body over `MAX_BODY_BYTES` (25 MB) is refused before it is read, also when it arrives in chunks. The rate limiter keeps at most 10,000 keys and cuts long keys. Open event streams are capped at 50 and end when the browser disconnects.
- core-py: an approval is decided by one conditional update, so two people deciding at once cannot both win (double send). A job whose worker died is queued again after 30 minutes and marked failed after its last attempt. The audit chain takes an advisory lock on Postgres so it cannot fork. A non ASCII token or signature is a refusal, not an error. The model address must be https (or localhost).
- core-py: `fixture_key` ignores runs of spaces, so recorded model answers replay the same on every operating system (the same test passed on macOS and failed on Linux). Fixtures were re-recorded in every system. New helpers `clean_email` and `verify_password_or_dummy` for the login routes.
- tools: `make_ci.py` writes one pinned GitHub Actions workflow into every system, `make_constraints.py` pins the Python packages, and `consistency_pass.py` checks the workflow.

## 1.2.1 (base)

- ui-kit: `CountUp` rounds each step of the count to the number of decimals its target has, so a custom format such as `${n}%` no longer prints 70.948037512176 on the way to 71. New exports `countPrecision` and `roundCountStep`, with tests.

## 1.2.0 (base)

- core-py: read only `viewer` role with `require_read` and `require_write` route guards. `approvals.decide` refuses the person who requested the action (`SelfApprovalError`). A real Anthropic Messages backend over httpx, chosen with `LLM_BACKEND=offline|fixture|anthropic` (offline stays the default), with structured JSON output (parse, validate, one repair), retries with backoff on 429, 5xx and 529, cost tracking, a call budget and a spend budget, kill switch respected, fixture recording and replay, redacted logs, and an untrusted content block. Model prices updated from the vendor page. Live use is UNVERIFIED.
- ui-kit: Kanban cards are labelled groups instead of buttons, so they can hold buttons and links; optional `onOpen` and `cardLabel`; Enter on a focused card opens it.
- docs: the three base changes requested by the builders are done.

## Hub 2026-11-23 (no base change)

- docs: `TOOLS-SCOREBOARD.md` (generated, 134 scored tools in 45 groups across seven systems), `BASE-VERSIONS.md`, business basics section 8 (what each system needs), README index of the seven planned repos.
- tools: `combine_scores.py` and `consistency_pass.py`, with tests.

## 1.1.1 (base)

- ui-kit: Dialog and Sheet use the solid surface colour so text behind them never ghosts through.

## 1.1.0 (base)

- ui-kit: the app shell search button now has the accessible name "Search" (it matches the visible text). Card titles render as h2 by default (new `headingLevel` prop) so a page heading is followed by h2. Keyboard key glyphs use a font stack that shows the command symbol on phones. Overlay animation is 320 ms and `OVERLAY_SETTLE_MS` (450) is exported for screenshot waits.
- tools: `check_env.py` joins the base files (copied into every system by `sync_base.py`).


## 1.0.0 (base, unreleased)

- core-py: settings, database, safety (draft mode and kill switch), audit chain, approvals, events and metrics, redaction, cost tracking, model wrapper with recorded fixtures, job queue, auth, server sent events, rate limit, adapter registry, evals, FastAPI base app.
- ui-kit: tokens, light and dark themes, seven accents, 35 components, demo app with browser checks.
- tools: sync_base.py and check_base_copies.py.
- docs: business basics guide, comparison method, facts and sources.
