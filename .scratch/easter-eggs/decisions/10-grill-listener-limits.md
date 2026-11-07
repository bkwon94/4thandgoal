# 10: The limits of the listener and the API

Map: `.scratch/easter-eggs/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The API refuses every call without the analyzer passphrase, except `/health`. Many visitors never open the analyzer, so they have no passphrase in the browser. Decide if the egg check uses an open route, guarded by a limit on calls, or asks for the passphrase at the first multi-tap. The passphrase also keeps the game CPC only. Decide how many calls one browser may make in an hour, and how fast a multi-tap must be. Decide how the listener leaves a normal tap alone: toggles, links, the iOS long-press callout, and the sim timer that unmounts a target. See `01-grill-egg-catalog.notes.md`.

## Decision

Brian decided in the grill of 2026-11-06.

The passphrase:

- The egg check is an open route, outside the passphrase guard. An outsider can find a spot but cannot claim it.
- The claim needs the passphrase. The claim form shows a passphrase field only when the browser has none yet. The analyzer and the claim form keep the passphrase in the browser, so each manager types it once per browser at most.
- The reason: every manager knows the passphrase, so a box before the check stops no manager who uses an AI. A box on the first multi-tap anywhere would also break a normal double-tap or long press.

The limit:

- Egg checks get their own limit of 60 per hour for each address, apart from the limit of 10 per minute of the other routes. A real hunter makes about 80 checks in a long session, and a sweep needs thousands.
- At the limit, a tap shows "The eggs need a rest. Try again in N minutes." A silent block would make a real spot look empty.

The listener:

1. A multi-tap counts when each tap lands within 400 ms of the one before, on the same element.
2. The listener never blocks what a tap already does. An egg target is never a link or a toggle. A chip or a "Show all" is only a condition.
3. The iOS callout turns off on every kind of target in the catalog, never on a link or an image. Text selection stays on, for the selected-word action.
4. The listener counts taps by the stable id of the element, not by the node, so a frame change of the sim does not reset the count.
5. Each check sends the page, the element id, the action, and the state of the conditions: the theme, the open states, the sim outcome, the trade key, and the scroll. The API matches all of them.

## Revised 2026-11-07 by Brian

Brian tested the hunt by hand on Android Chrome and in the phone mode of Chrome DevTools. The text above stays as the first decision.

- A long press of a touch fires `contextmenu`, then `pointercancel`, so the hold never sent. On a touch press of an egg target, the listener now calls `preventDefault` on `contextmenu`, and the hold sends.
- The block holds only for a touch press, with `pointerType` `touch`. A mouse right-click keeps its menu. A link and an image keep their menu.
- A blurb keeps its menu too, because Android Chrome starts the selection of a word from that long press. The selected word stays an action.
- The rule of item 2 holds: the listener never calls `preventDefault` on a tap. A tap fires no `contextmenu`.
- Item 1 now reads: a double-tap counts when the second tap lands within 400 ms of the first. A burst of 3 or more fast taps sends nothing.
- Item 5 now reads: each check sends the two teams of the analyzer trade, not the trade key.
