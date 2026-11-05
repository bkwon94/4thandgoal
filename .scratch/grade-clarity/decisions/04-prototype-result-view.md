# 04: The shape of the result view

Map: `.scratch/grade-clarity/MAP.md`.

**Kind:** prototype

**Blocked by:** 03

**Status:** done

## Question

The view leads with the verdict and one "why" sentence. Each side gets 2 or 3 bullets and a Week line. The adjuster rows fold away. The order and the look of these parts on a phone are not set.

The prototype shows two or three layouts of one real grade at three widths in `analyze-result.tsx` terms. Brian picks one. The spec needs the order of the parts, what shows before a tap, and the fold.

## Decision

Brian picked layout A, one column, on 2026-11-05. The view has these parts, in this order, at each width:

1. The verdict: the label "Decision for <team>", the answer as the large headline, and the one "why" sentence. A note on a small sample shows under it when the grade has one.
2. The trade: the swap card as it is now.
3. One card for each side, with the label "<team>", plus " · Your Side" for the side of the manager.
4. The as-of line, last.

Each side card shows these parts before a tap:

1. The player the side gets and the player the side gives. Each has a headshot, the name, the position and NFL team, and the Season rank. The Recent rank follows only when it shows.
2. The 2 or 3 bullets.
3. A box "This week and next" with one Week line for the trade week and one for the next week.

The fold is a closed `details` under the Week lines. Its summary reads "How the grade adds up · <n> rows". It holds the adjuster rows of decision 03, each with its mark. On a tablet and wider, the two players of a side stand next to each other. On a phone, they stack. The sides never stand next to each other.

The prototype code is deleted.
