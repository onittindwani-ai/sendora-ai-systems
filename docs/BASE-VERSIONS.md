# Base versions

The base (`packages/core-py`, `packages/ui-kit`, `packages/ARCHITECTURE.md` and a few tools) lives in this hub and is copied into every system repo with `tools/sync_base.py`. `tools/check_base_copies.py` fails when a copy differs from the hub. A system never edits its copy: a change goes into the hub, gets a new version and is synced into every system.

## Releases

| Base version | Tag | What changed |
| --- | --- | --- |
| 1.0.0 | `base-v1.0.0` | First base: shared API core, 35 UI components, themes and accents, sync and drift tools |
| 1.1.0 | `base-v1.1.0` | Search button name, card heading level, key glyphs on phones, overlay settle time, `check_env.py` |
| 1.1.1 | `base-v1.1.1` | Solid background for dialogs and sheets |
| 1.2.0 | `base-v1.2.0` | Viewer role, approvals refuse the requester, Kanban cards can hold buttons, Anthropic model path |

## What each system carries

| System | Folder while unpublished | Base version | Copy check |
| --- | --- | --- | --- |
| Pipecairn | `pipecairn` | 1.2.0 | OK |
| Ringlark | `ringlark` | 1.2.0 | OK |
| Booklantern | `booklantern` | 1.2.0 | OK |
| Deskfern | `deskfern` | 1.2.0 | OK |
| Lorefern | `lorefern` | 1.2.0 | OK |
| Penlark | `penlark` | 1.2.0 | OK |
| Slatehire | `slatehire` | 1.2.0 | OK |

Checked on 2026-11-23 with `python3 tools/check_base_copies.py <each system folder>`.

## Changes the builders asked for (all done in 1.2.0)

1. A read only role next to owner and approver in the auth module: done, role `viewer` with `require_read` and `require_write` (Lorefern, Penlark and Slatehire each worked around it and can now use it).
2. `approvals.decide` refuses a decision by the person who asked: done, `SelfApprovalError` (the systems still refuse in their own routes, which keeps working).
3. The Kanban card holds buttons and links and has a keyboard route to open it: done, a labelled group with `onOpen`, `cardLabel` and an Open button (Lorefern and Slatehire).
