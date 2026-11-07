# packages/eggs/site/listener: the listener of the egg hunt

## Knows

- The multi-tap: 2 or more taps on one element with a stable id, each within 400 ms of the one before. It sends `tap2` to `tap5` and more when the taps stop.
- The long press: it sends `hold1`, `hold3`, or `hold5` on release, with the hold rounded down. A press under 1 second is a tap, and a cancel sends nothing.
- The tap combo: tap A, tap B, then a double-tap on C within 5 seconds. The check of the double-tap carries `trail`, the stable ids of A and B.
- The selected word: one whole word in an element with a stable id, as `select` with `word` in lower case, once the selection settles for 600 ms.
- The count by stable id and not by node, so a frame of the sim replay keeps the count.
- The conditions of each check: `theme`, `open`, the sorted open ids, `sim_champion` and `sim_seeds` from the root of the sim replay, `trade` and `trade_answer` from the root of the analyzer result, `scrolled_end` after a scroll to the end of the page, and `not_found` on the 404 page. A condition with no state on the page stays out of the body.

## Ports

- `send` and `page` of `ListenerPorts`. The hunt gives them.

## Does not do

- It never blocks a tap, so a link, a toggle, or a chip still works.
- It reads no clock window. The API checks the clock window and the weekday on the clock of the client.
- It sends no check for a single tap, and it knows no egg.
