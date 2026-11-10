# 06: Where the past-season splits come from

Map: `.scratch/manager-brain/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The playbook leans on history, such as Henry in the second half and in cold weather. Decision 01 puts past-season splits on the fact sheet so a check can confirm a history claim. Find the source: does the Sleeper API give weekly stats of past seasons, for how many seasons, and at what cost in calls? Find where the pipeline caches slow sources now. Decide which splits the sheet holds: weeks 1 to 8 against weeks 9 to 17, and maybe games in cold weather. Find how to map a player across seasons and teams.

## Decision

Brian approved on 2026-11-09. The notes are in `06-research-history-splits.notes.md`.

1. **Source:** the nflverse weekly player file `stats_player_week_<season>.csv.gz`, which the pipeline already reads for this season. Its gsis ids map to Sleeper ids through `db_playerids.csv`. The Sleeper stats endpoint is not documented, so it is a cross-check only.
2. **Seasons:** the last 3 complete seasons, now 2023 to 2025. A past season never changes, so its file is cached with no max age at `data/nfl/cache/nflverse/stats_player_week_<season>.csv.gz`.
3. **Splits per player and season:** the team, the half-PPR points per game in weeks 1 to 8 and in weeks 9 to 17 with the game counts, and the points per game in cold games with the game count. A cold game is outdoor at 40 F or below, from `temp` and `roof` in `games.csv`.
4. **Small samples:** the sheet always shows the game count, and the Advisor says so when a split rests on few games.
5. **No history:** a player with no past season gets no split. The Advisor may speak of him in words, with no number (decision 01).

The sample shows why the number matters. Chase Brown is stronger in weeks 9 to 17 in all three seasons. Henry is stronger late only in 2025, and he fell late in 2024.
