# packages/eggs/site/listener: the listener of the egg hunt

## Knows

- The multi-tap: 2 or more taps on one element with a stable id, each within 400 ms of the one before.
- The check that it sends when the taps stop: the page, the stable id, the action, such as `tap3`, and the theme.

## Ports

- `send` and `page` of `ListenerPorts`. The hunt gives them.

## Does not do

- It never blocks a tap, so a link, a toggle, or a chip still works.
- It sends no check for a single tap, and it knows no egg.
