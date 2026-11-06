# 20: The letdowns of the draft

Spec: `.scratch/midseason-report/PRD.md`. Acceptance test AT-65.

**App:** both

**What to build:** Brian asked for this on 2026-11-06. A letdown is a pick with a top 10 price of the whole draft, which is not a bust, and which has no week in the top 17 of his position in the last 4 weeks played. For a snake draft, the price is the pick number. The pipeline adds `letdowns` to the draft facts of `midseason.json`: player, team, price, price rank, season rank at the position, and the last week in the top 17. The writer can cite each one. The site shows the letdowns under the busts of the draft chapter, as quiet rows of ticket 18, with the word tag "letdown". The weekly rank uses the points of the league scoring.

**Blocked by:** none.

**Status:** ready-for-agent

- [x] `midseason.json` of CPC week 8 lists Bijan Robinson as a letdown: $81, price rank 1, RB3, last top 17 week 4.
- [x] No player is both a bust and a letdown.
- [x] A rule test covers a pick with a top 17 week in the last 4 weeks, which is not a letdown.
- [x] The draft chapter of the page shows the letdown rows under the busts.
