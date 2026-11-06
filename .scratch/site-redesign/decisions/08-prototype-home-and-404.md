# 08: What do the home page and the 404 page show?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** prototype

**Blocked by:** 03, 04

**Status:** done

## Question

The home page is the first view of a new reader, so it carries most of the first reaction. Settle what it shows and in what order. Settle the 404 page in the same look.

## Decision

The home page uses board "Home 1 · Front page". The 404 page uses page A, "Hero", of board "404 · three pages". Brian chose this on 2026-11-05, on the canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8. He agreed with Claude's recommendation.

The home page, in this order:

1. The top band and the dock of decision 04, with Home active on the dock.
2. The intro: the season label and the site name of the brand copy.
3. The hero: the Matchup of the Week of the latest week, with its reason, the margin as the big number, both teams with avatars and scores, the first sentence of the blurb, and a "Read Week N" button.
4. The four numbers of the latest week, as on the week page: the top score, the median, the closest margin, and the Game Changer gap over projection.
5. Power Rankings: the top three, each with the rank, the avatar, the record, the movement, and the playoff odds, then a link to all teams.
6. Tools: one tile for each tool of the client, such as Trade Analyzer and Managers, each with an icon and one line of copy.
7. Weekly Reports: one row for each published week, newest first, with the week number, the dates, and the teams of its Matchup of the Week.

Each package still gives its own part of the home page through the registry, so a client with no rankings shows no Power Rankings part.

The 404 page:

- The top band and the dock, with no dock item active.
- A hero with the grid, the brackets, and the glow. It holds the label "ERROR // PAGE NOT FOUND", a big "404", and the line "This page does not exist. The link may be old, or the week is not out yet."
- Two buttons: "Go to Week N" for the latest week, in the brand color, and "Go Home".

Brian rejected board "Home 2 · Scoreboard", because six score cards in the hero are busy for a first view. He rejected board "Home 3 · Launcher", because a grid of doors repeats the job of the dock. He rejected 404 B, "Scoreline", because its joke is harder to read, and 404 C, "Wayfinder", because its list repeats the dock.

The home page uses only the published data: the week pages, the rankings file, and the brand copy. So the list of ideas that need new data stays empty.

The prototype lives on the canvas, not in the repo, so no prototype code needs a delete.
