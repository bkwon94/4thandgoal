# 04: The front door closes its trade Topics

Spec: `.scratch/trades-closed/PRD.md`. Acceptance tests AT-6, AT-7, AT-9, and AT-12.

**App:** both. The site and the API.

**What to build:** A site build of a client with Trades closed leaves out the trade Topics `trade_ideas`, `trade_check`, and `sell_high` from the chips, the day order, the More list, and the follow-ups, and leaves out the trade block strip. The Tour line of the ask box names no trade. At the API, when Jev routes a question to a trade Topic for a closed client, the answer is the closed line "The trade deadline has passed. Trades open again next season." from code, with no Claude call. The free answer gets no trade tool for a closed client. The Topic `leaders_trades` stays.

**Blocked by:** 01

**Status:** in-review

- [x] A closed `cpc` build with roster 1 shows no "Trades", "Check", or "Sell high or buy low" chip or Suggestion, and no trade block strip (AT-6).
- [x] The typed question "Who should I trade for at RB?" gets the closed line, never "I can't answer that.", and the API log shows no Claude call (AT-7).
- [x] The Tour step of the ask box has no word "trade" (AT-9).
- [x] The Topic "Position leaders and recent trades" still answers with the recent trades of 2026 (AT-12).
- [x] A pytest shows that a trade question for an open client still routes to its trade Topic.
