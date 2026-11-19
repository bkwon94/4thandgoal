# 09: The gain check and the backtest

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-46, AT-47, AT-51, and AT-54.

**App:** api

**What to build:** The Shortlist asks one gain Noul per side: "Does {team} start a better lineup after this trade?", with the lineup points of each side before and after the trade as facts. A clear no, below `NO_AT` 0.3, drops the offer. An unsure answer stays. A failed call is an error, never a no. One command runs the Spares tree on every CPC pair of week 11 and writes about 30 lines for Brian, each one stop or pass with the answer that decided it. Brian marks the wrong lines, in about 10 minutes. Each wrong line with his fix is a Backtest mark, with "Kenneth Walker III for Patrick Mahomes" and "Zay Flowers for Jared Goff" as the first two. The backtest command checks each mark against the tree and prints the result, and it does not run in `make check-fast`. The `finder` flag of CPC stays off, and the `next` version stays as on `main`.

**Blocked by:** 08

**Status:** ready-for-agent

- [ ] A real press for Bo Girds and every team shows neither of the two bad trades on the Shortlist or among the 3 trades.
- [ ] The list of about 30 lines goes to Brian, and his marks are saved as Backtest marks.
- [ ] The backtest command prints each mark with its result, and every mark is right.
- [ ] The `finder` flag of CPC is `false`, and the `next` version matches `main`.
