# 10: Where does the nav go on the front door?

Map: `.scratch/front-door-lineup/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

The front door is a chat. On a 375 px phone, the bottom stack takes about 220 px of 812: the Suggestions row (48), the ask box (64), the dock (80), and the home indicator (34). The dock also floats with a gap under it, so the page shows through between the ask box, the dock, and the bottom edge (Brian's screenshot, 2026-11-11).

Brian and the orchestrator lean to this: on the front door, the dock leaves, and a button in the header opens the pages. The bottom becomes the Suggestions row and the ask box on one solid surface, flush with the bottom edge. The other pages keep the dock, because they have no ask box. The cost is one more tap to the other pages.

The spec needs the place of the nav on the front door, its open and close motion, and the bottom surface, on a phone and on a desktop, in light and dark. This decision replaces the flush fix of the dock. The passphrase bug of decision 02 stays its own ticket.

Search scrolltide first. Use `transitions-dev`, `transitions-polish`, `apple-design`, `animate`, `emil-design-eng`, `make-interfaces-feel-better`, `critique`, and `polish`. Give the prototype port 3011, not 3000 or 8090.

## Decision

Brian chose on 2026-11-11, after the prototype of four states: `dock` (today), A (header sheet), B (morph pill), and C (thumb sheet). The answer takes the place of A and the list of B.

1. On the front door, the dock leaves. A menu button at the right of the header opens a sheet that drops from under the header. Its icon turns into an X.
2. The sheet is a list of rows, as in B: an icon, the page name, and a short note. The current page has a check. The notes are "Ask about your team", "Scores and recaps", "The league, ranked", "Grades and records", and "Check a trade".
3. The sheet closes by the X, a tap on the dimmed page, Escape, or a swipe up, back the way it came. The focus goes to the sheet on open and back to the button on close.
4. The bottom of the front door is one solid surface, flush with the bottom edge: the Suggestions row and the ask box at full width. Its padding holds the home indicator. It drops that padding while the keyboard is open.
5. On the front door, the week pill leaves the header. The header holds the logo, the theme toggle, and the menu button. The Answers are about the live week, so a pill with the last report week read as a second, wrong week. In the sheet, the week row opens the latest report, and a "Past weeks" control under it opens the list of weeks.
6. The other pages keep the dock and the week pill, because they have no ask box and the week matters there.
7. On a desktop, the menu button hides and the pages show inline in the header, as today.

The measure: the bottom stack drops from 222 px to 145 px at 375 x 812, before the 34 px of the home indicator. The gap under the dock goes away, because nothing floats.

Why not C: its nav button takes 62 px from the ask box, the placeholder had to shrink, and the button reads as an attach button. A manager opens the nav rarely and asks often. Why not B as built: a "Home" pill tells the manager where they already are, it hides the pages on a desktop, and its panel covers the header. The tiles of A took half the screen, so the list of B replaces them.

The passphrase bug of decision 02 stays its own ticket. Its cause: the passphrase field in `miss-card.tsx` does not call `useKeyboardField`, so the foot does not move above the keyboard for it. The fix marks that field and gives the card a scroll margin as tall as the foot.

The prototype code is deleted.
