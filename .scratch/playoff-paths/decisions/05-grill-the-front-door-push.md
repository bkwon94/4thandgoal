# 05: How does the front door push to the sim page?

Map: `.scratch/playoff-paths/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

The race is the most important thing at this point in the season, so the front door must push visitors to the sim page. Decide if the push is a link chip, such as "What do I need to make the playoffs?", or a Topic that Jev answers in chat with the Finish list of Your team and a link. Decide also where the push sits among the example questions, and when it stops.

## Decision

The playoff race Topic (`_playoff_race` in `apps/pipeline/src/cornerstone/topics.py`) is the first of the 3 Suggestions of the front door in each week of the regular season. The pin stops when week 14 is final. In the playoff weeks the Topic ranks like any other Topic. Its Answer keeps the odds and the near rows, and adds Your team's top 3 Finishes for a playoff spot, the status pill of The Race (Clinched or Out, none when In the hunt), and the link "Open The Race" to `/sim/<season>/`. Brian chose option A, 2026-11-24. A link chip skips the chat, which is the job of the front door. A card adds a fourth kind of part to a crowded screen.
