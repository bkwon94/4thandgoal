# 08: How does the front door look and move on a phone?

Map: `.scratch/front-door/MAP.md`.

**Kind:** prototype

**Blocked by:** 01, 07

**Status:** done

## Question

Build a throwaway prototype of the front door on a phone: the sheet for Your team, the Suggestions, the ask box, an Answer, a Claude answer, and an honest miss. Follow the DESIGN BAR of the map, and search scrolltide first. Design the stream as a first-class part: the data block first, the tool steps such as "Reading week 1…", the text, the "checking" to "checked" mark, and the "Fixing a number…" fade (decision 11). Start from the copy of prototype 07 and its decision. Brian runs it on his iPhone and reacts. The spec needs the layout and each state.

## Decision

Brian, 2026-11-10, after he ran three structures of the Thread on his iPhone with real week 8 data: A "Chat" (newest at the bottom), B "Stack" (newest first, with the ask box on top), and C "Pages" (one Answer per page, with a swipe).

1. The front door takes A, the chat scroll, with the fold of B.
   - The Thread reads top to bottom, newest at the bottom. The ask box stays at the bottom, with one row of Suggestion chips above it. "More" leads the chip row.
   - When a new question lands, each older Answer folds to one line: the question plus one fact, such as "Week recap · 99.6, the week median". A tap opens it in place, and a second tap folds it. The newest Answer never folds.
   - An opened fold scrolls to its top, under the header. Its data block shows flat, with a hairline, not as a card inside a card.
   - Reason: the direction is as close to a chat as we can get, and the ask box stays where the thumb is. A follow-up reads under the Answer it follows. The fold fixes the one weak spot of A: two long trade Answers in a row make a long scroll. B puts the ask box out of reach of the thumb. C hides older Answers behind a swipe, and a follow-up lands away from its Answer.
2. Site copy never names Jev, the Advisor, or the Finder. A step line uses plain words, such as "Read both rosters and the race", "Checked the players on each side", and "Weighed 6 offers". Brian, 2026-11-10.
3. The Case of a trade Answer leads with the reason for its Lean. A "Lean no" opens with the reason against, such as "You give up more than you get". The fairness line agrees with the Lean, such as "It helps <team> more".
4. The "checked" mark uses the ink color, not red, so it never reads as an error. Refresh on a stale Answer is a neutral ink button, and a stale Answer hides its "checked" mark.
5. A miss and a cap line hide the Suggestion chips of the dock, so the 3 closest Topics show only once.

Every state of ticket 08 ran in the prototype: the sheet, the empty Thread, More, a league Answer, a personal Answer, "Fixing a number…", the trade check with its steps, trade ideas, a free answer with tool steps, an honest miss, a stale Answer with Refresh, the two cap lines, and Clear. Each ran in light and dark, and the motion followed the DESIGN BAR.

What the prototype also showed:
- Brian read the template trade ideas of the prototype as real and found them bad. The real ones come from `/find` (decision 06). The spec must test the trade ideas Answer with real `/find` output before Brian sees it.
- No control stops a stream. The spec decides if it needs one.
- The prototype set `viewport-fit=cover` and `allowedDevOrigins` only for itself. The spec sets `viewport-fit=cover` for real (decision 07).
- The egg band of the site logs one CORS error from a LAN origin. The prototype did not cause it.

The prototype code is deleted from the repo. A copy for the spec sits in the session scratchpad, outside the repo.
