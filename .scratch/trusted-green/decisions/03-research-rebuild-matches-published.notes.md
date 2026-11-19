# 03 notes: Does a rebuild match the published files

Research for decision ticket 03. Checked on 2026-11-18 in a detached worktree of `main` at `6b75d218`, with no secret in the env (`env -i HOME PATH`). The target is week 10 of `cpc` and `norcal`, the latest published week of each client. No build fetched from Sleeper. The worktree is removed.

## Answer

1. A full `build --no-fetch` does not match, and it cannot run in CI with no key. It stops at the first Claude call with an auth error. With a key, the Claude text, the web research, the live nflverse data, and the live Sleeper news all differ from the build of record.
2. `page-json` matches byte for byte. It re-renders the saved `facts.json` and `blurbs.json`. For week 10 of both clients, `page.json`, `topics.json`, and `waiver.json` are identical to `published/`. It needs no secret and no network, and it takes about 2 s.
3. A `--no-fetch` build needs `ANTHROPIC_API_KEY` and `TYPESAFE_API_KEY`. It also calls Sleeper news, the Sleeper CDN, GitHub nflverse, and the dynastyprocess data file.
4. One full cpc build takes about 12.5 min, and Claude calls take most of it. A 2-core runner is about the same, so it is over the 5 min limit. A `page-json` rebuild is about 2 s per client.
5. The saved raw Sleeper data is in git for each week. The nflverse data is not: `data/nfl/cache/` is in `.gitignore`, and week 10 has no `raw/nflverse.json`.

## 1. Match or not

### Full build with `--no-fetch`

Run: `cornerstone build --client cpc --season 2026 --week 10 --no-fetch`, exit 1 after 15.4 s. The traceback ends in `waiver/research.py` `search_call`, the first Claude call:

```
TypeError: "Could not resolve authentication method. Expected one of api_key, auth_token, or credentials to be set. ..."
```

The build stops before `write_bundle`, so it writes no `facts.json`, `page.json`, or image. It did write one new file, `clients/cpc/data/2026/week-10/raw/nflverse.json`, which git does not track. I stopped there, as the ticket says. I did not run norcal the same way, because the code path is the same.

With a key, these parts of `run_build` (`apps/pipeline/src/cornerstone/pipeline.py` lines 404 to 475) cannot match the build of record:

- **Text that Claude writes.** `write_and_verify` writes each chapter with Claude. The week 10 cpc build made 55 calls to `api.anthropic.com` (`~/Library/Logs/cornerstone-weekly/build.log`, run of 2026-11-17 08:00). Each call gives new text, so `blurbs.json` and `page.json` differ.
- **Web research.** `research_board` calls Claude with `WEB_SEARCH_TOOL` (`packages/waiver/python/src/waiver/research.py` line 39). The claims of each waiver player differ, so `waiver.json` differs.
- **The live nflverse data.** `make_bundle` gets the nflverse files over the network each run. The build of record had `nflverse_pbp`, `nflverse_ftn`, and `ffopportunity` set to `false` in `verify.json`. A rebuild today gets all eight sources as `true`. The cache and the per-week `nflverse.json` are not in git, so CI cannot read the data of the build day.
- **The build clock.** `started = started or datetime.now(client.tz)` (`pipeline.py` line 336). It sets `today` of the bundle and the clock of the waiver board. The CLI passes no `started`, so each rebuild uses the time of the run.
- **Sleeper news.** `fetch_news` calls `api.sleeper.app/players/nfl/<id>/news` live. The news of a player changes each day.

`page.json` itself holds no time stamp field. I found no `*_at`, `started`, or `generated` key in the published week 10 file.

### The deterministic part of the facts

To see how much differs before Claude runs, I ran `make_bundle` from a script in the scratchpad. It used the saved build start from `verify.json` and the real `fetch_nflverse`. Then I compared the result with the committed `facts.json`. The script skips only the research call. The result:

| Client | Values that differ | Main places |
| --- | --- | --- |
| cpc | 553 | `waiver/buckets/*` (players, scores, prices), `sheet/chapters[]/fact_ids`, `data/drops[]` |
| norcal | 504 | the same places |

The research lists are empty in the script, so each `research` list differs too. The other differences come from the newer nflverse data. Thus even the facts do not match when the data comes from the network today.

### `page-json`, the re-render of the saved week

`cornerstone page-json --client <slug> --season 2026 --week 10` reads the saved facts and blurbs. Its docstring says "It calls no writer and no network" (`pipeline.py` line 723). It writes `page.json`, `waiver.json`, and `topics.json` into `clients/<slug>/build/<season>/week-NN/`. It writes no images.

Results with `cmp` against `published/2026/week-10/`:

| Client | `page.json` | `topics.json` | `waiver.json` |
| --- | --- | --- | --- |
| cpc | same | same | same |
| norcal | same | same | same |

`git status` was clean after the run, so the re-render also equals the committed `build/` files. `diff -rq` of the whole `build/2026/week-10/` tree against `published/2026/week-10/` shows no difference, images included. The season files `rankings.json`, `managers.json`, `midseason.json`, and `sim.json` in `build/2026/` equal those in `published/2026/`.

### Older weeks drift

A `page-json` of older weeks does not match. This shows that only the latest week is a safe target:

| Week | cpc `page.json` | norcal `page.json` |
| --- | --- | --- |
| 06 | differs | `page-json` fails, no saved data |
| 07 | differs | `page-json` fails, no saved data |
| 08 | differs | differs |
| 09 | same | same |

The week 6 diff is a schema change: the published file has `is_brian`, and the code now writes no such key. Each `topics.json` of weeks 8 and 9 also differs, or is absent from `build/`. The cause is that the code changed after the publish of those weeks. A later code change can make week 10 drift the same way. A diff against the latest week catches that drift, which is the point of the check.

## 2. Secrets and network calls of a `--no-fetch` build

From the run here and from the week 10 log (`build.log`, lines 843 to 1072):

| Need | Where | Fails how with no secret |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | `ClaudeWriter` makes `anthropic.Anthropic()` on its first call (`packages/facts/python/src/facts/writer.py` line 200) | `TypeError: Could not resolve authentication method`, exit 1, at the research call |
| `TYPESAFE_API_KEY` | `TypeSafeJev` makes `TypeSafeClient` on its first call (`packages/league/python/src/league/jev.py`). The week 10 log has 28 calls to `api.typesafe.ai`. | Not reached here. The docstring says "A missing key raises here, on the first call." It raises `JevError`. |
| Sleeper news, no key | `api.sleeper.app/players/nfl/<id>/news` | Not a secret. It is a live call to Sleeper. It is not a refetch of the week. |
| Sleeper CDN, no key | `sleepercdn.com`, the avatars and headshots that `render_week` downloads. The log has 29 calls. | Not reached here. |
| nflverse, no key | `github.com/nflverse/nflverse-data` releases, `ffverse/ffopportunity`, `dynastyprocess/data` | It works with no key. The data is newer than the build of record. |

A `--no-fetch` build makes no call to the Sleeper league API (`/v1/league/...`). `load_client` reads the saved `clients/<slug>/data/<season>/league.json`, and `resolve_week` calls no state when `--season` and `--week` are set (`pipeline.py` line 157).

`page-json` needs none of these. Both runs here used the empty env and passed.

## 3. Time

| Run | Local wall time | Notes |
| --- | --- | --- |
| Full cpc build, week 10, with fetch, by the launch agent | 12 min 33 s | `build.log`: start 08:00:04, end 08:12:37 on 2026-11-17. The 2026-11-10 run took 12 min 18 s. |
| `--no-fetch` cpc build, up to the first Claude call | 15.4 s (9.1 s user) | It includes the cold nflverse download, 38 MB into `data/nfl/cache/`. |
| `make_bundle` only, warm cache | about 8.5 s per client | The deterministic part of the build. |
| `page-json`, per client | 1.4 to 2.2 s | No network. |

The memory note `week-8-fixes.md` gives the same scale: "a real build per pass, about 18 minutes and 30 Claude calls".

Estimate for a 2-core GitHub runner:

- A full build is bound by about 55 Claude calls and 28 TypeSafe calls, not by the CPU. Thus it takes about 12 to 15 min per client, plus about 1 min for `uv sync` and the nflverse download. That is over the 5 min limit of the ticket, so the job would run one client only. It would also cost the Claude calls of a full build on each run.
- A `page-json` rebuild has about 1 s of CPU per client. On a 2-core runner, I estimate under 10 s for both clients, plus the `uv sync`.

## 4. Is the saved raw data in git

- **Yes for Sleeper.** `git ls-files clients/cpc/data/2026/week-10` lists the `raw/` files: `bracket`, `fetched`, `league`, `matchups`, `matchups_next`, `players`, `projections`, `projections_ahead`, `rosters`, `schedule`, `state`, `stats`, `transactions`, `transactions_prev`, `trending`, and `users`. It also lists `facts.json`, `blurbs.json`, and `verify.json`. Norcal week 10 has the same set.
- **Yes for the inputs of `page-json`.** `facts.json` and `blurbs.json` are committed for each week that `page-json` re-renders. `history/` and `league.json` of the season are committed too.
- **No for nflverse.** `.gitignore` has `data/nfl/cache/`. Only cpc week 6 has a committed `raw/nflverse.json`. The full build fetches nflverse again in CI, so its facts differ from the build of record.

## What this means for the job

A byte-for-byte diff works only for the render step. The CI job can run `page-json` for the latest published week of both clients, then diff `build/<season>/week-NN/` against `published/<season>/week-NN/`. That needs no secret, no network, and about 10 s. It catches each code change to the render, to the topics, or to the waiver file. It does not catch a change to the facts engine, because it reads the saved `facts.json`.

A check of the facts engine needs a saved nflverse input of the week and a fixed build clock. The code has the seam (`started` and `nflverse` of `make_bundle`), but the CLI does not pass them, and the nflverse data of the week is not in git. A full build with Claude can never match byte for byte.
