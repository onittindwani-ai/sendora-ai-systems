# Facts and sources (hub)

Every outside fact used in this repo, with where it came from and whether it was checked. VERIFIED means a current vendor or official page was read on the date shown. UNVERIFIED means it was not run or not found, and must be checked before you rely on it. Dates are when we checked.

## Libraries (registry metadata, checked 2026-11-22)

| Item | Version used | Source | Status |
| --- | --- | --- | --- |
| Next.js | 16.4.6 | https://www.npmjs.com/package/next | VERIFIED that it exists and builds the demo; its full API was not reviewed |
| React and React DOM | 19.3.1 | https://www.npmjs.com/package/react | VERIFIED |
| TypeScript | 5.9.3 (7.0.2 exists, not used) | https://www.npmjs.com/package/typescript | VERIFIED |
| motion, recharts, cmdk, sonner, dnd-kit core, Radix dialog, tabs, tooltip, lucide-react | see packages/ui-kit/package.json | npm registry | VERIFIED that they install and pass the tests |
| FastAPI 0.165, Pydantic 2.14, SQLAlchemy 2.1, httpx 0.28, argon2-cffi 25.1 | see packages/core-py/pyproject.toml | https://pypi.org | Ranges in pyproject are minimums; tests ran on Python 3.12 |
| Model prices in `costs.py` | Sonnet 5.5 2 and 10 USD per million tokens, Haiku 5.5 "from" 0.10 and 0.50 | https://platform.claude.com/docs/en/about-claude/models/overview (read 2026-11-23) | VERIFIED that the page says this on that day; the Haiku figure is a lower bound, so set exact prices for your account |
| Live Anthropic backend in `llm_anthropic.py` | not run against the real API | see the next section | UNVERIFIED live. Request shape checked against the docs and a local mock server only |

## Anthropic Messages API (docs read 2026-11-23)

Pages read: https://platform.claude.com/docs/en/api/messages, /api/errors, /api/overview, /api/versioning, /build-with-claude/structured-outputs and /about-claude/models/overview (the old docs.anthropic.com addresses redirect there). The excerpt of the Messages page the reader returned was cut off (100,000 of 1,324,833 characters), so the response body is confirmed only from the examples and the errors page.

| Fact used by `llm_anthropic.py` | Source | Status |
| --- | --- | --- |
| Endpoint `POST https://api.anthropic.com/v1/messages` | api/overview, api/messages | VERIFIED (docs) |
| Headers: `anthropic-version` and `content-type: application/json` are required; `x-api-key` is accepted ("legacy fallback for Authorization, still supported"), the primary form is `Authorization: Bearer <key>`. The code sends `x-api-key` | api/overview | VERIFIED (docs); which of the two the live service prefers for a new key is UNVERIFIED |
| Current `anthropic-version` is `2026-10-21` (the older `2023-06-01` is listed). Settable with `ANTHROPIC_VERSION` | api/versioning | VERIFIED (docs) |
| From version 2026-10-21 `temperature`, `top_p` and `top_k` are removed and a request that sends one gets a 400 on every model. The code never sends them | api/versioning | VERIFIED (docs) |
| Body fields `model`, `max_tokens`, `system` (string), `messages` (`role` and `content`) | api/messages | VERIFIED (docs) |
| Structured output: `output_config.format = {"type": "json_schema", "schema": {...}}`, no beta header, objects need `additionalProperties: false`, numeric, string length and most array constraints are not supported, `oneOf` is not supported (use `anyOf`). The code sanitises the schema and validates the reply with Pydantic afterwards | build-with-claude/structured-outputs | VERIFIED (docs) |
| Model ids `claude-sonnet-5-5` and `claude-haiku-5-5` exist and support structured output; pinned snapshots, no date suffix | about-claude/models/overview | VERIFIED (docs) |
| Sonnet 5.5 rejects `thinking: {"type": "disabled"}` and takes `{"type": "between_tools"}` for the lowest setting; Haiku 5.5 accepts `disabled`; forced tool use (`tool_choice` any or tool) is not supported on the 5.5 models. The code never forces a tool and sends a thinking field only when `LLM_THINKING=off` | api/errors | VERIFIED (docs) |
| Error body `{"type": "error", "error": {"type", "message"}, "request_id"}`; statuses 400 invalid_request_error, 401 authentication_error, 402 billing_error, 403 permission_error, 404 not_found_error, 409 conflict_error, 413 request_too_large, 429 rate_limit_error, 500 api_error, 504 timeout_error, 529 overloaded_error. Response header `request-id` | api/errors, api/overview | VERIFIED (docs) |
| Retry guidance: transient failures (connection errors, rate limits, 5xx) are retried with exponential backoff and a `retry-after` header is honoured when present. A spend cap 429 has no `retry-after` | api/errors | VERIFIED (docs). The code retries 408, 429, 500, 502, 503, 504, 529 and network errors, and caps a retry-after wait at 30 seconds |
| Success body: `content` array of blocks (text blocks carry the answer, thinking blocks are skipped), `usage.input_tokens` and `usage.output_tokens`, `stop_reason` (`end_turn`, `stop_sequence` documented; `max_tokens` and `refusal` assumed) | api/messages (examples only) | UNVERIFIED in part: the field names `usage.*` and `content[].type` come from the SDK convention, not from a page excerpt I could read in full |
| Thinking tokens may count toward `max_tokens`, so the default `LLM_MAX_TOKENS` is 4096 | not found in the pages read | UNVERIFIED (a safety margin, not a fact) |
| Whether `LLM_THINKING=off` saves money or time on a given model | not measured | UNVERIFIED |
| Everything above run against the real API with a real key | not done | UNVERIFIED. Tests use a local mock server written with the standard library (`packages/core-py/tests/stub_anthropic.py`) and recorded fixtures |

## Tests that were run on the base (2026-11-23, base 1.2.0)

- tools: 15 unit tests passed.
- core-py: 56 tests passed, 99 percent line coverage (934 statements, 14 not covered). The model path is tested against a local mock of the Anthropic endpoint (standard library server) that asserts the request path, headers and JSON body, plus recorded fixtures. No call to the real API was made.
- ui-kit: 62 tests passed (91 percent of statements, 95 percent of lines), plus a contrast test with 20 checks. `tsc --noEmit` passes for ui-kit and the demo.
- demo app: `next build` succeeded, 14 Playwright checks passed in desktop Chrome (installed Google Chrome, no browser download): screenshots at 1440x900 and 390x844, axe with no serious or critical findings on four pages (Pipeline now has a link inside each card) and in the dark theme, a keyboard path, Kanban cards that are not buttons and open from the keyboard, Kanban keyboard lift and drop, reduced motion, 5,000 rows, a Kanban drag, and no layout shift on load.
- Not run: Safari and Firefox, a screen reader, real phones, production hosting, the real Anthropic API.

## Business basics (checked 2026-11-22, see docs/00-BUSINESS-BASICS.md)

| Fact | Source | Status |
| --- | --- | --- |
| EIN online application is free, for entities in the US or its territories, needs the responsible party's SSN or ITIN, one EIN per responsible party per day, 15 minute session | https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online | VERIFIED 2026-11-22 |
| Moving DNS from Namecheap to Cloudflare means setting custom nameservers at Namecheap and recreating the records at Cloudflare | https://www.namecheap.com/support/knowledgebase/article.aspx/9607/2210/how-to-set-up-dns-records-for-your-domain-in-a-cloudflare-account/ and https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/ | VERIFIED from search summaries 2026-11-22, pages not opened one by one |
| Telnyx 10DLC order: brand, vetting, then campaign. Vetting gives a trust score from 0 to 100. A campaign sent before vetting finishes fails | https://developers.telnyx.com/docs/messaging/10dlc/quickstart/index and https://developers.telnyx.com/docs/messaging/10dlc/brand-registration | VERIFIED from search summaries 2026-11-22 |
| Website, company name and EIN should match the registration | https://support.telnyx.com/en/articles/6325747-10dlc-messaging-throughput-trust-scores-campaign-use-cases-and-vetting | VERIFIED from a search summary 2026-11-22 |
| Telnyx fees (brand registration and vetting) | https://support.telnyx.com/en/articles/6325747-10dlc-messaging-throughput-trust-scores-campaign-use-cases-and-vetting | UNVERIFIED. Sources disagree, check the portal |
| How long vetting stays valid | same | UNVERIFIED. Sources say both "does not change" and "expires after 6 to 12 months" |
| InboxKit and SendKit domain, DNS and mailbox requirements | none found | UNVERIFIED. Read their own docs before buying domains |
