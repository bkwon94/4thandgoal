# History, Trades, and Drops Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a season history layer from weeks 1 to 5, a Trades chapter with a grade per side, and drop and injury facts from nflverse, then rebuild week 6 with all three.

**Architecture:** A new `cornerstone history` command caches past Sleeper weeks under `data/{season}/history/`. The build reads that cache, the week's raw files, and a per-week nflverse extract saved as `raw/nflverse.json`, and it computes every new fact in code. The new facts follow the version 1 citation rules: `Nums`, `_fact(...)`, fact IDs, the code check, the verifier, and the template fallback. Each new source degrades: a missing source removes its facts and never stops the build.

**Tech Stack:** Python 3.11, `uv`, Pydantic, Jinja2, `httpx`, the Anthropic SDK, `pytest`. The standard library `csv` and `gzip` read the nflverse files. No pandas.

**Spec:** `design/specs/2026-10-20-history-trades-drops-design.md`. It builds on `design/specs/2026-10-20-cornerstone-weekly-design.md`. Read both.

## Global Constraints

- Read the scoring rates from `league.json` `scoring_settings`: `rec` 0.5, `rec_yd` 0.1, `rec_td` 6. Never hard-code them.
- Build every new fact with `_fact(fid, text, n, teams, players)` in `sheet.py`. Put every number in the text through `n(...)`, `n.ord(...)`, `n.record(...)`, or `n.text(...)`. The existing tests `test_every_number_appears_in_its_text` and `test_every_number_token_in_text_is_in_numbers` must pass on a bundle with history, trades, and nflverse.
- Give each new stat term one line in `prompts/vocabulary.md`, with the text this plan quotes.
- Read nflverse and ffverse files with `csv` and `gzip`. No pandas, no new dependency.
- A failure of nflverse, ffverse, or a past Sleeper week never stops a build. Log a warning for each degrade. Record the sources in `verify.json`.
- No chapter gains more than 6 fact IDs that start with `H.` or `P.`.
- A missing history week removes every `H.` and `P.` fact. It never makes one wrong.
- Every chapter holds at 390px with no horizontal scroll.
- No mock mode in product code. Tests use the recorded data under `tests/fixtures/` and inject callables, as version 1 does with `call`, `news`, and `fetch_bytes`.
- Mark a test that calls a real external API `@pytest.mark.live`.
- Cut-off times use `ZoneInfo("America/New_York")`. The Tuesday job runs at 08:00 in that zone.
- Every new code file starts with a two-line docstring.
- Prose, comments, docstrings, and commit messages follow Simplified Technical English. Prompt files and blurbs are exempt.
- Commit at the end of every task. Write the subject as one plain imperative sentence, as in `git log`: "Drop the standings highlight of Brian's team". End the message with the session's `Co-Authored-By` trailer. Never use `--no-verify`.
- Nothing publishes without `cornerstone publish`. No task in this plan runs it. Brian runs it.

## Review Focus

1. A stale nflverse cache, or a file that has no rows for the week yet, must degrade to the Sleeper `rec_drop` count. It must never give zero drops. Tests in Task 13 and Task 14.
2. A drop behind the line of scrimmage must count its air yards as 0. Kyren Williams, play 3519 of `2026_06_ARI_LA`, has `air_yards` -6. An `air_yards` of `NA` also counts as 0. Test in Task 14.
3. A rebuild of a week must keep the first recorded fetch time, so a trade never moves to another week or shows twice. Test in Task 8.
4. A three-team trade must not crash the trade facts. Week 5 has one, rosters 7, 8, and 12. Test in Task 9.
5. A Sleeper `gsis_id` with a leading space must still join. Terry McLaurin's blob value is `" 00-0035659"`. Test in Task 13.

## File Structure

| File | Change | Responsibility |
| --- | --- | --- |
| `src/cornerstone/history.py` | Create | Paths, fetch, load, and save of the history cache |
| `src/cornerstone/trades.py` | Create | The trade window, the late-trade test, and the fetch-time cut-off |
| `src/cornerstone/nflverse.py` | Create | Download with a one-day cache, parse of the three nflverse files and the ffverse id map |
| `src/cornerstone/facts_nflverse.py` | Create | Drop lines, drop value, and injury history from the nflverse extract |
| `src/cornerstone/models.py` | Modify | `PastWeek`, `History`, `Trade`, `DraftPick`, `BuildRecord`, `VerifyFile`, `DropPlay`, `NflverseWeek`, `DropLine`, `Grade`, `TradesWriterOut`; new fields on `SeasonHistory`, `Week`, `WeekData`, `Chapter`, `Blurb`, `Award` |
| `src/cornerstone/sleeper.py` | Modify | `fetch_past_week` |
| `src/cornerstone/parse.py` | Modify | `parse_past_week`, `parse_moves`, `parse_trades`; `Week.roster_slots`, `Week.scoring`, `Week.stats` |
| `src/cornerstone/facts_league.py` | Modify | Standings, ranks before, schedule strength, and season history from the history; Butterfingers |
| `src/cornerstone/sheet.py` | Modify | The `H.`, `P.`, `T`, `D.`, `I.`, `W.drops`, and `dropswing` facts; the `trades` chapter; the cap |
| `src/cornerstone/writer.py`, `verifier.py` | Modify | Grades; the code check for grades; the gates for `.dropswing` and the trade swing |
| `src/cornerstone/pipeline.py`, `cli.py` | Modify | `make_bundle`, `run_history`, the build record, the history save, the `history` command |
| `src/cornerstone/render.py`, `templates/week.html`, `static/style.css` | Modify | Trades cards, the Butterfingers tile, the drop note |
| `src/cornerstone/prompts/vocabulary.md`, `writer.md`, `verifier.md` | Modify | New terms and rules |
| `tests/fixtures/2026/history/week-0{1..5}/` | Create | Trimmed history weeks |
| `tests/fixtures/nflverse/` | Create | Trimmed nflverse and ffverse files |
| `tests/test_history.py`, `test_trades.py`, `test_nflverse.py`, `test_facts_nflverse.py` | Create | Tests for the new modules |

---

## Part 1: the history layer

### Task 1: Fetch and cache past weeks

**Files:**
- Create: `src/cornerstone/history.py`, `tests/test_history.py`, `tests/fixtures/2026/history/week-0{1..5}/*.json`
- Modify: `src/cornerstone/sleeper.py`, `src/cornerstone/pipeline.py`, `src/cornerstone/cli.py`, `tests/conftest.py`, `tests/test_cli.py`
- Data: `data/2026/history/week-0{1..5}/*.json`

**Interfaces:**
- Produces:
  - `HISTORY_FILES: tuple[str, ...] = ("matchups", "transactions", "stats", "projections")` in `history.py`.
  - `fetch_past_week(league_id: str, season: int, week: int, out_dir: Path) -> None` in `sleeper.py`. It writes one JSON file per name in `HISTORY_FILES`. Stats and projections use `_get_or_empty`, as `fetch_week` does.
  - `history_root(repo: Path, season: int) -> Path` returns `repo/data/{season}/history`.
  - `history_dir(root: Path, week: int) -> Path` returns `root/week-{NN}`.
  - `fetch_history(league_id: str, season: int, through: int, root: Path, force: bool = False, fetch: Callable[[str, int, int, Path], None] = fetch_past_week) -> list[int]` returns the weeks it fetched. It skips a week whose directory holds all four files, unless `force`.
  - `run_history(repo: Path, season: int, through: int, force: bool = False) -> list[int]` in `pipeline.py`.
  - CLI: `cornerstone history [--season INT] --through INT [--force]`. It prints `Fetched weeks: 1, 2, 3, 4, 5` or `Nothing to fetch`. Handle `history` before `resolve_week`, because it has no `--week`.
  - Fixture `fixture_history_root() -> Path` in `conftest.py` returns `tests/fixtures/2026/history`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_history.py
def test_fetch_history_skips_weeks_on_disk(tmp_path):
    root = tmp_path / "history"
    done = history_dir(root, 1)
    done.mkdir(parents=True)
    for name in HISTORY_FILES:
        (done / f"{name}.json").write_text("[]")
    seen = []
    fetched = fetch_history("L", 2026, 2, root, fetch=lambda lid, s, w, d: seen.append(w))
    assert fetched == [2] and seen == [2]

def test_fetch_history_force_refetches(tmp_path):
    # Same setup as above, with force=True.
    assert fetched == [1, 2]

@pytest.mark.live
def test_fetch_past_week_writes_four_files(tmp_path):
    fetch_past_week("1386167364424318976", 2026, 5, tmp_path)
    assert {p.stem for p in tmp_path.glob("*.json")} == set(HISTORY_FILES)
```

In `tests/test_cli.py`, add `"history"` to the loop in `test_help_lists_commands`.

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_history.py tests/test_cli.py -v`
Expected: FAIL with an import error, and `history` missing from the help.

- [ ] **Step 3: Write `fetch_past_week`, `history.py`, `run_history`, and the `history` subcommand**

- [ ] **Step 4: Run the tests, then the live test once**

Run: `uv run pytest -v` then `uv run pytest -m live tests/test_history.py -v`
Expected: all pass.

- [ ] **Step 5: Fetch the real history**

Run: `uv run cornerstone history --season 2026 --through 5`
Expected: `Fetched weeks: 1, 2, 3, 4, 5`. Each of `data/2026/history/week-01` to `week-05` holds four files.

- [ ] **Step 6: Cut the test fixtures**

Write a script in the session scratchpad. It copies `matchups.json` and `transactions.json` of each history week into `tests/fixtures/2026/history/week-0N/` as they are. It cuts `stats.json` and `projections.json` to the rows whose `player_id` is in the `players` list of any matchup entry of weeks 1 to 6. Week 6 comes from `tests/fixtures/2026/week-06/raw/matchups.json`. Do not commit the script.

- [ ] **Step 7: Commit**

```bash
git add src/cornerstone/history.py src/cornerstone/sleeper.py src/cornerstone/pipeline.py src/cornerstone/cli.py tests/ data/2026/history
git commit -m "Fetch and cache past weeks with cornerstone history"
```

---

### Task 2: Parse the history into models

**Files:**
- Modify: `src/cornerstone/models.py`, `src/cornerstone/parse.py`, `src/cornerstone/history.py`, `tests/test_history.py`

**Interfaces:**
- Consumes: `history_dir`, `HISTORY_FILES` from Task 1.
- Produces:
  - `PastWeek(week: int, scores: dict[int, float], pairs: list[tuple[int, int]], points: dict[str, float], projections: dict[str, float], stats: dict[str, dict[str, float]], moves: list[Move])`. `points` merges `players_points` of every roster. `pairs` holds sorted roster id pairs, full pairs only.
  - `History(week: int, weeks: dict[int, PastWeek])` with `complete(self) -> bool`: true when every week from 1 to `week` is in `weeks`.
  - `parse_moves(transactions: list[dict]) -> list[Move]` in `parse.py`. It replaces the private `_moves`. `parse_week` calls it.
  - `parse_past_week(raw: dict[str, object], week: int) -> PastWeek` in `parse.py`. It reads the keys `matchups`, `transactions`, `stats`, `projections`. It skips the empty slot `"0"`.
  - `load_history(root: Path, raw: dict[str, object], week: int) -> History` in `history.py`. Weeks 1 to `week - 1` come from disk. The current week comes from `raw`. A week with a missing file is absent from `weeks`.

- [ ] **Step 1: Write the failing tests**

```python
def test_load_history_has_six_weeks(fixture_history_root, fixture_raw_dir):
    h = load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)
    assert sorted(h.weeks) == [1, 2, 3, 4, 5, 6] and h.complete()
    assert h.weeks[1].scores[6] == 153.54
    assert h.weeks[6].scores[7] == 46.08
    assert (6, 10) in h.weeks[6].pairs
    assert h.weeks[5].points["12501"] == 17.3

def test_missing_week_is_incomplete(tmp_path, fixture_history_root, fixture_raw_dir):
    shutil.copytree(fixture_history_root, tmp_path / "h")
    shutil.rmtree(tmp_path / "h" / "week-03")
    h = load_history(tmp_path / "h", load_raw(fixture_raw_dir), week=6)
    assert sorted(h.weeks) == [1, 2, 4, 5, 6] and not h.complete()

def test_parse_moves_matches_parse_week(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert parse_moves(raw["transactions"]) == parse_week(raw).moves
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_history.py -v`
Expected: FAIL, `load_history` is not defined.

- [ ] **Step 3: Write the models, `parse_moves`, `parse_past_week`, and `load_history`**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/models.py src/cornerstone/parse.py src/cornerstone/history.py tests/test_history.py
git commit -m "Parse the cached weeks into a season history"
```

---

### Task 3: Standings, ranks before, and schedule strength from the history

**Files:**
- Modify: `src/cornerstone/facts_league.py`, `src/cornerstone/sheet.py`, `tests/test_facts_league.py`

**Interfaces:**
- Consumes: `History`, `PastWeek` from Task 2.
- Produces:
  - `season_records(history: History, through: int) -> dict[int, tuple[int, int, float]]`: wins, losses, and points for over weeks 1 to `through`. Each week counts the head-to-head result and the median result. The median is the mean of the 6th and 7th scores, as in `median_facts`. A tie in either game counts as neither.
  - `standings(week: Week, history: History | None = None) -> list[Standing]`. With a complete history, wins, losses, points for, and the opponent win rate in `schedule_strength` come from `season_records(history, week.week)`. Else it reads `week.teams` and logs the warning `history incomplete: standings from rosters.json`.
  - `ranks_before(week: Week, table: list[Standing], history: History | None = None) -> dict[int, int]`. With a complete history, it ranks `season_records(history, week.week - 1)`. Else it keeps the version 1 subtraction.
  - `matchup_of_the_week(week, mfacts, table, before: dict[int, int] | None = None) -> Pick`. It uses `before` when given.
  - `Context.__init__(self, week, news, history: History | None = None)` and `build_bundle(week, news=fetch_news, history: History | None = None) -> Bundle`. Context passes the history to `standings` and `ranks_before`, and passes `self.before` to `matchup_of_the_week`.
  - `Context.history` holds the `History` object, or `None`. The version 1 `list[SeasonHistory]` moves to `Context.season_history`. `build_bundle` sets `WeekData.history` from `c.season_history`.

- [ ] **Step 1: Write the failing tests**

```python
def _history(raw_dir, root):
    return load_history(root, load_raw(raw_dir), week=6)

def test_standings_come_from_history(fixture_raw_dir, fixture_history_root):
    wk, _ = _setup(fixture_raw_dir)
    for t in wk.teams.values():
        t.wins, t.losses, t.points_for = 0, 0, 0.0
    t = standings(wk, _history(fixture_raw_dir, fixture_history_root))
    rows = {wk.teams[s.roster_id].name: (s.rank, s.wins, s.losses, s.points_for) for s in t}
    assert rows["Lil Fridge"] == (1, 10, 2, 739.67)
    assert rows["Bo Girds"] == (3, 8, 4, 723.15)
    assert rows["Pukancun on 3"] == (12, 1, 11, 493.39)

def test_schedule_strength_comes_from_history(fixture_raw_dir, fixture_history_root):
    wk, _ = _setup(fixture_raw_dir)
    real = [s.schedule_strength for s in standings(wk)]
    for t in wk.teams.values():
        t.wins, t.losses = 0, 1
    assert [s.schedule_strength for s in standings(wk, _history(fixture_raw_dir, fixture_history_root))] == real

def test_ranks_before_from_history(fixture_raw_dir, fixture_history_root):
    wk, _ = _setup(fixture_raw_dir)
    h = _history(fixture_raw_dir, fixture_history_root)
    before = ranks_before(wk, standings(wk, h), h)
    by_name = {wk.teams[rid].name: rank for rid, rank in before.items()}
    assert (by_name["behold the lamb"], by_name["Bo Girds"]) == (11, 2)
    assert (by_name["Return of T Mac"], by_name["Unsolicited Dak Picks"]) == (9, 7)

def test_incomplete_history_falls_back_with_a_warning(fixture_raw_dir, caplog):
    wk, _ = _setup(fixture_raw_dir)
    h = History(week=6, weeks={})
    assert standings(wk, h) == standings(wk)
    assert "history incomplete" in caplog.text
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_facts_league.py -v`
Expected: FAIL, `standings()` takes no `history`.

- [ ] **Step 3: Write `season_records` and the history paths in `standings`, `_schedule_strength`, `ranks_before`, `matchup_of_the_week`, and `Context`**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass. The version 1 tests still pass, because they pass no history.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/facts_league.py src/cornerstone/sheet.py tests/test_facts_league.py
git commit -m "Compute the standings and the ranks before the week from the history"
```

---

### Task 4: Team history facts

**Files:**
- Modify: `src/cornerstone/models.py`, `src/cornerstone/facts_league.py`, `src/cornerstone/sheet.py`, `src/cornerstone/prompts/vocabulary.md`, `tests/conftest.py`, `tests/test_sheet.py`, `tests/test_verifier.py`

**Interfaces:**
- Consumes: `History`, `season_records`, `build_bundle(..., history=)` from Task 3.
- Produces:
  - `SeasonHistory` gains `average: float = 0.0`, `trend: float | None = None`, `streak: int = 0`. A positive streak counts wins, a negative streak counts losses. A head-to-head tie ends a streak.
  - `season_history(week: Week, history: History | None = None) -> list[SeasonHistory]`. With no history it keeps the version 1 result. `Context.season_history` holds the result.
  - `history_facts(c: Context) -> list[Fact]` in `sheet.py`. It returns nothing unless `c.history` is complete.
  - `HISTORY_FACTS_MAX = 6` in `sheet.py`. `chapters()` adds the `H.` facts of both teams to `motw` and to each `recap_{mid}`, and adds `H.` facts to `median` and `next_week`. The selection under the cap is the builder's call.

Fact rules, with `avg` the season average over weeks 1 to N and the trend the mean of the last 3 weeks:

| ID | When | Text |
| --- | --- | --- |
| `H.{rid}.streak` | streak of 2 or more | `{team} has won {n} straight.` or `{team} has lost {n} straight.` |
| `H.{rid}.trend` | trend differs from avg | `{team} has scored {trend} per week over the last 3 weeks, {up/down} from a season average of {avg}.` |
| `H.{rid}.high` | this week is above every earlier week, or below | `{team}'s {pts} this week is a season high.` or `... a season low.` |
| `H.{rid}.avg` | always | `{team} averages {avg} per week this season.` |

Round with `r2` on `Decimal` sums.

Vocabulary lines, added after **position rank**:

```
- **streak**: head-to-head results only, the median game excluded.
- **team trend**: the last 3 weeks against the season average.
- **season high**: a team's highest weekly total this season.
- **season low**: a team's lowest weekly total this season.
- **season average**: a team's points for divided by the weeks played this season.
```

- [ ] **Step 1: Write the failing tests**

Put `hbundle` in `tests/conftest.py`, so later tasks in other test files can use it.

```python
@pytest.fixture
def hbundle(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    return build_bundle(parse_week(raw), news=lambda pid: [],
                        history=load_history(fixture_history_root, raw, week=6))

def test_streak_facts(hbundle):
    f = hbundle.sheet.facts
    assert f["H.8.streak"].text == "Return of T Mac has won 3 straight."
    assert f["H.6.streak"].text == "Bo Girds has lost 2 straight."
    assert "H.2.streak" not in f  # All You Need Is Love won 1

def test_trend_facts(hbundle):
    f = hbundle.sheet.facts
    assert f["H.8.trend"].text == ("Return of T Mac has scored 128.82 per week over the last 3 weeks, "
                                   "up from a season average of 103.16.")
    assert f["H.6.trend"].text == ("Bo Girds has scored 117.71 per week over the last 3 weeks, "
                                   "down from a season average of 120.53.")

def test_high_low_and_average(hbundle):
    f = hbundle.sheet.facts
    assert f["H.7.high"].text == "To Infinity and Bijan's 46.08 this week is a season low."
    assert f["H.11.high"].text == "Unsolicited Dak Picks's 81.47 this week is a season low."
    assert not any("season high" in x.text for x in f.values())
    assert f["H.6.avg"].text == "Bo Girds averages 120.53 per week this season."

def test_history_facts_capped_per_chapter(hbundle):
    for c in hbundle.sheet.chapters:
        assert sum(fid.startswith(("H.", "P.")) for fid in c.fact_ids) <= 6, c.key

def test_no_history_facts_without_history(bundle):
    assert not any(fid.startswith("H.") for fid in bundle.sheet.facts)
```

Also run `test_every_number_appears_in_its_text` and `test_every_number_token_in_text_is_in_numbers` on `hbundle`: parametrize them over both fixtures.

In `tests/test_verifier.py`, replace `test_vocabulary_has_no_season_history_terms` with `test_vocabulary_has_the_history_terms`. It asserts each of `**streak**`, `**team trend**`, `**season high**`, `**season low**`, `**season average**` is in `vocabulary.md`.

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_sheet.py tests/test_verifier.py -v`
Expected: FAIL, `build_bundle()` gives no `H.` facts.

- [ ] **Step 3: Extend `SeasonHistory` and `season_history`, write `history_facts`, attach the facts, and add the vocabulary lines**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/ tests/conftest.py tests/test_sheet.py tests/test_verifier.py
git commit -m "Add streak, trend, season high, and season average facts"
```

---

### Task 5: Player trend and recent adds from the week before

**Files:**
- Modify: `src/cornerstone/history.py`, `src/cornerstone/sheet.py`, `src/cornerstone/prompts/vocabulary.md`, `tests/test_history.py`, `tests/test_sheet.py`

**Interfaces:**
- Consumes: `History`, `PastWeek`, `hbundle` from Tasks 2 to 4.
- Produces:
  - `player_points(past: PastWeek, player_id: str) -> float | None` in `history.py`: `past.points` first, then `past.stats[player_id]["pts_half_ppr"]`, else `None`.
  - `player_trend(history: History, player_id: str) -> int | None`: the count of weeks N-2 to N where the points are above the projection. `None` when any of the 3 weeks has no points or no projection.
  - `Context.moves`: `week.moves` plus `history.weeks[week.week - 1].moves` when that week is present. `matchup_facts` and `recent_add_facts` read `c.moves`.
  - `P.{pid}.trend` for each started line, only with a complete history. Text with `b` beaten: `{name} has beaten projection in {b} of the last 3 weeks.` when `b >= 2`, else `{name} has missed projection in {3 - b} of the last 3 weeks.`
  - Attach `P.` facts to `motw` and `recap_{mid}` for the matchup's starters, to `awards` for the award winners, and to `game_changer` for the Game Changer. The cap from Task 4 holds.
  - `_trend_text(name: str, beaten: int, n: Nums) -> str` in `sheet.py`. Task 9 reuses it.

Vocabulary line:

```
- **player trend**: against projection over the last 3 weeks.
```

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_history.py
def test_player_trend(fixture_history_root, fixture_raw_dir):
    h = load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)
    assert player_trend(h, "12501") == 3   # Matthew Golden
    assert player_trend(h, "9509") == 1    # Bijan Robinson

# tests/test_sheet.py
def test_player_trend_facts(hbundle):
    f = hbundle.sheet.facts
    assert f["P.12501.trend"].text == "Matthew Golden has beaten projection in 3 of the last 3 weeks."
    assert f["P.9509.trend"].text == "Bijan Robinson has missed projection in 2 of the last 3 weeks."

def test_week_five_add_is_a_recent_add(hbundle, bundle):
    assert "week 5" in hbundle.sheet.facts["M4.move.13274"].text  # Germie Bernard, waiver
    assert "M4.move.13274" not in bundle.sheet.facts
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_history.py tests/test_sheet.py -v`
Expected: FAIL, `player_trend` is not defined.

- [ ] **Step 3: Write `player_points`, `player_trend`, `Context.moves`, the `P.` facts, and the vocabulary line**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass, with the cap test still green.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/ tests/test_history.py tests/test_sheet.py
git commit -m "Add the player trend and read recent adds from the week before"
```

---

### Task 6: Wire the history into the build

**Files:**
- Modify: `src/cornerstone/models.py`, `src/cornerstone/history.py`, `src/cornerstone/pipeline.py`, `tests/test_pipeline.py`

**Interfaces:**
- Consumes: `load_history`, `build_bundle(..., history=)` from Tasks 2 to 5.
- Produces:
  - `BuildRecord(started: datetime, sources: dict[str, bool])`. This task sets the source key `"history"`.
  - `VerifyFile(build: BuildRecord | None = None, chapters: dict[str, list[VerifyResult]])`. `verify.json` holds this shape.
  - `read_verify(path: Path) -> VerifyFile` in `pipeline.py`. It also reads the version 1 shape, a plain dict of chapter lists, as `build=None`.
  - `make_bundle(repo: Path, season: int, week: int, news: NewsFetcher = fetch_news, started: datetime | None = None) -> tuple[Bundle, BuildRecord]` in `pipeline.py`. It loads the raw data, runs the week gate and raises `BuildStopped`, loads the history, and builds the bundle. `started` defaults to the current time in `America/New_York`. `run_build` calls it in place of its own parse and build.
  - `save_week_to_history(raw_dir: Path, out_dir: Path) -> None` in `history.py`. It puts the four `HISTORY_FILES` in `out_dir` and writes `injuries.json`: `{player_id: injury_status}` for every player in this week's `matchups.json` with a status in `players.json`. Copy or symlink is the builder's call. `run_build` calls it after the render.
  - `run_rewrite` reads with `read_verify` and writes the `VerifyFile` back with its `build` unchanged.

- [ ] **Step 1: Write the failing tests**

```python
def _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo(tmp_path, fixture_raw_dir)
    shutil.copytree(fixture_history_root, history_root(repo, 2026))
    return repo

def test_build_records_the_history_source(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    record = read_verify(week_dir(repo, 2026, 6) / "verify.json").build
    assert record.sources["history"] is True

def test_build_without_history_degrades(tmp_path, fixture_raw_dir, caplog):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.sources["history"] is False
    assert "history incomplete" in caplog.text

def test_build_saves_the_week_to_history(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    out = history_dir(history_root(repo, 2026), 6)
    assert {p.stem for p in out.glob("*.json")} == {*HISTORY_FILES, "injuries"}
    injuries = json.loads((out / "injuries.json").read_text())
    assert injuries["2216"] == "Out"           # Mike Evans
    assert injuries["5859"] == "Questionable"  # A.J. Brown

def test_rewrite_reads_the_version_1_verify_shape(tmp_path, fixture_raw_dir):
    # Build, then overwrite verify.json with {key: [results]} and rewrite "median".
    assert read_verify(path).build is None
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_pipeline.py -v`
Expected: FAIL, `read_verify` is not defined.

- [ ] **Step 3: Write the models, `read_verify`, `make_bundle`, and `save_week_to_history`, and change `run_build` and `run_rewrite`**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/ tests/test_pipeline.py
git commit -m "Read the history in the build and save each built week to it"
```

---

### Task 7: Smoke test week 6 after part 1

**Files:**
- Create: `$SCRATCH/smoke_week6.py`, where `$SCRATCH` is the session scratchpad directory. It stays out of the repo.

- [ ] **Step 1: Write the smoke script**

```python
"""Smoke test: build week 6 from disk and render it in the scratchpad.
It makes no Claude call, so it reuses the saved blurbs."""
import sys
from pathlib import Path
from pydantic import TypeAdapter
from cornerstone.models import Blurb
from cornerstone.pipeline import make_bundle, week_dir
from cornerstone.render import render_index, render_week
from cornerstone.sheet import read_bundle, write_bundle
repo, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
bundle, record = make_bundle(repo, 2026, 6, news=lambda pid: [])
write_bundle(bundle, out / "facts.json")
bundle = read_bundle(out / "facts.json")
blurbs = TypeAdapter(dict[str, Blurb]).validate_json((week_dir(repo, 2026, 6) / "blurbs.json").read_text())
page = render_week(bundle, blurbs, out / "site", lambda url: None)
render_index(out / "site")
print(page, record.sources, len(bundle.sheet.facts))
```

- [ ] **Step 2: Run it**

Run: `uv run python $SCRATCH/smoke_week6.py . $SCRATCH/smoke`
Expected: the page path, `{'history': True}`, and a fact count. `grep -c '"H\.8\.streak"' $SCRATCH/smoke/facts.json` prints a count of 1 or more.

- [ ] **Step 3: Check the page**

Open `$SCRATCH/smoke/site/2026/week-06/index.html` at 390px wide. Expected: every version 1 chapter renders, and the page has no horizontal scroll.

- [ ] **Step 4: Run the full suite and commit any fix**

Run: `uv run pytest -v`
Expected: all pass. If the smoke run needed a fix, commit it with a subject that names the fix. If not, `git status --short` prints nothing and no commit is due.

---

## Part 2: the Trades chapter

### Task 8: The trade model and the week's trade window

**Files:**
- Create: `src/cornerstone/trades.py`, `tests/test_trades.py`
- Modify: `src/cornerstone/models.py`, `src/cornerstone/parse.py`, `src/cornerstone/sleeper.py`, `src/cornerstone/pipeline.py`, `tests/test_pipeline.py`, `tests/test_sleeper.py`, `tests/fixtures/2026/week-06/raw/transactions.json`

**Interfaces:**
- Consumes: `PastWeek`, `BuildRecord`, `read_verify`, `make_bundle` from Part 1.
- Produces:
  - `DraftPick(season: str, round: int, roster_id: int, previous_owner_id: int, owner_id: int)`.
  - `Trade(transaction_id: str, created: datetime, roster_ids: list[int], adds: dict[str, int], drops: dict[str, int], draft_picks: list[DraftPick])`. `created` is the aware datetime of Sleeper's epoch milliseconds.
  - `parse_trades(transactions: list[dict]) -> list[Trade]` in `parse.py`: rows with `type == "trade"` and `status == "complete"`. `PastWeek` gains `trades: list[Trade] = []`.
  - `default_cutoff(season_start: date, week: int) -> datetime` in `trades.py`: 08:00 `America/New_York` on the Tuesday after week N-1, that is `season_start + timedelta(days=6 + 7 * (week - 2))`.
  - `BuildRecord` gains `fetched: datetime | None = None`: the fetch time of this week's `transactions.json`, the `until` of the window.
  - `fetch_week` writes `raw/fetched.json` as `{"transactions": "<ISO time>"}`, the aware time just after the `transactions/{week}` call returns. The file is outside `RAW_FILES`, so `load_raw` does not change. It stays on disk, so a `--no-fetch` rebuild reads the same value.
  - `read_fetch_time(raw_dir: Path) -> datetime | None` in `sleeper.py` reads that file. `None` when it is absent.
  - `previous_fetch_time(repo: Path, season: int, week: int) -> datetime | None` in `trades.py`: `build.fetched` from the `verify.json` of week N-1.
  - `trades_for_week(this_week: list[Trade], last_week: list[Trade], after: datetime, until: datetime) -> list[Trade]`: trades with `after < created <= until`, no duplicate `transaction_id`, oldest first. The list index plus 1 is the `n` in `T{n}`.
  - `is_late(trade: Trade, week: Week) -> bool`: true when a player the trade moved is in this week's matchup lines of the roster that gave him. Such a trade happened after his game, so his points went to the old roster. This is the spec rule. A late trade gets a card and a grade, no `swing` and no `need`.
  - `WeekData` gains `trades: list[Trade] = []`, a Pydantic field default. `build_bundle` gains `trades: list[Trade] | None = None`, read as no trades.
  - `make_bundle` gains `fetched: datetime | None = None` and computes the window. `after` is `previous_fetch_time(...)`, else `default_cutoff(...)`. `until` is `fetched`, else `read_fetch_time(raw_dir)`, else `started` with the warning `no fetch time for week {N}: window ends at the build start`. The build-start fallback is for week 6 only, because version 1 saved no fetch time. The spec says so. `this_week` comes from `raw["transactions"]`, `last_week` from the history week N-1, with a warning when that week is absent. The `BuildRecord` holds the `until` it used in `fetched`.
  - `run_build` passes the `fetched` of an existing `verify.json` build record for the same week to `make_bundle`. A rebuild therefore never moves the window, also after a `--refetch`.

- [ ] **Step 1: Add the Tuesday trade to the fixture**

The fixture `tests/fixtures/2026/week-06/raw/transactions.json` holds 5 trades. The trade between rosters 7 and 8, created 2026-10-20 11:55 ET, is only in `data/2026/week-06/raw/transactions.json`. Copy that one row into the fixture, as it is. Keep the other rows. Commit the fixture with this task. Every later count of 6 trades depends on it.

- [ ] **Step 2: Write the failing tests**

```python
ET = ZoneInfo("America/New_York")

def _six(fixture_raw_dir, fixture_history_root, until):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    return trades_for_week(parse_trades(raw["transactions"]), h.weeks[5].trades,
                           default_cutoff(date(2026, 9, 9), 6), until)

def test_default_cutoff_week_6():
    assert default_cutoff(date(2026, 9, 9), 6) == datetime(2026, 10, 13, 8, 0, tzinfo=ET)

def test_window_holds_the_six_week_6_trades(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    assert [x.roster_ids for x in t] == [[4, 12], [7, 12], [4, 7], [6, 7], [11, 12], [7, 8]]

def test_window_end_drops_the_tuesday_trade(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 8, 0, tzinfo=ET))
    assert len(t) == 5 and t[-1].roster_ids == [11, 12]

def test_late_trade(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [is_late(x, wk) for x in t] == [False, False, False, False, False, True]

# tests/test_pipeline.py
def _fetched(repo, when):
    (week_dir(repo, 2026, 6) / "raw" / "fetched.json").write_text(json.dumps({"transactions": when.isoformat()}))

def test_window_ends_at_the_saved_fetch_time(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    _fetched(repo, datetime(2026, 10, 20, 8, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    bundle = read_bundle(week_dir(repo, 2026, 6) / "facts.json")
    assert len(bundle.data.trades) == 5
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.fetched == datetime(2026, 10, 20, 8, 0, tzinfo=ET)

def test_rebuild_keeps_the_first_fetch_time(tmp_path, fixture_raw_dir, fixture_history_root):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    _fetched(repo, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    _fetched(repo, datetime(2026, 10, 21, 9, 0, tzinfo=ET))
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert read_verify(week_dir(repo, 2026, 6) / "verify.json").build.fetched == datetime(2026, 10, 20, 12, 0, tzinfo=ET)

def test_window_starts_at_the_fetch_before(tmp_path, fixture_raw_dir, fixture_history_root):
    # Write data/2026/week-05/verify.json with build.fetched 2026-10-16 18:00 ET.
    bundle, _ = make_bundle(repo, 2026, 6, news=_no_news,
                            fetched=datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    assert [x.roster_ids for x in bundle.data.trades] == [[11, 12], [7, 8]]

def test_window_without_a_fetch_time_ends_at_the_build_start(tmp_path, fixture_raw_dir, fixture_history_root, caplog):
    bundle, record = make_bundle(repo, 2026, 6, news=_no_news,
                                 started=datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    assert len(bundle.data.trades) == 6 and record.fetched == datetime(2026, 10, 20, 12, 0, tzinfo=ET)
    assert "no fetch time for week 6" in caplog.text

# tests/test_sleeper.py
@pytest.mark.live
def test_fetch_week_records_the_fetch_time(tmp_path):
    fetch_week("1386167364424318976", 2026, 6, tmp_path / "raw", tmp_path / "players.json")
    assert read_fetch_time(tmp_path / "raw").tzinfo is not None
```

- [ ] **Step 3: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_trades.py tests/test_pipeline.py -v`
Expected: FAIL with an import error.

- [ ] **Step 4: Write the models, `parse_trades`, `trades.py`, the fetch time in `fetch_week`, and the window in `make_bundle` and `run_build`**

Record the fetch time in `fetch_week` or right after it. The place is the builder's call. The value must be on disk in `raw/`, so a `--no-fetch` rebuild gets the same `until`.

- [ ] **Step 5: Run all tests**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add src/cornerstone/ tests/test_trades.py tests/test_pipeline.py tests/test_sleeper.py tests/fixtures/2026/week-06/raw/transactions.json
git commit -m "Pick the trades of the week by the time of the build before"
```

---

### Task 9: Trade facts and the trades chapter

**Files:**
- Modify: `src/cornerstone/models.py`, `src/cornerstone/parse.py`, `src/cornerstone/sheet.py`, `src/cornerstone/verifier.py`, `src/cornerstone/prompts/vocabulary.md`, `src/cornerstone/prompts/writer.md`, `tests/conftest.py`, `tests/test_sheet.py`, `tests/test_trades.py`, `tests/test_verifier.py`, `tests/test_writer.py`

**Interfaces:**
- Consumes: `Trade`, `is_late`, `trades_for_week` from Task 8. `player_points`, `player_trend`, `_trend_text` from Task 5.
- Produces:
  - `Week` gains `roster_slots: int = 0`: `len(roster_positions)` plus `settings.reserve_slots` from `league.json`. Week 6 gives 15. The reserve slot counts, because `matchups.json` `players` lists the injured reserve player: rosters 4 and 7 hold 15.
  - `trade_facts(c: Context) -> list[Fact]` in `sheet.py`. `Context` gains `trades`.
  - `Chapter` gains `grade_keys: list[str] = []`. The `trades` chapter sets `T{n}.{rid}` for each roster of each trade, in trade order, then roster order.
  - `SENTENCE_RANGES["trades"] = (4, 6)`.
  - The chapter `trades`, title `Trades`, exists only when `c.trades` is not empty. Its facts are every `T` fact plus the `S.` facts of the trade rosters. Its scope is the trade rosters.
  - `verifier.py`: the `decided` gate also passes a cited ID that matches `re.fullmatch(r"T\d+\.\d+\.swing", fid)`. The `cost` gate already passes it, because the ID holds `.swing`.
  - `writer.md` rule 6, full new text: `6. Never say "decided" or "decider" unless a cited fact ID contains `.driver`, or the sentence cites a trade swing fact `T{n}.{rid}.swing` whose gap is at least the margin.`

Fact rules. Items join as `A`, `A and B`, `A, B and C`. A player list keeps the order of the trade's `adds` map. A pick reads `{season} round {round} pick`.

| ID | When | Text |
| --- | --- | --- |
| `T{n}.sides` | two rosters | `{A} traded {items A gave} to {B} for {items A got}.` with A = `roster_ids[0]` |
| `T{n}.sides` | three or more rosters | `In a {k}-team trade, {team} got {items}; {team} got {items}.` one clause per roster |
| `T{n}.{rid}.got.{pid}` | each player the roster got | `{team} got {name}: {pts} this week, {season} this season, position rank {r} of {of}.` then the trend sentence |
| `T{n}.{rid}.gave.{pid}` | each player the roster gave | `{team} gave {name}: ...` same shape |
| `T{n}.{rid}.need` | trade not late | `{team} is {w}-{l}, {rank} of 12, with {n} {POS} and {n} {POS} after the trade and {k} open roster spot(s).` |
| `T{n}.{rid}.swing` | trade not late, and a started player on either side | `The players {team} got scored {x} this week; the players it gave scored {y}. The gap is {z}, {above/equal to/below} the margin of {m} in its matchup.` |

- The `got` and `gave` facts drop the season clause and the trend sentence without a complete history. They drop the rank clause for a player who did not start. The rank is the `RANK.{pid}` rank.
- The `need` positions are the positions of every player in the trade, in alphabetical order. The count is of the roster's lines in this week's matchup. Open spots are `max(0, roster_slots - line count)`. Use `spot` for 1.
- A late trade gets no `need` fact, because the lineup-lock roster is from before the trade.
- In `swing`, `x` sums the players the roster got that it started this week. `y` sums the players it gave that their new roster started this week. `z = abs(x - y)`. `m` is the margin of the roster's matchup.

Vocabulary lines:

```
- **roster need**: depth at the traded positions and open spots, as of this week's lineup.
- **trade swing**: the gap against the margin. Only when the gap is at least the margin may the writer say the trade decided the game.
- **trade grade**: an opinion from the fact sheet, A to F, with the reason.
```

- [ ] **Step 1: Write the failing tests**

Put `tbundle` in `tests/conftest.py`. Tasks 10 and 11 use it.

```python
@pytest.fixture
def tbundle(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    trades = trades_for_week(parse_trades(raw["transactions"]), h.weeks[5].trades,
                             default_cutoff(date(2026, 9, 9), 6), datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    return build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=trades)

def test_sides_fact(tbundle):
    assert tbundle.sheet.facts["T5.sides"].text == (
        "Unsolicited Dak Picks traded Bhayshul Tuten and Garrett Wilson to "
        "Amon-Ra Dawg Your Team for Devaughn Vele and Josh Jacobs.")

def test_got_facts(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12.got.12490"].text.startswith(
        "Amon-Ra Dawg Your Team got Bhayshul Tuten: 22.7 this week, 81.9 this season, position rank 4 of 31.")
    assert f["T5.11.got.5850"].text.startswith(
        "Unsolicited Dak Picks got Josh Jacobs: 0 this week, 0 this season.")
    assert f["T5.12.gave.11834"].text.startswith(
        "Amon-Ra Dawg Your Team gave Devaughn Vele: 5.7 this week, 55.4 this season")
    assert "T5.11.gave.12490" in f

def test_need_fact(tbundle):
    assert tbundle.sheet.facts["T5.12.need"].text == (
        "Amon-Ra Dawg Your Team is 4-8, 9th of 12, with 5 RB and 5 WR after the trade and 1 open roster spot.")

def test_swing_facts(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12.swing"].text == (
        "The players Amon-Ra Dawg Your Team got scored 29.1 this week; the players it gave scored 0. "
        "The gap is 29.1, above the margin of 9.51 in its matchup.")
    assert f["T5.11.swing"].text.endswith("The gap is 29.1, below the margin of 38.82 in its matchup.")

def test_late_trade_has_no_swing_and_no_need(tbundle):
    f = tbundle.sheet.facts
    assert not any(fid.startswith("T6.") and fid.endswith((".swing", ".need")) for fid in f)
    assert "T6.sides" in f

def test_trades_chapter(tbundle):
    ch = next(c for c in tbundle.sheet.chapters if c.key == "trades")
    assert ch.grade_keys == ["T1.4", "T1.12", "T2.7", "T2.12", "T3.4", "T3.7",
                             "T4.6", "T4.7", "T5.11", "T5.12", "T6.7", "T6.8"]
    assert (ch.min_sentences, ch.max_sentences) == (4, 6)

def test_no_trades_no_chapter(hbundle):
    assert "trades" not in {c.key for c in hbundle.sheet.chapters}

def test_three_team_trade(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    three = next(t for t in h.weeks[5].trades if len(t.roster_ids) == 3)
    f = build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=[three]).sheet.facts
    assert f["T1.sides"].text.startswith("In a 3-team trade,")
    assert all(name in f["T1.sides"].text for name in ("To Infinity and Bijan", "Return of T Mac", "Amon-Ra Dawg Your Team"))

def test_got_fact_without_history(fixture_raw_dir):
    # Build with the same trades and history=None.
    assert f["T5.12.got.12490"].text == (
        "Amon-Ra Dawg Your Team got Bhayshul Tuten: 22.7 this week, position rank 4 of 31.")

def test_need_clamps_open_spots_at_zero(tbundle):
    # Pukancun on 3 lists 15 players against 15 slots.
    need = tbundle.sheet.facts["T1.4.need"]
    assert need.text.endswith("and 0 open roster spots.")
    assert "0" in need.numbers

# tests/test_verifier.py
def test_trade_swing_passes_the_cost_and_decided_gates(...):
    # In the trades chapter, "The trade decided it and cost them." citing T5.12.swing gives no gate failure.

# tests/test_writer.py
def test_writer_rule_6_allows_the_trade_swing(fixture_raw_dir):
    # The system prompt holds "or the sentence cites a trade swing fact `T{n}.{rid}.swing`".
```

Run the two number tests from `test_sheet.py` on `tbundle` too.

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_trades.py tests/test_verifier.py tests/test_writer.py -v`
Expected: FAIL, no `T5.sides` fact.

- [ ] **Step 3: Write `roster_slots`, `trade_facts`, the `trades` chapter, the gate change, writer rule 6, and the vocabulary lines**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/ tests/conftest.py tests/test_sheet.py tests/test_trades.py tests/test_verifier.py tests/test_writer.py
git commit -m "Add the trade facts and the Trades chapter"
```

---

### Task 10: Trade grades from the writer

**Files:**
- Modify: `src/cornerstone/models.py`, `src/cornerstone/writer.py`, `src/cornerstone/verifier.py`, `src/cornerstone/prompts/writer.md`, `src/cornerstone/prompts/verifier.md`, `tests/test_writer.py`, `tests/test_verifier.py`

**Interfaces:**
- Consumes: `Chapter.grade_keys`, `tbundle` from Task 9.
- Produces:
  - `Grade(key: str, letter: str)` and `TradesWriterOut(WriterOut)` with `grades: list[Grade] = []`. A list, not a dict, keeps the structured output schema to fixed keys.
  - `Blurb` gains `grades: dict[str, str] = {}`, keyed by `T{n}.{rid}`. The spec says "keyed by roster id". One roster can make several trades in a week, as roster 7 does four times in week 6, so the key names the trade too.
  - `write_blurb` calls with `TradesWriterOut` when `chapter.grade_keys` is not empty. It maps the list into `Blurb.grades`.
  - `build_writer_prompt` adds the line `Grade keys: T1.4, T1.12, ...` after the sentence range when `chapter.grade_keys` is not empty.
  - `code_check` for a chapter with `grade_keys`: `set(blurb.grades)` must equal `set(chapter.grade_keys)`, and each letter must be one of `A`, `B`, `C`, `D`, `F`. Failure text: `[0] grade for {key} is missing`, `[0] grade for {key} is not a trade side`, `[0] grade {key} is '{letter}'; use one letter A, B, C, D, or F`.
  - `template_blurb` for `trades`: one sentence per `T{n}.sides` fact, with that fact's ID, and no grades.

Writer rules, appended to `writer.md` as rules 18 to 20:

```
18. In the Trades chapter, grade each side of each trade on value, from the fact sheet only, with weight on this season's points, the trend, the roster need, and the injury status. Give an honest grade: one letter, A, B, C, D, or F. A trade can be a C for both sides. Put each grade in `grades` under a key from the "Grade keys" line. Give the reason in the sentences.
19. With more than two trades, write about the two with the widest gap between the grades. Name the rest in one sentence.
20. Never put a number on a draft pick.
```

Verifier rule, appended to the list in `verifier.md`:

```
- A trade grade is an opinion. A letter grade and the judgment behind it make no factual claim. Every number in the reason still needs a chapter fact.
```

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_writer.py
def test_trades_prompt_lists_grade_keys(tbundle):
    ch = next(c for c in tbundle.sheet.chapters if c.key == "trades")
    _, user = build_writer_prompt(ch, tbundle.sheet, None)
    assert "Grade keys: T1.4, T1.12, T2.7, T2.12, T3.4, T3.7, T4.6, T4.7, T5.11, T5.12, T6.7, T6.8" in user

def test_write_blurb_maps_grades(tbundle):
    def call(system, user, model):
        assert model is TradesWriterOut
        return model(sentences=[Sentence(text="x.", fact_ids=["T5.sides"])],
                     grades=[Grade(key="T5.12", letter="A")])
    assert write_blurb(ch, tbundle.sheet, call).grades == {"T5.12": "A"}

def test_trades_template_lists_the_sides(tbundle):
    b = template_blurb(ch, tbundle.sheet)
    assert [s.fact_ids for s in b.sentences] == [[f"T{n}.sides"] for n in range(1, 7)]
    assert b.grades == {}

def test_writer_rules_hold_the_grade_rule():
    # system prompt holds "A trade can be a C for both sides." and "Never put a number on a draft pick."

# tests/test_verifier.py
def test_missing_grade_fails(tbundle):   # all keys but T5.12 -> "grade for T5.12 is missing"
def test_plus_grade_fails(tbundle):      # T5.12 = "B+" -> "use one letter A, B, C, D, or F"
def test_full_grades_pass(tbundle):      # every key "C" -> no grade failure
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_writer.py tests/test_verifier.py -v`
Expected: FAIL, `TradesWriterOut` is not defined.

- [ ] **Step 3: Write the models, the writer changes, the code check, the template, and the prompt rules**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass. The pipeline fake returns no grades, so the `trades` chapter falls back to the template. That is the expected result.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/ tests/test_writer.py tests/test_verifier.py
git commit -m "Let the writer grade each side of a trade and check the grades"
```

---

### Task 11: Render the trade cards

**Files:**
- Modify: `src/cornerstone/render.py`, `src/cornerstone/templates/week.html`, `src/cornerstone/static/style.css`, `tests/test_render.py`

**Interfaces:**
- Consumes: `WeekData.trades`, `Blurb.grades`, `tbundle` from Tasks 8 to 10.
- Produces:
  - `build_context` gains `"trades"`: one item per trade with its sides. A side has the team, the grade or `None`, the players it got with this week's points, and the pick texts.
  - The section `<section class="chap" id="trades">` sits after Awards and before All Matchups. Its label reads `Trades`. Each card has `class="trade"`. A grade renders as `<span class="grade">{letter}</span>` in red. A missing grade renders as `<span class="grade none">No grade</span>` in gray. The blurb sits under the cards. The rest of the markup is the builder's call.
  - The section renders when `blurbs` has no `trades` key, and when the `trades` blurb is a template fallback. In both cases every grade renders as "No grade" in gray, and a missing blurb gives an empty blurb paragraph.
  - Under the cards, a `<p class="blurb note">` in the style of the median note reads: `Grades are Tina's opinion from the fact sheet, not a computed score.`

- [ ] **Step 1: Write the failing tests**

```python
def test_trades_section_order_and_cards(tbundle, tmp_path):
    html = render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png).read_text()
    assert html.index('id="trades"') > html.index(">Awards<")
    assert html.index('id="trades"') < html.index(">All Matchups<")
    assert html.count('class="trade"') == 6
    assert "Bhayshul Tuten" in html and "22.7" in html

def test_grade_letter_and_no_grade(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    blurbs["trades"].grades = {"T5.12": "A"}
    html = render_week(tbundle, blurbs, tmp_path, _fake_png).read_text()
    assert '<span class="grade">A</span>' in html
    assert html.count("No grade") == 11

def test_trades_render_without_a_trades_blurb(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    del blurbs["trades"]
    html = render_week(tbundle, blurbs, tmp_path, _fake_png).read_text()
    assert html.count('class="trade"') == 6 and html.count("No grade") == 12

def test_trades_render_with_the_template_blurb(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    ch = next(c for c in tbundle.sheet.chapters if c.key == "trades")
    blurbs["trades"] = template_blurb(ch, tbundle.sheet)
    html = render_week(tbundle, blurbs, tmp_path, _fake_png).read_text()
    assert html.count("No grade") == 12

def test_trades_opinion_note(tbundle, tmp_path):
    html = render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png).read_text()
    assert "Grades are Tina's opinion from the fact sheet, not a computed score." in html

def test_no_trades_no_section(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    assert 'id="trades"' not in render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_render.py -v`
Expected: FAIL, no `id="trades"`.

- [ ] **Step 3: Write the context, the section, the opinion note, and the CSS**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/render.py src/cornerstone/templates/week.html src/cornerstone/static/style.css tests/test_render.py
git commit -m "Render a card per trade with a grade per side"
```

---

### Task 12: Smoke test week 6 after part 2

- [ ] **Step 1: Run the smoke script**

Run: `uv run python $SCRATCH/smoke_week6.py . $SCRATCH/smoke`
Expected: no error. `grep -c '"T6.sides"' $SCRATCH/smoke/facts.json` prints 1 or more. The old `blurbs.json` has no `trades` key, so each card shows "No grade".

- [ ] **Step 2: Check the page**

Open the page at 390px wide. Expected: 6 trade cards between Awards and All Matchups, and no horizontal scroll.

- [ ] **Step 3: Run the full suite and commit any fix**

Run: `uv run pytest -v`
Expected: all pass. Commit a fix if the run needed one. Else no commit is due.

---

## Part 3 and 4: nflverse drops and injury history

### Task 13: Fetch and parse nflverse

**Files:**
- Create: `src/cornerstone/nflverse.py`, `tests/test_nflverse.py`, `tests/fixtures/nflverse/play_by_play_2026.csv.gz`, `ftn_charting_2026.csv`, `injuries_2026.csv.gz`, `db_playerids.csv`
- Modify: `src/cornerstone/models.py`, `tests/conftest.py`

**Interfaces:**
- Produces, in `nflverse.py`:
  - `PBP_URL`, `FTN_URL`, `INJURIES_URL` with a `{season}` field, and `FFIDS_URL`, all from the spec's tables.
  - `CACHE_MAX_AGE_SECONDS = 24 * 60 * 60`.
  - `http_get(url: str) -> bytes`: `httpx` with `follow_redirects=True`, because GitHub release URLs redirect.
  - `download(url: str, path: Path, max_age_seconds: int = CACHE_MAX_AGE_SECONDS, fetch: Callable[[str], bytes] = http_get) -> Path | None`. A fresh cache returns at once. Else it fetches and replaces the file through a temp file, as `sleeper._players` does. On a failure it returns a stale cache with a warning, or `None` with no cache.
  - `read_drops(pbp: Path, ftn: Path, week: int) -> dict[str, list[DropPlay]] | None`, keyed by the receiver's `gsis_id`. It joins FTN rows with `is_drop == "TRUE"` to play-by-play rows on `(nflverse_game_id, nflverse_play_id)` = `(game_id, play_id)`. It returns `None` when either file has no row for `week`. An `air_yards` of `NA` or empty reads as 0.
  - `read_injuries(path: Path, week: int) -> dict[str, dict[int, str]] | None`: `gsis_id` to week to `report_status`, `season_type == "REG"` rows with a status only. `None` when the file has no row for `week`.
  - `read_id_map(path: Path) -> dict[str, str]`: `sleeper_id` to `gsis_id`, rows with `NA` or empty skipped.
  - `gsis_id(player_id: str, players: dict, id_map: dict[str, str]) -> str | None`: the stripped blob `gsis_id`, else the id map.
  - `nflverse_week(season: int, week: int, player_ids: list[str], players: dict, cache_dir: Path, fetch: Callable[[str], bytes] = http_get) -> NflverseWeek`. The cache file name is the URL's last path part.
- Produces, in `models.py`:
  - `DropPlay(game_id: str, play_id: str, air_yards: float, yardline_100: float)`.
  - `NflverseWeek(sources: dict[str, bool], gsis: dict[str, str], drops: dict[str, list[DropPlay]] | None, injuries: dict[str, dict[int, str]] | None)`. `drops` and `injuries` are keyed by Sleeper player id and cut to `player_ids`. The source keys are `nflverse_pbp`, `nflverse_ftn`, `nflverse_injuries`, `ffverse`.
- Produces, in `conftest.py`: `fixture_nflverse_dir() -> Path` and `nfl_week6(fixture_nflverse_dir, fixture_raw_dir, tmp_path) -> NflverseWeek`. It reads the starters and the players blob from `fixture_raw_dir`. The fixture copies the four files into a fresh cache directory and calls `nflverse_week` with a `fetch` that raises.

Fixture rows, cut by a scratchpad script that keeps the header and every column:

| File | Rows kept |
| --- | --- |
| play-by-play, FTN | week 6 plays: `2026_06_DAL_GB` 1332, 2120, 2852, 632 (Matthew Golden), 824, 4367 (CeeDee Lamb); `2026_06_ARI_LA` 2554, 3519 (Kyren Williams); `2026_06_HOU_JAX` 3594 (Parker Washington); `2026_06_PIT_TB` 2233 (Pat Freiermuth); `2026_06_NO_NYG` 270, 4164, 4468 (Chris Olave). Play 632 is Golden's touchdown catch, not a drop. |
| injuries | every row of `00-0031588` Stefon Diggs, `00-0035659` Terry McLaurin, `00-0037239` Chris Olave |
| ffverse ids | `sleeper_id` 12501, 8150, 9487, 7600, 8144, 6786, 2449, 5927 |

- [ ] **Step 1: Cut the fixtures from the real files**

Download the four files once with `download` to the scratchpad, or reuse the copies there. Write the cut files to `tests/fixtures/nflverse/`. Gzip the play-by-play and injuries cuts.

- [ ] **Step 2: Write the failing tests**

```python
def test_read_drops_golden(fixture_nflverse_dir):
    d = read_drops(fixture_nflverse_dir / "play_by_play_2026.csv.gz", fixture_nflverse_dir / "ftn_charting_2026.csv", 6)
    assert [(p.play_id, p.air_yards, p.yardline_100) for p in d["00-0040667"]] == [
        ("1332", 39.0, 43.0), ("2120", 23.0, 23.0), ("2852", 5.0, 51.0)]

def test_read_drops_without_the_week_is_none(fixture_nflverse_dir):
    assert read_drops(..., 7) is None

def test_read_injuries(fixture_nflverse_dir):
    inj = read_injuries(fixture_nflverse_dir / "injuries_2026.csv.gz", 6)
    assert inj["00-0031588"] == {5: "Out", 6: "Questionable"}
    assert inj["00-0035659"] == {4: "Questionable", 5: "Questionable"}
    assert read_injuries(fixture_nflverse_dir / "injuries_2026.csv.gz", 7) is None

def test_gsis_from_blob_strips_space(fixture_raw_dir):
    assert gsis_id("5927", load_raw(fixture_raw_dir)["players"], {}) == "00-0035659"

def test_gsis_from_id_map_for_golden(fixture_raw_dir, fixture_nflverse_dir):
    ids = read_id_map(fixture_nflverse_dir / "db_playerids.csv")
    assert gsis_id("12501", load_raw(fixture_raw_dir)["players"], ids) == "00-0040667"

def test_download_falls_back_to_a_stale_cache(tmp_path):
    path = tmp_path / "f.csv"
    path.write_text("old")
    os.utime(path, (0, 0))
    assert download("u", path, fetch=_boom) == path and path.read_text() == "old"
    assert download("u", tmp_path / "none.csv", fetch=_boom) is None

def test_nflverse_week_from_fixtures(nfl_week6):
    assert all(nfl_week6.sources.values())
    assert len(nfl_week6.drops["12501"]) == 3
    assert nfl_week6.gsis["12501"] == "00-0040667"
```

`_boom` raises `httpx.ConnectError`. `nfl_week6` passes the starters of week 6 as `player_ids`.

- [ ] **Step 3: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_nflverse.py -v`
Expected: FAIL with an import error.

- [ ] **Step 4: Write `nflverse.py` and the models**

- [ ] **Step 5: Run all tests**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add src/cornerstone/nflverse.py src/cornerstone/models.py tests/
git commit -m "Fetch and parse the nflverse drops and injury reports"
```

---

### Task 14: Drop facts and Butterfingers

**Files:**
- Create: `src/cornerstone/facts_nflverse.py`, `tests/test_facts_nflverse.py`
- Modify: `tests/conftest.py`, `src/cornerstone/models.py`, `src/cornerstone/parse.py`, `src/cornerstone/facts_league.py`, `src/cornerstone/sheet.py`, `src/cornerstone/verifier.py`, `src/cornerstone/prompts/vocabulary.md`, `src/cornerstone/prompts/writer.md`, `tests/test_verifier.py`

**Interfaces:**
- Consumes: `NflverseWeek`, `DropPlay`, `nfl_week6` from Task 13.
- Produces:
  - `Week` gains `scoring: dict[str, float] = {}` from `league.json` `scoring_settings`, and `stats: dict[str, dict[str, float]] = {}` from `stats.json`.
  - `DropLine(player_id: str, roster_id: int, matchup_id: int, drops: int, targets: int | None, value: float | None, end_zone: int | None)`.
  - `drop_value(play: DropPlay, scoring: dict[str, float]) -> float`: `rec` plus `max(air_yards, 0) * rec_yd`, plus `rec_td` when `air_yards >= yardline_100`. Sum on `Decimal`.
  - `drop_lines(week: Week, nfl: NflverseWeek | None) -> list[DropLine]`: started lines with 1 or more drops. The count comes from `nfl.drops` when it is not `None`, else from Sleeper `rec_drop` with `value` and `end_zone` `None`. `targets` is Sleeper `rec_tgt`. Order: drops, then value, both high first, then name.
  - `WeekData` gains `drops: list[DropLine] = []` and `drop_source: Literal["nflverse", "sleeper", "none"] = "none"`.
  - `Award.key` gains `"butterfingers"`. `AWARD_TITLES["butterfingers"] = "Butterfingers"`. `awards(week, mfacts, drops: list[DropLine] | None = None)` ranks it last, with `None` read as no drops,, after Overachiever, with the version 1 skip rule.
  - `build_bundle` gains `nfl: NflverseWeek | None = None`.
  - `verifier.py`: the `cost` gate markers become `(".driver", ".swing", ".dropswing")`.
  - `writer.md` rule 9, full new text: `9. State no cause or consequence, such as because, thanks to, cost, sank, or carried, unless the sentence cites a `.driver`, `.swing`, or `.dropswing` fact that supports it.`

Fact rules:

| ID | When | Text |
| --- | --- | --- |
| `D.{pid}` | each drop line | `{name} dropped {n} of {t} targets this week.`, or `{name} dropped {n} passes this week.` with no targets |
| `D.{pid}.value` | value known | `{name}'s drops were worth about {v} points by the drop value method, with {k} in the end zone.` |
| `M{mid}.dropswing` | nflverse up, losing side's started drop value at least the margin | `{team}'s starters dropped {n} passes worth about {v}, at least the margin of {m}.` |
| `W.drops` | 1 or more drop lines | `Most drops this week: {name} ({team}), {n}; {name} ({team}), {n}; {name} ({team}), {n}.` top three |
| `AW.butterfingers` | via `award_facts` | reason `{name} dropped {n} passes, the most of any started player this week, worth about {v} points by the drop value method.` The clause after "week" goes with no value. |

Attach `D.{pid}` and `D.{pid}.value` to the player's `motw` or `recap_{mid}`, to `awards` for award winners, and to `game_changer` for the Game Changer. Attach `W.drops` to `awards`.

Vocabulary lines:

```
- **drop**: a pass the FTN charting flags as a drop. With nflverse down, the count is Sleeper's `rec_drop`.
- **drop value**: an estimate. One reception at the league rate, plus the air yards at the per-yard rate, plus a touchdown when the throw reached the end zone.
- **drop swing**: the losing side's drop value is at least the margin. Only then may the writer say the drops cost the game.
- **Butterfingers**: the started player with the most drops, across all teams.
```

Writer rule 21, and the new rule 9 text above:

```
21. A drop fact names the receiver only. Never blame the quarterback for a drop. Write "worth about" for a drop value. Say drops cost the game only in a sentence that cites a `.dropswing` fact.
```

- [ ] **Step 1: Write the failing tests**

In `tests/conftest.py`, move the body of `tbundle` into a helper `_trade_bundle(raw_dir, history_root, nfl=None) -> Bundle`. `tbundle` returns `_trade_bundle(fixture_raw_dir, fixture_history_root)`. `dbundle` returns `_trade_bundle(fixture_raw_dir, fixture_history_root, nfl=nfl_week6)`. The tests that need no nflverse use `tbundle`. No second copy of the build.

```python
def test_drop_value_golden(nfl_week6, fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [drop_value(p, wk.scoring) for p in nfl_week6.drops["12501"]] == [4.4, 8.8, 1.0]

def test_negative_air_yards_count_as_zero(nfl_week6, fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [drop_value(p, wk.scoring) for p in nfl_week6.drops["8150"]] == [0.9, 0.5]

def test_drop_facts(dbundle):
    f = dbundle.sheet.facts
    assert f["D.12501"].text == "Matthew Golden dropped 3 of 13 targets this week."
    assert f["D.12501.value"].text == (
        "Matthew Golden's drops were worth about 14.2 points by the drop value method, with 1 in the end zone.")
    assert f["M4.dropswing"].text == (
        "Bo Girds's starters dropped 7 passes worth about 17.8, at least the margin of 5.34.")
    assert f["W.drops"].text == ("Most drops this week: Matthew Golden (Bo Girds), 3; "
        "Chris Olave (All You Need Is Love), 3; CeeDee Lamb (behold the lamb), 2.")

def test_butterfingers(dbundle):
    a = next(x for x in dbundle.data.awards if x.key == "butterfingers")
    assert a.line.name == "Matthew Golden" and "14.2" in dbundle.sheet.facts["AW.butterfingers"].text

def test_drops_degrade_to_sleeper_count(tbundle):   # nfl=None
    f = tbundle.sheet.facts
    assert f["D.9487"].text.startswith("Parker Washington dropped 3 ")
    assert "D.12501.value" not in f and "M4.dropswing" not in f
    assert tbundle.data.drop_source == "sleeper"

def test_stale_nflverse_week_degrades(...):
    # nflverse_week(2026, 7, ...) from the week 6 fixtures gives drops None, so drop_lines uses Sleeper.

# tests/test_verifier.py
def test_dropswing_passes_the_cost_gate(dbundle):   # "The drops cost Bo Girds the game." citing M4.dropswing
def test_drop_value_alone_fails_the_cost_gate(dbundle):   # same sentence citing D.12501.value -> "'cost' needs"
```

Run the two number tests from `test_sheet.py` on `dbundle` too.

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_facts_nflverse.py tests/test_verifier.py -v`
Expected: FAIL with an import error.

- [ ] **Step 3: Write the parse fields, `facts_nflverse.py`, the facts, the award, the gate, rule 9, and the prompt lines**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass. `test_awards_one_player_one_tile` still passes with no drops.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/ tests/
git commit -m "Add drop facts, the drop swing, and the Butterfingers award"
```

---

### Task 15: Injury history and pre-game status

**Files:**
- Modify: `src/cornerstone/facts_nflverse.py`, `src/cornerstone/sheet.py`, `src/cornerstone/prompts/vocabulary.md`, `src/cornerstone/prompts/writer.md`, `tests/test_facts_nflverse.py`, `tests/test_writer.py`

**Interfaces:**
- Consumes: `NflverseWeek.injuries`, `Week.stats`, `dbundle` from Task 14.
- Produces:
  - `injury_facts_nfl(c: Context) -> list[Fact]` in `sheet.py`, for started lines with a Sleeper id in `nfl.injuries`. None when `nfl.injuries` is `None`.
  - `I.{pid}.pregame` when the player has a status in week N: `{name} was listed {status} on the final NFL injury report before his game this week.`
  - `I.{pid}.history`, one of two forms:
    - Listed in week N: `{name} has been on the report {n} weeks.` with `n` the count of listed weeks 1 to N. Use `week` for 1.
    - Not listed in week N, listed in week N-1, and Sleeper `gp` above 0 in week N: `{name} was on the NFL injury report in {n} earlier weeks this season and plays this week.` with `n` the count of listed weeks 1 to N-1. Use `week` for 1. The fact holds one number. With no week N-1 listing or no `gp`, there is no return claim and no `history` fact.
  - Each `T{n}.{rid}.got.{pid}` and `.gave.{pid}` fact gains the `pregame` sentence when the player has one.
  - Attach the `I.` facts like the `D.` facts.

Vocabulary lines:

```
- **injury history**: the weekly NFL report status from nflverse, per week.
- **pre-game status**: the final NFL report before the game, from nflverse. A roast of a manager who started a player listed Out or Doubtful before the game cites this fact.
```

Writer rule 11, full new text:

```
11. Use no profanity. Make no joke about an injury itself or about a player's health. The `.inj.` status and `W.injured` are from after the games: never use them to say a manager started, benched, or added a player who was listed Out, Doubtful, or Questionable. Say the player 'is now listed'. A sentence that cites an `I.{pid}.pregame` fact may say the manager started a player listed Out or Doubtful before the game. Never write that a report is from Friday. The roast is the manager's choice, the trade, the add, or the roster hole next week.
```

- [ ] **Step 1: Write the failing tests**

```python
def test_pregame_fact(dbundle):
    assert dbundle.sheet.facts["I.2449.pregame"].text == (
        "Stefon Diggs was listed Questionable on the final NFL injury report before his game this week.")

def test_history_listed_this_week(dbundle):
    assert dbundle.sheet.facts["I.2449.history"].text == "Stefon Diggs has been on the report 2 weeks."

def test_history_returned_this_week(dbundle):
    assert dbundle.sheet.facts["I.5927.history"].text == (
        "Terry McLaurin was on the NFL injury report in 2 earlier weeks this season and plays this week.")
    assert "I.5927.pregame" not in dbundle.sheet.facts

def test_no_injury_facts_without_the_file(tbundle):
    assert not any(fid.startswith("I.") for fid in tbundle.sheet.facts)

def test_got_fact_carries_the_pregame_status(...):
    # nfl_week6 with injuries["12490"] = {6: "Questionable"}, built with the week 6 trades:
    assert "Bhayshul Tuten was listed Questionable on the final NFL injury report" in f["T5.12.got.12490"].text

# tests/test_writer.py: extend test_prompt_lets_the_manager_take_the_injury_joke
    assert "I.{pid}.pregame" in system and "Friday" in system and "**pre-game status**" in system
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_facts_nflverse.py tests/test_writer.py -v`
Expected: FAIL, no `I.2449.pregame`.

- [ ] **Step 3: Write the injury facts, the trade clause, the vocabulary lines, and rule 11**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/ tests/
git commit -m "Add the injury history and the pre-game status from nflverse"
```

---

### Task 16: Wire nflverse into the build and the page

**Files:**
- Modify: `src/cornerstone/pipeline.py`, `src/cornerstone/render.py`, `src/cornerstone/templates/week.html`, `src/cornerstone/static/style.css`, `tests/test_pipeline.py`, `tests/test_cli.py`, `tests/test_render.py`

**Interfaces:**
- Consumes: `nflverse_week`, `NflverseWeek`, `build_bundle(..., nfl=)` from Tasks 13 to 15.
- Produces:
  - `NflverseFetcher = Callable[[int, int, list[str], dict], NflverseWeek]` in `pipeline.py`.
  - `fetch_nflverse(repo: Path) -> NflverseFetcher`, a module-level name, so tests can patch it. It binds one cache directory, `repo/data/cache/nflverse/`, to `nflverse_week`. The three nflverse files and `db_playerids.csv` all live there.
  - `load_nflverse(raw_dir: Path) -> NflverseWeek | None` reads `raw/nflverse.json`.
  - `make_bundle(..., nflverse: NflverseFetcher | None = None)`. When `raw/nflverse.json` is present, it reads the file and calls no fetcher. When the file is absent and `nflverse` is `None`, it builds with `nfl=None`. When the file is absent, it calls the fetcher with the week's rostered player ids. It writes the file only when every one of the four sources is `True`. It never saves a degraded extract, so the next build with no file fetches again. A saved file is never fetched again, so a rebuild sees the same data. The `BuildRecord` sources gain the four nflverse keys. `run_build` passes `nflverse` through.
  - `run_rewrite` gains `nflverse: NflverseFetcher | None = None`, the same as `run_build`. It reads `raw/nflverse.json` when present. It never calls the fetcher, because a rewrite uses the saved facts. `run_rewrite(**OFFLINE)` therefore works.
  - `TILE_KEYS` gains `"butterfingers"`. The tile shows the player, the drop count, and the drop value when known. The five-tile layout at 390px is the builder's call.
  - The drop note, a `<p class="blurb note">` at the end of All Matchups:
    - `drop_source == "nflverse"`: `Drop value is an estimate: one reception at the league rate, plus the air yards at the per-yard rate, plus a touchdown when the throw reached the end zone.`
    - `drop_source == "sleeper"`: `Drops are a count only this week, from Sleeper. No value was estimated.`
    - `drop_source == "none"`: no note.
  - `OFFLINE` in `tests/test_pipeline.py` gains a fixture-backed `nflverse`. The CLI tests that build patch `pipeline.fetch_nflverse` the same way, so no test downloads a file.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_pipeline.py
def test_build_writes_the_nflverse_extract_and_sources(tmp_path, fixture_raw_dir, fixture_history_root):
    run_build(repo, 2026, 6, _fake, fetch=False, **OFFLINE)
    assert (week_dir(repo, 2026, 6) / "raw" / "nflverse.json").exists()
    sources = read_verify(week_dir(repo, 2026, 6) / "verify.json").build.sources
    assert sources == {"history": True, "nflverse_pbp": True, "nflverse_ftn": True,
                       "nflverse_injuries": True, "ffverse": True}

def test_saved_extract_is_not_fetched_again(...):
    # Second run_build with nflverse=<callable that raises AssertionError> passes.

def test_nflverse_down_still_builds(...):
    # nflverse=lambda *a: NflverseWeek(sources={k: False for k in NFLVERSE_KEYS}, gsis={}, drops=None, injuries=None)
    assert "count only this week" in page.read_text()

def test_degraded_extract_is_not_saved_and_the_next_build_fetches(...):
    # First run_build with the down fetcher above: raw/nflverse.json does not exist.
    # Second run_build with the fixture-backed fetcher: the file exists and every source is True.

def test_rewrite_takes_the_nflverse_argument(...):
    # run_build, then run_rewrite(repo, 2026, 6, "median", _fake, **OFFLINE) with nflverse=<callable that raises AssertionError>.
    # The rewrite passes and makes no fetch.

# tests/test_render.py
def test_butterfingers_tile_and_drop_note(dbundle, tmp_path):
    html = render_week(dbundle, _blurbs(dbundle), tmp_path, _fake_png).read_text()
    assert "Butterfingers" in html and "14.2" in html
    assert "Drop value is an estimate" in html
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_pipeline.py tests/test_render.py -v`
Expected: FAIL, `make_bundle()` takes no `nflverse`.

- [ ] **Step 3: Write the fetch in `make_bundle`, the `nflverse` argument of `run_rewrite`, the tile, the note, and the test fetchers**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -v`
Expected: all pass, with no network call. Check with the network off if in doubt.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/ tests/
git commit -m "Fetch the nflverse extract in the build and show the drops on the page"
```

---

### Task 17: Smoke test week 6 after parts 3 and 4

- [ ] **Step 1: Run the smoke script**

`make_bundle` keeps its `nflverse=None` default, so the Task 7 script does not fetch nflverse. First change the script. If `data/2026/week-06/raw/nflverse.json` is absent, call `fetch_nflverse(repo)` with the week's rostered player ids and the players blob, and write the extract there. Then load the file with `load_nflverse(raw_dir)`, which validates it as the Task 13 `NflverseWeek` model. Pass the extract to `make_bundle` by name: `nflverse=lambda *args: extract`.

Run: `uv run python $SCRATCH/smoke_week6.py . $SCRATCH/smoke`
Expected: the sources print five `True` values. The run downloads the nflverse files once and writes `data/2026/week-06/raw/nflverse.json`. `grep -c '"M4.dropswing"' $SCRATCH/smoke/facts.json` prints 1 or more.

- [ ] **Step 2: Check the page**

Open the page at 390px wide. Expected: five award tiles with Butterfingers last, the drop note under All Matchups, and no horizontal scroll.

- [ ] **Step 3: Run the full suite and commit any fix**

Run: `uv run pytest -v`
Expected: all pass. Leave `raw/nflverse.json` for Task 18. Commit a code fix if the run needed one.

---

## Week 6 rebuild

### Task 18: Rebuild week 6 for Brian's review

**Files:**
- Data: `data/2026/week-06/`, `data/2026/history/week-06/`, `site/2026/week-06/`, `site/index.html`

- [ ] **Step 1: Confirm the history is on disk**

Run: `uv run cornerstone history --season 2026 --through 5`
Expected: `Nothing to fetch`.

- [ ] **Step 2: Build week 6**

Run: `uv run cornerstone build --week 6 --season 2026`
Expected: the page path, and the page opens in the browser. This step calls Claude for 12 chapters.

- [ ] **Step 3: Check the build record and the fallbacks**

Read `data/2026/week-06/verify.json`. Expected: `build.sources` holds five `True` values. Read the build log for `fallback True`. A fallback is not an error, but list each one for Brian. The log also shows `no fetch time for week 6`. That is expected, because version 1 fetched the week 6 raw data, so the week 6 window ends at the build start.

- [ ] **Step 4: Commit**

```bash
git add data/2026/week-06 data/2026/history/week-06 site
git commit -m "Rebuild week 6 with the history, the trades, and the drops"
```

- [ ] **Step 5: Stop for Brian**

Tell Brian the page is ready to review, with the list of fallbacks. Do not run `cornerstone publish`. Brian runs `uv run cornerstone publish --week 6 --season 2026` after his review. A fix after the review uses `cornerstone rewrite --week 6 --season 2026 --chapter <key>`.
