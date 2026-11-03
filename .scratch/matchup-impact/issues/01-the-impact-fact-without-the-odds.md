# 01: The impact fact, without the odds

Spec: `.scratch/matchup-impact/PRD.md`. Acceptance tests AT-4, AT-5, AT-6, and AT-8.

**App:** pipeline

**What to build:** Each matchup of a week gets one impact fact, `M<n>.impact`, for both of its teams. It holds five parts of the impact: the standings place before and after, the cut, the median result, the streak, and a clinch or an out. It holds only the parts that apply this week. The Matchup of the Week and recap prose blocks have it in scope. The Game Changer and Next Week prose blocks do not.

**Blocked by:** None. It can start now.

**Status:** in-review

- [x] A test on the fixture week reads `M<n>.impact` and finds the standings place before and after for both teams, as "rose from", "fell from", or "stayed" in the standings.
- [x] A test finds the median result of both teams and the record of each team for the week, such as 2-0, 1-1, or 0-2.
- [x] A test finds a head-to-head streak of 3 or more that the game started, extended, or ended, and no streak under 3.
- [x] Tests cover a team that crossed into the playoff spots, a team that fell out, a first clinch, a first out, and a loser who beat the median.
- [x] A test finds `M<n>.impact` in the fact lists of `motw` and each recap, and in neither `next_week` nor `game_changer`.
- [x] The fact text never says "moved" and never says "rank" alone, per **Standings place** in `GLOSSARY.md`.
- [x] The golden files hold the new facts, and `make check` passes.
- [ ] A build of `2026` week 8 records the evidence of AT-4, AT-5, AT-6, and AT-8 in `EVIDENCE.md`.

## Comments
