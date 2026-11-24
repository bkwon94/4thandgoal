# 02: The API refuses each trade route after the Lock

Spec: `.scratch/trades-closed/PRD.md`. Acceptance tests AT-14, AT-16, AT-17, AT-18, AT-21, AT-22, and AT-27.

**App:** API.

**What to build:** After the Lock of a client, the API answers each trade route with the closed reply: HTTP 410 with the body `{"closed": true, "line": "The trade deadline has passed. Trades open again next season."}`. The routes are `/analyze`, `/find`, `/trade-check`, `/trade-ideas`, `/find-stream`, `/sell-high`, and `/deadline/trades`. A refused call makes no Jev call and no Claude call. `/teams` stays open. `/suggestions` makes no `trade_ideas` or `sell_high` fact and offers no trade Topic. The fair warm-up skips a closed client, and a press or the Trade Wire never wakes it for that client. Before its Lock, NorCal answers as now.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] A pytest calls each of the 7 routes for `cpc` after the Lock and gets 410 with the closed body (AT-14).
- [x] A pytest with a counting fake Jev and fake Claude shows 0 calls for the 7 refused routes (AT-16).
- [x] A pytest shows that the fair warm-up never warms a closed client. A start of the local evidence API logs no "Fair warm-up of cpc started" (AT-17).
- [x] `POST /clients/cpc/suggestions` for roster 1 holds no trade Topic and no trade fact (AT-18).
- [x] A pytest with the clock at 12:00 Eastern on 2026-12-14 shows that the NorCal `/trade-check` still grades (AT-21).
- [x] A pytest with the clock at 00:00:01 Eastern on 2026-12-15 shows that the NorCal `/trade-check` returns 410 (AT-22).
- [x] The diff of the spec changes no file under `packages/eggs/` (AT-27).
