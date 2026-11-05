# Grade clarity: map

App: both.
Spec branch: `grade-clarity`.

## DESTINATION

The analyze route gives a grade that a manager reads in under a minute. The grade says why each side wins or loses this week and for the rest of the season, and each number in it matches Sleeper.

## DECISIONS SO FAR

- The goal: a manager reads a grade in under a minute, sees why each side wins or loses this week and for the season, and trusts each number. Brian, 2026-11-05.
- The spec covers the trade grade only. The finder gets the shared fixes of the facts, but its prompt and its view stay as they are. Brian, 2026-11-05.
- The view leads with the verdict and one "why" sentence. Each side gets 2 or 3 short bullets in place of the paragraph. The adjuster rows fold away. Brian, 2026-11-05.
- No text names the value chart or another inner part of the grade. Each adjuster row uses plain words. Brian, 2026-11-05.
- The slot fact goes, so no text says "takes RB1" or "sits on the bench". The best lineup stays inside the code as a measure of depth. Brian, 2026-11-05.
- The main rank in the text is the Season rank, by total points, as Sleeper sorts it. A Recent rank shows only on a large gap, always with its label. Brian, 2026-11-05.
- Each side gets a Week line for the trade week and the next week. It stands beside the letter and never moves it. The verdict can name it. Brian, 2026-11-05.
- The Week line counts, for each position the trade touches, the players of the side who play that week, are not out, and rank above the line. It assigns no lineup slot. Brian, 2026-11-05.
- A player steps up for a week when the player directly ahead of him on his NFL team's depth chart, at his position, is listed Out or IR. Questionable and Doubtful do not count. QB, RB, WR, and TE only. Brian, 2026-11-05.
- The Week line shows for every side. ADR 0004 still holds for the roster fit adjuster. The race of the side weighs the Week line in the verdict only. Brian, 2026-11-05.
- The other data of a grade is correct for now, so no audit of the numbers runs. Brian, 2026-11-05.
- The terms Season rank, Recent rank, Week line, and Steps up go into `GLOSSARY.md`. Position rank keeps its name as the measure inside the grade. Brian, 2026-11-05.

## NOT YET SPECIFIED

- Which measure ranks players inside the grade, for the line and the holes? `decisions/01-research-rank-measure.md`.
- How fresh are the nflverse depth chart and the Sleeper injury status when a grade runs? `decisions/02-research-depth-chart-freshness.md`.
- What plain words does each adjuster row use, and where does the text name the value chart today? `decisions/03-grill-plain-adjuster-rows.md`.
- What shape does the result view take? `decisions/04-prototype-result-view.md`.
- How large is the gap between the Season rank and the Recent rank that shows the Recent rank? `decisions/05-spec-recent-rank-gap.md`.

## OUT OF SCOPE

- The prompt and the view of the trade finder. The goal is about the grade, and only `norcal` turns on the finder.
- The Position rank of the weekly report. The weekly report has its own readers, and this spec changes the grade only.
- A Week line past the next week. The letter already grades the rest of the season.
- An audit of the other numbers of a grade. Brian sees no other wrong number now.
