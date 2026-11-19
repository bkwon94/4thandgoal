# 03: The line of each Stop and the replay link on desktop

Map: `.scratch/front-door-tour/MAP.md`.

**Kind:** grill

**Blocked by:** 02

**Status:** done

## Question

The spec needs the final header and the final line of each of the four Stops: the Suggestions, the ask box, the team switch, and the menu. The copy follows the site rules: "manager", never "rival", and no internal names such as Jev or front door.

The replay link sits in the menu sheet on a phone and a tablet. Desktop has the pill bar and no menu sheet, so the spec needs a spot for the replay link there too. Ticket 02 added the header. Its placeholders are "Suggestions", "Ask box", "Your team", and "Menu". The line may wrap to three lines on desktop.

## Decision

Grill of 2026-11-18 with Brian.

The copy of each Stop:

| Stop | Header | Line |
| --- | --- | --- |
| 1 | Suggestions | Picks for your team right now. Tap one to open it, or tap More for the full list. |
| 2 | Ask | Type any question about your team or your league, such as start or sit, a trade, or the playoff race. |
| 3 | Your team | Tap to see the league as another manager. |
| 4 | Menu | Every page of the league lives here. |

Why:

- Stop 1 says "right now", not "this week". The 14 Topics cover the season and the league too, not only the week.
- Stop 2 says "any question about your team or your league", not "anything". A question out of range gets "I can't answer that."
- Stop 3 adds "Tap" to the prototype line, so a league mate sees that the team name is a button.
- Stop 4 stays generic. It names no page, so a client with another menu needs no new copy.

The replay:

1. On a phone and a tablet, the menu sheet has a "Show the tour" link. It shows only on the front door. The front door passes it into the sheet through a slot, so the shell names no Tour.
2. On desktop, a "?" icon button sits beside the theme button. It shows only on the front door, through the `actions` slot of `TopBand`. Its accessible name is "Show the tour".
3. A tap on either one closes the menu sheet if it is open, then starts the Tour at Stop 1.
4. The pill bar gets no Tour item, because it holds only page links.
5. Stop 4 gives no replay hint.

No new glossary term and no ADR.
