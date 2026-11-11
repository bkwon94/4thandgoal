# 15: The Waiver targets Answer gives a sane list

Spec: `.scratch/front-door/PRD.md`. Source: row H5 of `.scratch/front-door/HANDS-ON.md`.

**App:** pipeline, api

**What to build:** The waiver list holds weak players with bids that make no sense, such as Drew Sample for 13. A player with no Sleeper projection counts 0 and ties into the top half, and `behind_injury` fires on a backup. Two hard rules go into `packages/waiver/`: a player with a rest of season projection of 0 lands in no add bucket, and `behind_injury` fires only when every player above the candidate is out. The API applies the same projection rule to the published file as it is, puts the `trending` bucket first, and gives Claude no bid. A Jev add judgment and a real price wait for a later waiver spec.

**Blocked by:** None

**Status:** done

- [x] A player with a rest of season projection of 0 lands in no add bucket: `best_adds`, `trending`, `sneaky`, or `stashes`.
- [x] A player behind an out backup with a healthy starter above is not sneaky. A player with every player above him out is sneaky.
- [x] `_waiver_list` of the API drops each player with a rest of season projection of 0 or none, next to the rule that drops a rostered player.
- [x] The `trending` bucket comes first in `waiver_list`, and the prompt of the Topic says to lean on it.
- [x] `waiver_list` holds no `bid`, the block shows no bid, and the prompt says to quote no FAAB bid.
- [x] `schema_version` and the site types of `waiver.json` stay the same. The waiver page shows a bucket of fewer than 8 players.

## Comments
- Closes with the squash merge of the spec PR.
