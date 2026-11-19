# 02: The Trade Wire route

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-13, AT-14, AT-15, AT-16, and AT-17.

**App:** api

**What to build:** A new read route of the API, for one client, lists the accepted trades of the current week of the Lock (week 11 for CPC), newest first by the time Sleeper accepted them. It reads Sleeper with a query string, so the Sleeper CDN cache does not delay it, and keeps its answer for 5 s. Each trade has its time, and for each team the roster id, the team name, the avatar, the players it gets with their positions, and the FAAB it gets. It has no draft picks. A pending or vetoed trade is not in the list. The trade parser of the league package keeps the FAAB, and the route reads which team got a player from the `adds` of the transaction, never from the cached rosters. The route checks the passphrase through the read guard and does not count against the limit of 30 requests per minute per IP.

**Blocked by:** none

**Status:** in-review

- [x] A route test with a recorded Sleeper answer shows trade W of week 9 with both teams, the players, the positions, and $5 of FAAB to roster 8.
- [x] A route test shows only `complete` trades of the leg, newest first.
- [x] Two calls within 5 s make one Sleeper read, and a call after 5 s makes a second.
- [x] A call with no passphrase answers 401, and 40 calls from one IP in 60 s all answer 200.
