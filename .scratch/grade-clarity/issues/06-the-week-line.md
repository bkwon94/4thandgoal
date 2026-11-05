# 06: The Week line

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-5, AT-11, AT-12, AT-13, AT-14, AT-17, AT-18, and AT-34.

**App:** both

**What to build:** Each side of a grade gets a Week line for the trade week and the next week, in a box "This week and next" on its card. For each position the trade touches, the line counts the players of the side who play, are not out, and rank above the line, before and after. It names the opponent of each player the side gets with its rank, each bye, and each player who is out. It never moves the letter. The verdict can name it.

**Blocked by:** 01, 02, 05.

**Status:** ready-for-agent

- [x] Each side of the document holds `week_lines`, a list of `{week, text}` for the trade week and the next week only.
- [x] Out counts in the trade week only. IR, PUP, NA, and Sus, out for the season, and a return week after the next week count in both weeks. Questionable and Doubtful never count.
- [x] A grade on a Tuesday or a Wednesday says "listed Out last week".
- [x] The fact sheet holds one Week line fact for each side. No factor is a Week line row.
- [x] A three-side trade gives three sides with Week lines.
- [x] The side card shows the box "This week and next" between the bullets and the fold.
- [x] `make check-fast` passes at the root.

## Comments

- The code writes each Week line in `packages/analyzer/python/src/analyzer/week_line.py`. The result document, the fact sheet (`<roster>.week_line`), and the cache key read it. No adjuster reads it.
- The trade A lines on the saved week 8 data, graded on a Thursday: roster 10 reads "Week 9: WRs in the top 36 who play stay at 2. Washington plays at BAL, 9th most points to WRs. Bernard has a bye. Egbuka and Samuel are listed Out." and "Week 10: WRs in the top 36 who play stay at 2. Washington plays at TEN, 1st most points to WRs. Egbuka has a bye." Roster 6 stays at 3 in both weeks, and Cooper plays at KC, then BUF at home.
- The schedule now holds the game of each week: `TeamSchedule.games`, with the opponent and home or away. A home game reads "Cooper plays BUF at home".
- The grade time is `AsOf.graded_at`, the `now` of the request. A saved week has none, so its text says "is listed Out". The day is the one in US Eastern time. The cache key holds the Tuesday-or-Wednesday flag, because the text changes with it.
- `DOCUMENT_VERSION` goes to 16. The API and site fixtures hold the Week lines of a real run on the week 6 fixture.
- The agent made no live run of `make analyze`: the live path saves the week to the history and reads the value chart with Claude. The tests grade trade A on the saved week 8 data and the 2026 schedule of the nflverse fixture.
- For Brian: the line names the bye and the absence of each player of the side after the trade at each position the trade touches, at any rank, not only the players in the top N. It does not name a player the side gives.
- For Brian: the words of each absence. "is listed Out" (or "was listed Out last week" on a Tuesday or a Wednesday), "is on IR", "is on the PUP list", "is not active" for NA, "is suspended" for Sus, "is out for the season", and "is out until week 11" for a return week on file. A count with no change reads "stay at 2".
- For Brian: with no NFL schedule on file, every player counts as one who plays, and the line ends "No NFL schedule is on file, so no bye or opponent shows."
- For Brian: the analysis prompt now says the Week line fact moves no letter and that a bullet or the verdict reason can name it when this week matters.
- Steps up (ticket 07) adds its sentence in `_text` of `week_line.py`, after the absences. The status of each player that a Week line reads is not yet in the cache key; ticket 07 adds it.
