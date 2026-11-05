# 02: Layout A with bullets

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-10, AT-21, AT-27, AT-28, AT-29, and AT-33.

**App:** both

**What to build:** A manager grades a trade and reads layout A. The decision and its "why" sentence come first, then the trade card, then one card for each side, then the as-of line. Each side card shows the players it gets and gives, 2 or 3 bullets from Claude in place of the paragraph, and the rows in a closed fold "How the grade adds up · <n> rows". The deal row replaces "The Data". The as-of line names no chart week. A week with no values shows the new note. The fallback shows no bullets, and the rows still show.

**Blocked by:** None. It can start now.

**Status:** in-review

- [x] Each side of the document holds `bullets`, a list of 2 or 3 strings, in place of `analysis`. The prose checks run on each bullet.
- [x] The chart sentence is the first factor of each side, the deal row, in plain words that name no source. No `chart` block stays.
- [x] `as_of.no_chart_note` reads "This week's player values are not out yet, so both sides start even." The as-of line has no "Chart week".
- [x] After two failed Claude calls, `fallback` is true, each side has no bullets, and the factors still show.
- [ ] The site renders layout A in one column at each width. The fairness line stays under the decision. The counters slot stays as now.
- [ ] The two players of a side stack at 375 px and stand next to each other at 768 and 1280 px. The fold is closed before a tap.
- [x] The view reads no query string.
- [x] The finder prompt and the finder cards do not change.
- [x] `DOCUMENT_VERSION` goes up by one.
- [x] `make check-fast` passes at the root.

## Comments

- The merge: `2f17042` into `grade-clarity` on 2026-11-05. `make check BASE=main` passed.
- Two boxes stay open: one column at each width, and the players stack at 375 px. jsdom cannot measure a width. The screenshots of the evidence stage prove them.
- The finder shares the as-of line, so its line also loses "Chart week", and its no-values note has the new text. The finder prompt and the finder cards do not change.
- Brian checks the deal row text for a trade of one player for two: "after a discount on the side with more players".
- `GLOSSARY.md`: "Deal row" replaces "Chart lean", and "Bullets" is new.
