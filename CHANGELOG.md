# Changelog

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
