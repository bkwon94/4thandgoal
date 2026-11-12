# 01: What is the shape of the front door lineup?

Map: `.scratch/front-door-lineup/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The outcome statement names three parts: a Start or sit Topic, a shorter row of Suggestions, and more blocks. The spec needs the destination, the data, the judgment, the scope, and the words before the other decisions.

## Decision

Brian decided each item in the Stage 1 grill on 2026-11-11.

1. The goal: a manager opens the site on game day and leaves with a lineup decision. The Answers show richer blocks than a list or a table. The Suggestions take one short row, so the Thread gets the screen of a phone.
2. One spec, `front-door-lineup`, for both apps.
3. The new blocks show in both paths: in a free answer, and in each Topic Answer that matches a block. Most managers tap a Suggestion and never type.
4. Start or sit reads live data on the API, as the personal Topics do. The weekly build is five days old by Sunday.
5. The data is Sleeper only. Sleeper gives the status, the body part, the practice level, and a projection that updates through the week. It gives no news text. A news source is out of scope.
6. Free judgment: Jev weighs the whole fact sheet and may bench a player with a higher projection. The projections come from Rotowire (`company: rotowire`), which already prices in the opponent. Brian chose free judgment over "projection first" with that risk known.
7. No backtest gate. Brian judges the calls by feel after the ship.
8. Every slot, the DEF of cpc too. cpc is half PPR with 2 FLEX and a DEF. norcal is full PPR with 3 FLEX and no DEF. Code scores each projection from its stat line with the scoring of the league.
9. The order of the day: Start or sit leads Thursday to Sunday, and "Your next matchup" moves to second place. It is third on Wednesday, after waiver targets. Jev lifts it on any day when a starter is OUT, on IR, or on a bye. Monday stays as it is.
10. A Questionable starter gets a "Q" tag with his practice level, and a pivot line: "Start Kamara if he is active. If he is ruled out, start Allgeier." Code picks the pivot as the best legal bench player for the slot.
11. A typed "Start A or B?" with two players of Your team goes to Start or sit, with the comparison block. A player off the roster goes to a free answer. Three or more players get the lineup block for the slot.
12. The words: Start or sit (key `start_sit`), Week lineup, Swap, Pivot, Fact sheet. See `GLOSSARY.md`.
13. Thirteen blocks in v1: lineup, two-player comparison, matchup card, schedule strip, standings ladder, slot rank bars, trade card, rank mover list, NFL game card, bye grid, transaction feed, recap card, and the text block. The text block is the default for the text of every Answer: a small subset of markdown, with the marks stripped before the Jev check. Decision 09 sets the subset.
14. The design bar holds for every UI ticket: `transitions-dev`, scrolltide components when one fits, `apple-design`, `animate`, `critique`, `polish`, and `frontend-design` or the claude.ai Design artifact as needed.

The hard rules in code are facts only: slot eligibility, the bye, OUT, IR, or suspended, and the game lock. The fact sheet holds the projection and its stat line, the defense against the position (`fan_pts_allow_<pos>` of the Sleeper DEF rows), the team strength from `pts_allow`, the expected margin, the pass or run tilt, the share of targets, carries, and snaps over 3 weeks, the status, and the win odds of the fantasy matchup.
