# A given player names its destination roster

A trade on the analyze route is a list of two to four sides, and each side lists the players it gives. With two sides the destination of a given player is implied: the other side. With three or more sides it is not, so every given player carries a `to` roster id, in a two-side trade too. We chose one shape over an optional `to` because one shape is one check on the API and one render on the site. A side's `gets` is derived from the other sides' `to` fields, never sent.

## Consequences

- The response mirrors it: each player in `gives` carries `to`, and each player in `gets` carries `from`, so the swap card can tag a player with three sides on the page.
- The finder stays a two-side tool. It sends `to` like any caller and hides once a trade has a third side.
- The ready rule reads the destinations: every side gives at least one player and gets at least one player.
