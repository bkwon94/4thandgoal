# 07: How does the Index list sit at 390px?

Map: `.scratch/card-polish/MAP.md`.

**Kind:** prototype

**Blocked by:** 05, 06

**Status:** done

## Question

The Scrolltide layout puts the list beside the picture, which does not fit at 390px. On a phone, a tap must replace the hover. The prototype also chooses what fills the large picture, because no avatar is sharp at that size (decision 05). The first try is a panel in the hero look: the grid, the brand glow, and the stats of the chosen team, with the avatar small inside it. Brian must see the phone layout and the desktop layout before the spec fixes it.

## Decision

Brian chose on his phone on 2026-11-07, after a prototype on the live Managers index. All three variants followed the Scrolltide Team Roster method: the ledger list, the letter roll on the active name, and the All, In, Bubble, Out chips.

1. Phone and tablet take C, the ledger only. Each row is the place, the team name, and the playoff odds. A tap opens the row in place with the Open card drawer: the `grid-template-rows` height, the 6px blur-in, and the spring. The open row holds the avatar, the facts, the grade letter, the grade read, the four arcs of the Grade dial, and a link to the manager page. One row is open at a time. All 12 teams fit on one 390px screen closed.
2. Desktop takes A, the ledger and stage. The ledger sits beside one sticky panel, which is the hero of the page: dark, the grid texture, the corner brackets, and the brand glow, with every text line on a plate. A hover or a focus on a row swaps the panel, with the wipe and the 1.22 zoom of the item. The spec sets the tier where the stage starts. The desktop tier of 64rem is the first try.
3. Brian found C "a bit boring but ok". The first try to lift it, for the spec: a small avatar before the name, the grade letter at the end of the row, and a color on the race word. The row stays one line.

Why not B: a plain stage lost the effect that makes the stage worth its space. Why not A on a phone: the sticky panel took about 60% of the screen and left about 3 rows of the ledger in view.

This changes decision 03, point 2. The Index list replaces the cards, so the four arcs live in the open row and in the stage, not on a card.

The stage uses the hero surface, and the `hero-slots` spec owns the hero. The spec must check the stage against the slots of `hero-slots`, or keep the stage as its own surface with the same look. The names of rows not in focus are a muted color, so the spec must check their contrast with axe. The playoff odds and the status word come from `manager.odds`, which the loader joins from the last week of `rankings.json`. The status word is in the data but not in the `JoinedOdds` type.

The prototype code is deleted. It was never committed.
