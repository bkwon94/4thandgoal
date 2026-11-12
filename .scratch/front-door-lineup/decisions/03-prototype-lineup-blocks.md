# 03: What do the blocks of Start or sit look like?

Map: `.scratch/front-door-lineup/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

Start or sit needs three blocks: the lineup block (slot, starter, projection, a Swap mark, a "Q" tag, the pivot), the two-player comparison block, and the NFL game card (the two teams, the expected margin, the defense rank against the position, the pass or run tilt). The spec needs the look, the fields, and the motion of each on a phone and on a desktop, in light and dark.

Build each one with real week 10 data of both leagues. Search scrolltide first. Use `transitions-dev`, `apple-design`, `animate`, `critique`, `polish`, and `frontend-design` or the claude.ai Design artifact as needed. Give the prototype its own port, not 3000 or 8090.

## Decision

Brian chose variant A, Ledger, on 2026-11-11, on his iPhone, with two parts of variant C. He turned down variant B.

1. The lineup block lists the slots in Sleeper order. Each row shows the slot, the player, the team, the opponent, the kickoff, and the projection in league points.
2. A row with a Swap or a Q opens taller in place. Its reason or its Pivot comes into focus from a blur. The first such row opens on arrival, and the other rows do not move.
3. A Swap row reads "Swap over K. Vidal", with the benched name struck through. A Q row shows the body part and the practice level, and the Pivot line under a red rule.
4. OUT, IR, and bye players sit in one line under the rows: "Can't play: J. Jacobs Out (finger)".
5. The header of the lineup block holds a small toggle from C: "By projection" and "With 1 Swap". It shows what the Swaps change in the total, and the digits roll on the change.
6. The comparison block puts the two players head to head. One pair of bars for each fact grows from a center line. The side that wins a fact is red, and a dot marks each deciding fact. The pick closes the block: "Start J. Downs."
7. The NFL game card takes the shape of C: a tug bar for the expected margin, a strip of the 32 defenses with the opponent lit, and two pass-share bars against a league mark.
8. The blocks stack at desktop width, because the column of the front door is about 760 px.

Why A: the slot order matches Sleeper, so a manager reads the lineup in one pass. The bars of the comparison show why the pick beats a higher projection. B split the lineup into to-do cards and tiles, and the pick took more reading. The arc dial of C showed two projections beside the pick but not the reason.

The prototype found two facts for the spec:

- Sleeper has `practice_participation` null for every player on Wednesday, before the first practice report. The Q tag says "No practice report yet" until the report lands.
- The expected margin comes from the Sleeper DEF projections, as the gap of the projected points, not from a betting line.

The prototype code is deleted.
