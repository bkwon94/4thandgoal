# 15: How do the list rows, the tags, and the controls of the report look?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** prototype

**Blocked by:** 14

**Status:** done

## Question

Brian found these parts cluttered and ugly: the "Grab him now" list, the position switch, the steals and busts, the trade rows, and the record book. Big red pill tags, such as "FREE AGENT", "JUST BAD", "HURT ON ARRIVAL", and the award pills, take over each row. The very round shape of the position switch, the "Show all" button, and the cards looks weird. Screenshots: `~/screenshots/midseason-feedback/02` to `06`.

This ticket decides the shape of a row, the look and the place of a tag, the corner radius, and the look of the position switch and the "Show all" control. The site-redesign PRD sets the radii of the shared look. This ticket says if the report keeps them, and where the report differs. Brian must see boards with the real data before the choice.

## Decision

Brian decided it on 2026-11-06, after three phone boards with the real CPC week 8 data in the row "Ticket 15 · rows and tags" of the Design canvas: R1 Quiet text, R2 Data rail, and R3 Editorial. Each board showed Grab him now, the Position top 10 with its switch, the steals and busts, the trade rows, and the record book. He chose R1 Quiet text, with the awards as lines from R3.

- **A tag has no box and no fill.** A fact that describes the player goes in the second line, such as "Free agent · QB · MIN". Any other tag is a small mono caps word in a muted color. "Just bad" and "hurt on arrival" use the accent color.
- **Cards have 8 px corners.** No full pill in the report.
- **The position switch is plain text segments,** with a 2 px accent underline that slides to the chosen position.
- **"Show all" is a mono text control with a chevron,** with no border, at the foot of the card. It changes to "Show top 5", and the chevron turns.
- **The awards are lines, not cards:** "MVP — Jahmyr Gibbs, Maye d'force B with U — 135.1 points over the line in his starts."
- **Decimal places:** player points show 1 decimal place, such as 77.8. Team scores show 2, such as 158.96, as Sleeper does.

Not chosen: R2, because its blue and amber rails add colors outside the one accent of the shared look and need a legend. R3 chips, because a row with three chips still looks cluttered.

Brian also cut two parts of the report in this session:

- **"The one that got away" goes,** in the draft and in the waiver hits. This removes PRD story 26 and AT-14, and changes decision 02, decision 03, and ticket 07.
- **The Players to watch chapter goes:** Due to rise, Due to fall, and Grab him now. Brian: Grab him now must be good, and it recommended only bench quarterbacks. This removes PRD story 39 and AT-23, and changes decision 10 and ticket 06. Act III holds the look ahead and the sim.

## Later change

- 2026-11-06, Brian: the awards are cards with a headshot or an avatar, not lines.
