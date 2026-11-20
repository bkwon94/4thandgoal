# 15: The Ledger cards, the near fold, and the new wait

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-36, AT-38, AT-65, AT-66, AT-67, and AT-68.

**App:** site

**What to build:** Each Finder trade lands as the Ledger card of prototype 17 (branch `deadline-week-17-proto`, `c403b55f`). The card has "You get · N" and "You give · N" columns, a row per player with the position, the NFL team, and the rank, no trade value on a row, and a trade value total under each column. One plain line under the totals states the gap, such as "You get 9% more trade value". The Lean, the Case of up to 3 lines, the folded Bullets, and "See the Full Result" stay. Up to 5 cards show, then "Close, but not sent · N", folded, with up to 3 near ideas. The wait shows the new lines with the real counts of the press, each with the "n of 5 ·" prefix: "Reading 11 teams", "Matching trade value", "Checking N trades for fairness", "Checking N against both lineups", and "Picking the best 5". The meta line "This can take about 25 seconds." goes, and no copy states a time. Site copy names no internal tool. Use the design bar of the repo: transitions-dev, apple-design, critique, and polish.

**Blocked by:** 14

**Status:** in-review

- [ ] A real press for Bo Girds on the local API shows Ledger cards of three different shapes, at 375, 768, and 1280 px, in both themes.
- [x] A card with totals of 68.0 and 62.5 shows "You get 9% more trade value".
- [x] Up to 5 cards show, then the "Close, but not sent" fold with up to 3 near ideas.
- [x] The wait shows each new line with the real counts, one at a time, and no count of seconds or minutes.
- [x] Playwright WebKit at 390x660 finds no text overlap and no fixed bar over content.

## Comments

- 2026-11-20: Brian changed AT-65 to three different shapes, because the gain check drops every 1-for-1, 2-for-1, and 3-for-1 offer of Bo Girds. The evidence stage proves box 1.
