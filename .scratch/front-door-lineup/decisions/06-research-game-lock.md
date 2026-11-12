# 06: How does the API know that a game has started?

Map: `.scratch/front-door-lineup/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The game lock is a hard rule: a player whose NFL game has started cannot move. The spec needs the source of that fact. Find out:

1. Whether the live Sleeper stats of the week show a player once his game starts, and how soon.
2. Whether a Sleeper source, or another free source, gives the kickoff time of each NFL game.
3. When Sleeper sets the final Inactive status before a kickoff.

Write the findings at `decisions/06-research-game-lock.notes.md`.

## Decision

The research decided it on 2026-11-11. The notes are `decisions/06-research-game-lock.notes.md`.

1. The source of the lock is the Sleeper GraphQL `scores` query at `https://sleeper.com/graphql`. It needs no key. `start_time` is the kickoff in epoch ms, UTC. `metadata.has_started` is a live flag. Its `game_id` and team codes match the stats and the projections that the API reads.
2. The rule: a game is locked when `now >= start_time` or when `has_started` is true. The API fetches the times fresh for each Answer, because a moved kickoff changes `start_time`.
3. The fallback is the ESPN scoreboard JSON, with a map of team codes, such as `WSH` to `WAS`. The live stats are a second signal only, because they lag the kickoff by 0.4 to 4.9 minutes.
4. No source sets the final inactive status in time. `injury_status` never holds `Inactive`, and healthy scratches get no flag. So the Pivot line stays the plan for a Questionable starter, and the lock does not read this field.

Risk: neither Sleeper path has docs, so Sleeper can change or block it. The live values of a game in progress are not seen yet. The first chance is NYG at WAS at 2026-11-13T01:15Z.
