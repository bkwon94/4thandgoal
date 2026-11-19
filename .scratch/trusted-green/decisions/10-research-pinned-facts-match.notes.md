# 10 notes: Do pinned inputs give the same facts

Research for decision ticket 10. Checked on 2026-11-18 in a detached worktree of `main` at `6b75d218`, with no secret in the env (`env -i HOME PATH`). The target is week 10 of `cpc` and `norcal`. No Claude call, no TypeSafe call, and no Sleeper week fetch ran. The worktree is removed.

## Answer

1. **Yes, the two runs match byte for byte.** With the three inputs pinned, two `make_bundle` runs give the same `facts.json` for each client. `cmp` shows no difference. The `BuildRecord` of the two runs is the same too.
2. The match holds across processes, a different `PYTHONHASHSEED` (1, 2, 7), and a different `TZ` (`Pacific/Auckland`).
3. Two more inputs feed the facts, and the ticket did not name them. The scratch run pinned both, so the match holds:
   - **The nflverse cache** `data/nfl/cache/nflverse/`. The waiver board reads it through `load_slow_sources`, not through the extract.
   - **Sleeper news** of the game changer, from `fetch_news`. It is a live call on each build.
4. The pinned facts do not match the committed `facts.json` of week 10: 553 values differ for cpc, 504 for norcal. The cause is the nflverse data. The build of record had a degraded extract and did not save it. A facts diff can only start with a week whose build saved all its inputs.
5. The build needs five changes for a CI job. See "Changes the build needs" below.

## Method

The scripts lived in the scratchpad, outside the worktree. Each run is a separate process.

1. **Pin step, once per client.** Run `make_bundle` with `started` and `fetched` from the `build` record of `verify.json`. Wrap the real `fetch_nflverse` and `fetch_news` to keep what they return. Save the extract to `raw/nflverse.json` of the week, whatever its flags. Save the news by player id to a JSON file. This fetch also fills `data/nfl/cache/nflverse/`.
2. **Run step, two times per client.** Run `make_bundle` with `nflverse=None` and the same `started` and `fetched`. With `nflverse=None`, `_nflverse_for_week` returns the saved extract and fetches nothing (`apps/pipeline/src/cornerstone/pipeline.py` lines 267 to 270). The news function reads only the saved file, and it stops the run on a player outside it.
3. **Research.** Copy the `research` list and `experts_missing` of the committed `facts.json` onto the new board. Add `research_facts(p, claims)` to each player, as `research_board` does (`packages/waiver/python/src/waiver/research.py` lines 107 to 115). No Claude call runs.
4. Write each result with `write_bundle` and compare with `cmp`.

The pinned clocks, from `verify.json`:

| Client | `started` | `fetched` |
| --- | --- | --- |
| cpc | `2026-11-17T08:00:10.687660-05:00` | `2026-11-17T08:00:07.313690-05:00` |
| norcal | `2026-11-17T11:03:27.805449-05:00` | `2026-11-17T11:02:33.310718-05:00` |

## Results

| Compare | cpc | norcal |
| --- | --- | --- |
| run 1 against run 2, all pinned | same | same |
| run 1 against run 3, other `TZ` and seed | same | not run |
| run 1 against a run with no nflverse cache | 26 values differ | 22 values differ |
| run 1 against the committed `facts.json` | 553 values differ | 504 values differ |

A run of the run step takes about 4 s per client with a warm cache. The pin step takes 7 to 12 s with the cold nflverse download.

### Run with no nflverse cache

I moved `data/nfl/cache/` away and ran the run step again. The saved extract was still in place. Only the waiver board changed:

- `waiver/buckets/stashes` and `waiver/buckets/sneaky` are empty. Run 1 has 3 stashes and 7 sneaky players for cpc.
- Each `bye` of `best_adds` and `trending` is `None`. Run 1 has a week number.

The cause is `load_slow_sources` in `make_bundle` (`pipeline.py` lines 351 to 352). It reads the schedules, depth charts, id map, injuries, expected points, and weekly player stats from the cache, with no network call (`packages/league/python/src/league/slow_sources.py` lines 81 to 121). The saved extract does not hold these values. Thus a CI job with an empty cache builds a different board than the build of record.

The cache also expires. `is_fresh` gives a file 24 h (`packages/league/python/src/league/nflverse.py` lines 41 and 53 to 55). The next fetch replaces it with newer data. So the cache of the build day is gone a day later.

### Run against the committed facts

The differences are the same kind that ticket 03 found:

| Place | Cause |
| --- | --- |
| `data/drops[]`, the `D.*` facts, `W.drops` | The play by play. The build of record had `nflverse_pbp` set to `false`. Today it is `true`. |
| `AW.lucky`, `AW.unlucky` | The expected points of ffopportunity. The record had `ffopportunity` set to `false`. |
| `M5.dropswing` | The drops again. |
| `waiver/buckets/*` | The newer extract and the newer cache. The board of today has players that the board of record did not have, so they get no research: cpc `12499` and `9511`, norcal `9511`. |
| `sheet/chapters[]/fact_ids` | It follows the facts above. |

The news fact `AW.game_changer.news` is the same today as in the committed file. It can change on any later day, because the endpoint is live.

## Size of each pinned input

| File | Bytes | gzip |
| --- | --- | --- |
| cpc `raw/nflverse.json`, week 10, all sources `true` | 682,864 | 52,188 |
| norcal `raw/nflverse.json`, week 10, all sources `true` | 685,758 | 52,609 |
| cpc news, 1 player | 5,756 | not measured |
| norcal news, 1 player | 5,756 | not measured |
| `data/nfl/cache/nflverse/`, all files | about 38 MB | the large files are `.gz` already |

The cache files, in bytes:

| File | Bytes |
| --- | --- |
| `depth_charts_2026.csv.gz` | 15,625,886 |
| `play_by_play_2026.csv.gz` | 10,547,366 |
| `ftn_charting_2026.csv` | 4,367,505 |
| `ep_weekly_2026.csv` | 2,844,797 |
| `db_playerids.csv` | 2,642,951 |
| `games.csv` | 2,190,569 |
| `snap_counts_2026.csv` | 1,258,135 |
| `stats_player_week_2026.csv.gz` | 677,455 |
| `injuries_2026.csv.gz` | 68,394 |

The slow sources read six of these: `games.csv`, `depth_charts_2026.csv.gz`, `db_playerids.csv`, `injuries_2026.csv.gz`, `ep_weekly_2026.csv`, and `stats_player_week_2026.csv.gz`. That is about 24 MB. The play by play, the FTN file, and the snap counts go only into the extract.

The committed `facts.json` is 497,946 bytes for cpc and 414,665 bytes for norcal.

## Changes the build needs

Each change pins one input in a real CI job. The CI job then runs `make_bundle` with the saved inputs and diffs the result with the committed `facts.json`.

1. **The build clock.** Add a CLI option, such as `--started`, or read `build.started` and `build.fetched` of the saved `verify.json` in a facts-only command. `run_build` already takes `started` (`pipeline.py` line 415), and it already reads `fetched` from `verify.json` (lines 432 and 446). The CLI passes no `started` (`apps/pipeline/src/cornerstone/cli.py` line 383).
2. **The nflverse extract.** Save the extract on each build, also a degraded one, and commit `raw/nflverse.json` with the week. Now `_nflverse_for_week` saves only a complete extract (`pipeline.py` lines 283 to 288), so a degraded week has no file. That guard exists so the next build tries the sources again. A pinned build must keep the extract of record, so the retry must not replace the committed file. The `publish` stage already covers `clients/<slug>/data/<season>/`, so it commits the file with no change to its paths. A week adds about 0.7 MB of JSON per client.
3. **The slow sources of the waiver board.** Save the values that `load_slow_sources` gives into the week folder, as a small file like the extract. The other way is to commit the six cache files of the build day, about 24 MB per week. The cache is in `.gitignore` and expires after 24 h, so neither is in git now.
4. **The research lists.** Add a path that reuses the saved research of `facts.json` and makes no Claude call. For example, a `SearchCall` that returns the saved claims of each player, given to `research_board`. A player that is not in the saved board gets no claim. The diff then shows that player as a change of the board, which is a real change.
5. **Sleeper news.** Save the news that `fetch_news` returns into `raw/` of the week, and read it back on a rebuild. It is one player per client, about 6 KB. With no saved news, a CI job calls the live endpoint, and the `AW.game_changer.news` fact can differ.

With these five, a CI job needs no secret and no network. The run step took about 4 s per client here.

A facts diff of week 10 cannot pass with the files in git today. The extract and the cache of the build day are lost. The first week that can pass is the first week built after changes 2, 3, and 5.
