# 01: survey of egg spots on the CPC site

An Opus agent read the code of `main` at `df2c08c0` on 2026-11-06. It changed no file.

## Facts

- CPC takes week, rankings, midseason, managers, analyzer, and sim. The midseason page `/midseason/2026/` is frozen at week 8. The sim replay is its finale at `#sim`.
- The site has no global footer. The logo is a link to home, so a tap on it leaves the page.
- Old week pages and the midseason page never change after they publish. They give the most stable ids.
- Avatars have no data id. Headshots fall back to initials, and DEF players have none. A target on them needs a context id.
- The API guards every route except `/health` with the passphrase. A route for the listener needs its own open route or the same guard.
- The analyzer result is client state. The trade condition needs a trade key on the result root, or the API matches the last analyze call.
- iOS opens a callout on a long press of a link or an `img`. The listener must call `preventDefault` on `contextmenu` only on egg targets.
- The sim timer moves to the next frame each beat, so a target can unmount during a multi-tap.

## Ranked spots

1. Sim champion trophy: replay the sim until roster X wins, then long press the trophy. `packages/sim/site/replay/champion-card.tsx`.
2. Sim final standings: triple-tap the row of roster X at seed 6, the cut line. `standings.tsx`.
3. Sim bracket: tap 3x the chip of roster X in the semifinal. `bracket.tsx`.
4. Midseason Luck table: long press the cell of roster X, in light mode. `act-one/luck.tsx`.
5. Midseason Top 10: choose the DEF or TE chip, tap 4x the rank-10 row. `act-one/top10.tsx`.
6. Midseason bench list: open "Show all", double-tap row 9 or later. `act-two/lineup.tsx`.
7. Midseason Look Ahead: open "Show all", long press the game of week 14. `act-three/look-ahead.tsx`.
8. Midseason act heading: tap 5x "What Comes Next", in light mode. `report/act-title.tsx`.
9. Old week recap: week 6, open one game, long press the "Won by" line. `all-matchups.tsx`.
10. Old week position leaders: week 7, DEF chip, triple-tap the rank-3 row. `position-leaders.tsx`.
11. Old week awards: long press the points of one award tile. `awards.tsx`.
12. Old week median bar: tap 3x the bar of roster X. `median-game.tsx`.
13. Old week next-week card: long press the must-watch card, in light mode. `next-week.tsx`.
14. Rankings old week: chip week 2, open the card of roster X, double-tap the Sched tile. `power-rankings.tsx`.
15. Rankings old week hero: chip week 1, tap 3x the "01". `TopHero`.
16. Rankings movement arrow: long press the row of a down arrow on an old week.
17. Manager grade popover: open the grade, long press one factor row. `grade-popover.tsx`.
18. Manager result chip: tap 4x the chip of week 3. `manager-hero.tsx`.
19. Manager moves: long press the "Dropped" row of an old week. `moves.tsx`.
20. Analyzer verdict: grade one exact trade, long press the answer word. `analyze-result.tsx`.
21. Analyzer fold: open "How the grade adds up", tap 3x the "Handcuff" row. `analyze-result.tsx`.
22. Analyzer fold-line avatar: long press the avatar of the partner after a grade. `fold-line.tsx`.

## Bad targets

The logo, the managers index cards, the standings rows, the theme button, every nav link, the hero corner brackets, the latest week page, the home page, the points-line dots (10 px), bare avatars and headshots, the 404 page, the analyzer player rows, the "Sim the season" button, and the passphrase box. Each one is a link, a toggle, too small, too visited, or changes each week.

## Taps that already mean something

Toggles undo on a second tap: the game cards, the ladder cards, the chips, "Show all", and the analyzer fold. The week chip strip closes on a `pointerdown` anywhere. The grade popover closes on a tap outside. The `.press` class scales on tap, which is harmless.
