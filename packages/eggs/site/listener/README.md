# packages/eggs/site/listener: the listener of the egg hunt

## Knows

- The double-tap: exactly 2 taps on one element with a stable id, the second within 400 ms of the first. It sends `tap2` when the taps stop. A burst of 3 or more fast taps sends nothing, so a spam of taps finds no egg.
- The long press: a press of 2 seconds or more sends `hold` on release, with no upper limit. A press under 1 second is a tap. A press of 1 to 2 seconds and a cancel send nothing.
- The menu of a touch hold: Android Chrome fires `contextmenu` during a long press, then `pointercancel`, so the hold would never send. On a touch press of an egg target, the listener calls `preventDefault` on `contextmenu`. A link, an image, a blurb, and a mouse right-click keep the menu. A blurb keeps it because Android Chrome starts the selection of a word from that long press.
- The tap combo: tap A, tap B, then a double-tap on C within 5 seconds. The check of the double-tap carries `trail`, the stable ids of A and B.
- The selected word: one whole word in an element with a stable id, as `select` with `word` in lower case, once the selection settles for 600 ms.
- The count by stable id and not by node, so a frame of the sim replay keeps the count.
- The conditions of each check: `theme`, `open`, the sorted open ids, `sim_champion` and `sim_seeds` from the root of the sim replay, `trade_teams`, the two roster ids of the trade key, and `trade_answer` from the root of the analyzer result, `scrolled_end` after a scroll to the end of the page, and `not_found` on the 404 page. A condition with no state on the page stays out of the body.

## Ports

- `send` and `page` of `ListenerPorts`. The hunt gives them.

## Does not do

- It never blocks a tap, so a link, a toggle, or a chip still works. A tap fires no `contextmenu`, so the block of the menu never touches a tap.
- It reads no clock window. The API checks the clock window and the weekday on the clock of the client.
- It sends no check for a single tap, and it knows no egg.
