# Cornerstone Weekly Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A local Python tool that pulls one NFL week from the Sleeper API, computes a fact sheet, has Claude write and verify blurbs, renders a phone-first static page, and publishes it to GitHub Pages after Brian's approval.

**Architecture:** A pipeline of six steps, each a module that reads the previous step's JSON file from `data/{season}/week-{NN}/` and writes its own. Code computes every fact. Claude only writes prose from a fact sheet with IDs, and a second Claude call plus code checks verify every sentence. Jinja2 renders into `site/` in the private source repo. `cornerstone publish` copies `site/` into a public site-only repo, which GitHub Pages serves.

**Tech Stack:** Python 3.11+, `uv`, `httpx`, `pydantic`, `anthropic`, `jinja2`, `pytest`. Plain CSS and a few lines of JavaScript. `gh` and `git` for publish. launchd for the Tuesday run.

**Spec:** `~/plans/2026-10-20-cornerstone-weekly-design.md`. Task 1 copies it into the repo at `design/specs/2026-10-20-cornerstone-weekly-design.md`. Approved mockup: `~/plans/cornerstone-weekly-mockups/phone-week6-v4.html`. Real week 6 raw data for tests: `~/plans/cornerstone-weekly-fixtures/2026/week-06/raw/`.

## Global Constraints

- League ID `1386167364424318976`, season `2026`, 12 teams, half PPR, 6 playoff teams, playoffs start week 15.
- Version 1 builds weeks 6 to 14 only. A week outside that range stops with a message.
- Every number on the page comes from code. Claude never computes.
- Every blurb sentence cites at least one fact ID. Unsupported sentences fall back to a template sentence.
- Nothing pushes to GitHub except `cornerstone publish`, which Brian runs by hand.
- Source repo `~/repos/cornerstone-fantasy-sleeper-weekly-report` is private. Site repo `~/repos/cornerstone-fantasy-sleeper-weekly-report-site` is public and holds only built HTML. Never commit source into the site repo.
- Colors: black `#141414`, red `#b8342a`, light gray `#ececec`, white `#ffffff`.
- Claude model for every call: `claude-opus-5-5`. `max_tokens=16000`. `output_config={"effort": "high"}`. Omit `thinking` so adaptive thinking runs.
- Tests never call Claude unless marked `@pytest.mark.live`. Tests may call the Sleeper API when marked `@pytest.mark.live`. Default `pytest` run skips `live`.
- No mock mode in product code. Tests use the real week 6 fixtures on disk and inject a callable for the Claude call.
- House style for prose, comments, docstrings, and commits is Simplified Technical English. Blurbs and prompt files are exempt.
- Every code file starts with a two-line docstring that says what the file does.
- Commit after every task with the attribution line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Never use `--no-verify`.

## Review Focus

1. A starter with no projection, such as an injured player, must not crash the gap math and must not win Underperformer. Test in Task 4.
2. A player on a roster but missing from the players file must render by ID with no crash. Test in Task 3.
3. A team with no custom avatar and no user avatar must get the fallback image, not a broken link. Test in Task 9.
4. A build for a week Sleeper has not scored yet, or a week 15 or later, must stop with exit code 2 and a plain message. Test in Task 6.
5. A blurb that cites a real fact ID but states a number not in that fact must fail the code check, not pass to the page. Test in Task 8.

---

### Task 1: Repository scaffold

**Files:**
- Create: `~/repos/cornerstone-fantasy-sleeper-weekly-report/pyproject.toml`, `README.md`, `CLAUDE.md`, `.gitignore`, `src/cornerstone/__init__.py`, `src/cornerstone/cli.py`, `tests/conftest.py`, `tests/test_cli.py`
- Copy: `~/plans/2026-10-20-cornerstone-weekly-design.md` to `design/specs/`, this plan to `design/plans/`, `~/plans/cornerstone-weekly-mockups/*` to `design/mockups/`, `~/plans/cornerstone-weekly-fixtures/2026/week-06/raw/*` to `tests/fixtures/2026/week-06/raw/`

**Interfaces:**
- Produces: console script `cornerstone` that runs `cornerstone.cli:main`. Fixture path helper `fixture_raw_dir() -> Path` in `tests/conftest.py` that returns `tests/fixtures/2026/week-06/raw`.

- [ ] **Step 1: Create the project with uv**

Run: `cd ~/repos && mkdir cornerstone-fantasy-sleeper-weekly-report && cd cornerstone-fantasy-sleeper-weekly-report && git init && uv init --package --python 3.11 --name cornerstone`
Then add dependencies: `uv add httpx pydantic anthropic jinja2` and `uv add --dev pytest`.
Set `[project.scripts] cornerstone = "cornerstone.cli:main"` in `pyproject.toml`. Add `[tool.pytest.ini_options]` with `markers = ["live: calls a real external API"]` and `addopts = "-m 'not live'"`.

- [ ] **Step 2: Write `CLAUDE.md`**

Content, in this order: the two names, the one-paragraph purpose, the pipeline in six lines, the rule that nothing publishes without `cornerstone publish`, the test markers, the STE house style line that points to `~/.claude/rules/communication/simplified-technical-english.md`. Names: Claude is **Truckasaurus Tina**. Brian is **Homie B-Rex**. Keep both exactly.

- [ ] **Step 3: Write `.gitignore` and `README.md`**

`.gitignore`: `.venv/`, `__pycache__/`, `data/cache/`, `.superpowers/`, `.tmp/`. Do not ignore `site/`. It is committed in the source repo as the record of what was published. `README.md`: what the site is, the public URL, the three commands `cornerstone build`, `cornerstone publish`, `cornerstone rewrite --chapter <key>`, and the Tuesday runbook in five numbered lines.

- [ ] **Step 4: Copy the design, plan, mockups, and fixtures into the repo**

Run the copies listed under Files. Confirm `tests/fixtures/2026/week-06/raw/` has 11 JSON files.

- [ ] **Step 5: Write the failing CLI test**

```python
# tests/test_cli.py
import subprocess

def test_help_lists_commands():
    out = subprocess.run(["uv", "run", "cornerstone", "--help"], capture_output=True, text=True)
    assert out.returncode == 0
    for cmd in ("build", "publish", "rewrite"):
        assert cmd in out.stdout
```

- [ ] **Step 6: Run the test to confirm it fails**

Run: `uv run pytest tests/test_cli.py -v`
Expected: FAIL, `cornerstone` has no `build` subcommand.

- [ ] **Step 7: Write `main() -> int` in `src/cornerstone/cli.py` with argparse subcommands `build`, `publish`, `rewrite`**

`build` takes `--week INT` optional and `--season INT` optional. `rewrite` takes `--week INT` optional and `--chapter STR` required. `publish` takes `--week INT` optional. Each subcommand prints "not implemented" and returns 1 for now.

- [ ] **Step 8: Run the test to confirm it passes**

Run: `uv run pytest -v`
Expected: 1 passed.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "chore: scaffold the weekly report"
```

---

### Task 2: Sleeper client with disk cache

**Files:**
- Create: `src/cornerstone/sleeper.py`, `tests/test_sleeper.py`

**Interfaces:**
- Produces:
  - `RAW_FILES: tuple[str, ...] = ("state", "league", "users", "rosters", "matchups", "matchups_next", "transactions", "projections", "stats", "players", "bracket")`
  - `fetch_week(league_id: str, season: int, week: int, raw_dir: Path, players_cache: Path) -> None` writes `raw_dir/{name}.json` for every name in `RAW_FILES`. `players.json` is read from `players_cache` when that file is less than 7 days old, else fetched and saved to both.
  - `load_raw(raw_dir: Path) -> dict[str, object]` returns the parsed JSON for every name in `RAW_FILES`, keyed by name.
  - `fetch_news(player_id: str) -> list[dict]` returns the news items or an empty list on any HTTP error.
  - `fetch_state() -> dict`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_sleeper.py
import pytest
from cornerstone.sleeper import RAW_FILES, load_raw, fetch_week, fetch_state

def test_load_raw_returns_every_file(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert set(raw) == set(RAW_FILES)
    assert raw["league"]["name"] == "Cornerstone League 2026"
    assert len(raw["matchups"]) == 12

@pytest.mark.live
def test_fetch_week_writes_every_file(tmp_path):
    fetch_week("1386167364424318976", 2026, 6, tmp_path / "raw", tmp_path / "players.json")
    assert {p.stem for p in (tmp_path / "raw").glob("*.json")} == set(RAW_FILES)

@pytest.mark.live
def test_fetch_state_has_week():
    assert "display_week" in fetch_state()
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_sleeper.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write `sleeper.py`**

Base URLs: `https://api.sleeper.app/v1` for official, `https://api.sleeper.app` for projections, stats, and news. Endpoints are the table in the spec under Data. Projections and stats take `?season_type=regular&position[]=QB&position[]=RB&position[]=WR&position[]=TE&position[]=DEF&position[]=K`. `matchups_next` is `matchups/{week+1}`. Use one `httpx.Client` with a 30 second timeout. Projections, stats, and news are unofficial. On an HTTP error for those three, write an empty list and log a warning. On an HTTP error for an official endpoint, raise.

- [ ] **Step 4: Run all tests, then the live tests once**

Run: `uv run pytest -v` then `uv run pytest -m live -v`
Expected: all pass. The live run writes 11 files.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/sleeper.py tests/test_sleeper.py
git commit -m "feat: fetch and cache one week of Sleeper data"
```

---

### Task 3: Domain models and raw parsing

**Files:**
- Create: `src/cornerstone/models.py`, `src/cornerstone/parse.py`, `tests/test_parse.py`

**Interfaces:**
- Produces, all pydantic `BaseModel` in `models.py`:
  - `Team(roster_id: int, name: str, owner: str, avatar_url: str | None, wins: int, losses: int, points_for: float, is_brian: bool)`
  - `PlayerLine(player_id: str, name: str, position: str, nfl_team: str | None, points: float, projection: float | None, season_avg: float | None, started: bool, slot: str | None)`
  - `Side(roster_id: int, points: float, lines: list[PlayerLine])`
  - `Matchup(matchup_id: int, a: Side, b: Side)`
  - `Move(player_id: str, roster_id: int, kind: Literal["waiver", "free_agent", "trade"], week: int, bid: int | None)`
  - `Week(season: int, week: int, teams: dict[int, Team], matchups: list[Matchup], next_matchups: list[tuple[int, int]], moves: list[Move], last_scored_week: int, season_start: date)`
- `parse_week(raw: dict[str, object], brian_user: str = "bkwon") -> Week` in `parse.py`.
- Name fallback: a player ID with no entry in `players` gets `name=player_id`, `position="?"`.
- `season_avg` is `None` in version 1. Task 5 fills it from season history when the backfill lands. Keep the field.
- Avatar rule: `metadata.avatar` if set, else `https://sleepercdn.com/avatars/thumbs/{avatar}` if the user has an `avatar`, else `None`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_parse.py
from cornerstone.sleeper import load_raw
from cornerstone.parse import parse_week

def test_parse_week_teams_and_matchups(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert wk.week == 6 and wk.last_scored_week == 6
    assert len(wk.teams) == 12 and len(wk.matchups) == 6
    bo = next(t for t in wk.teams.values() if t.name == "Bo Girds")
    assert bo.is_brian and (bo.wins, bo.losses) == (8, 4)
    assert bo.avatar_url.endswith(".jpg")
    lamb = next(t for t in wk.teams.values() if t.name == "behold the lamb")
    assert lamb.avatar_url.startswith("https://sleepercdn.com/avatars/thumbs/")

def test_parse_week_lines_have_projection(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    m = next(m for m in wk.matchups if m.matchup_id == 4)
    shough = next(l for s in (m.a, m.b) for l in s.lines if l.name == "Tyler Shough")
    assert shough.started and shough.points == 26.96 and shough.projection == 17.06

def test_unknown_player_falls_back_to_id(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    raw["players"].pop("8183")  # Brock Purdy
    wk = parse_week(raw)
    names = {l.name for m in wk.matchups for s in (m.a, m.b) for l in s.lines}
    assert "8183" in names
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_parse.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write `models.py` and `parse.py`**

`parse_week` builds the projection map from `projections` by `player_id` to `stats.pts_half_ppr`. A starter is a player in the matchup's `starters` list. `slot` comes from the index into `league.roster_positions`. Moves come from `transactions` with `status == "complete"`, one `Move` per entry in `adds`, `week` from `leg`, `bid` from `settings.waiver_bid`. `next_matchups` pairs `roster_id`s from `matchups_next` by `matchup_id`. `season_start` from `state.season_start_date`.

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/models.py src/cornerstone/parse.py tests/test_parse.py
git commit -m "feat: parse raw Sleeper data into domain models"
```

---

### Task 4: Matchup facts and the median game

**Files:**
- Create: `src/cornerstone/facts_matchup.py`, `tests/test_facts_matchup.py`

**Interfaces:**
- Produces, in `models.py` (add):
  - `MatchupFacts(matchup_id: int, winner: int | None, loser: int | None, score_w: float, score_l: float, margin: float, top_scorer: dict[int, PlayerLine], drivers: list[PlayerLine], swing: list[PlayerLine], bench_regret: list[tuple[PlayerLine, PlayerLine]], recent_moves: list[Move])`
  - `MedianFacts(median: float, above: list[int], below: list[int], closest_above: tuple[int, float], closest_below: tuple[int, float])`
- `matchup_facts(m: Matchup, moves: list[Move], week: int) -> MatchupFacts`
- `median_facts(week: Week) -> MedianFacts`
- Rules: `winner is None` on a tie. `drivers` are lines on either side with `projection is not None` and `abs(points - projection) >= margin`. `swing` are started lines on the winning side with `points > margin`. `bench_regret` pairs a bench line with the lowest started line at the same position when the swap would flip the result. `recent_moves` are moves for a started player on either side with `week in (week, week - 1)`. Lines with `projection is None` never enter `drivers`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_facts_matchup.py
from cornerstone.sleeper import load_raw
from cornerstone.parse import parse_week
from cornerstone.facts_matchup import matchup_facts, median_facts

def _wk(d): return parse_week(load_raw(d))

def test_closest_matchup_facts(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    m = next(m for m in wk.matchups if m.matchup_id == 4)
    f = matchup_facts(m, wk.moves, 6)
    assert wk.teams[f.winner].name == "behold the lamb"
    assert (f.score_w, f.score_l, f.margin) == (114.95, 109.61, 5.34)
    bo = next(r for r in f.top_scorer if wk.teams[r].name == "Bo Girds")
    assert f.top_scorer[bo].name == "Tyler Shough"
    assert "Kyren Williams" in {l.name for l in f.drivers}

def test_blowout_top_scorer_is_purdy_not_defense(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    m = next(m for m in wk.matchups if m.matchup_id == 1)
    f = matchup_facts(m, wk.moves, 6)
    brock = next(r for r in f.top_scorer if wk.teams[r].name == "Brock ‘N’ Roll")
    assert f.top_scorer[brock].name == "Brock Purdy"

def test_no_projection_never_drives(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    for m in wk.matchups:
        f = matchup_facts(m, wk.moves, 6)
        assert all(l.projection is not None for l in f.drivers)

def test_median(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    med = median_facts(wk)
    assert round(med.median, 2) == 106.83 and len(med.above) == 6
    assert wk.teams[med.closest_above[0]].name == "Bo Girds"
    assert round(med.closest_above[1], 2) == 2.79
    assert wk.teams[med.closest_below[0]].name == "Amon-Ra Dawg Your Team"
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_facts_matchup.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write `facts_matchup.py` and add the two models**

Median is the mean of the 6th and 7th scores sorted descending. `above` is every roster with `points > median`.

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/models.py src/cornerstone/facts_matchup.py tests/test_facts_matchup.py
git commit -m "feat: compute matchup and median facts"
```

---

### Task 5: League facts, awards, picks, next week

**Files:**
- Create: `src/cornerstone/facts_league.py`, `tests/test_facts_league.py`

**Interfaces:**
- Produces, in `models.py` (add):
  - `Standing(rank: int, roster_id: int, wins: int, losses: int, points_for: float, in_playoffs: bool, games_from_cut: int, schedule_strength: float | None, strength_rank: int | None)`
  - `Award(key: Literal["game_changer", "top_scorer", "mvb", "underperformer", "overachiever"], line: PlayerLine, roster_id: int, matchup_id: int, reason: str, skipped: list[str])`
  - `Pick(matchup_id: int, reason: Literal["Closest Finish", "Upset", "Top of the Table", "Playoff Stakes"], scores: dict[str, float])`
  - `NextMatchup(a: int, b: int, must_watch: bool, reason: str | None)`
  - `SeasonHistory(roster_id: int, high: float, low: float, weeks_over: dict[int, int], new_high: bool, new_low: bool)` with `weeks_over` keyed by 100, 110, 120. In version 1, history covers only the current week. The backfill extends it.
  - `PositionRank(player_id: str, position: str, rank: int, of: int)`
- Functions:
  - `standings(week: Week) -> list[Standing]` sorted by wins desc, then points_for desc. `in_playoffs` is rank 6 or better. `games_from_cut` is wins minus the sixth-place wins. `schedule_strength` is the mean win rate of the remaining opponents through week 14 from `next_matchups` only in version 1, so it is one opponent. Keep the field and the rank.
  - `awards(week: Week, mfacts: list[MatchupFacts]) -> list[Award]` in the order game_changer, top_scorer, mvb, underperformer, overachiever. Each pick skips players already picked and records the skipped names. Underperformer requires `projection >= 10`. When no started line has a projection, the projections feed is down. Then `awards` omits `underperformer` and `overachiever`, and Game Changer ranks by points instead of gap. Game Changer candidates are `swing` lines of every matchup, ranked by `points - projection` with `+5` when the player is in `recent_moves`. `reason` is one plain sentence with the numbers.
  - `matchup_of_the_week(week: Week, mfacts: list[MatchupFacts], table: list[Standing]) -> Pick`. Four signals each scaled 0 to 1: closeness `1 - margin / max_margin`, upset `(loser_rank_before - winner_rank_before) / 11` clipped at 0, table `1 - (rank_a + rank_b - 3) / 22`, stakes `1` if either team is within one game of the cut else `0`. Weights 0.4, 0.25, 0.2, 0.15. Ties go to smallest margin. `reason` is the signal with the highest weighted contribution.
  - `next_week(week: Week, table: list[Standing]) -> list[NextMatchup]`. Must Watch is the top two by the same table and stakes signals. `reason` names the ranks, like "3rd vs 5th, loser falls to the cut".
  - `position_ranks(week: Week) -> list[PositionRank]` over started lines only.
  - `season_history(week: Week) -> list[SeasonHistory]`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_facts_league.py
from cornerstone.sleeper import load_raw
from cornerstone.parse import parse_week
from cornerstone.facts_matchup import matchup_facts
from cornerstone.facts_league import standings, awards, matchup_of_the_week, next_week, position_ranks

def _setup(d):
    wk = parse_week(load_raw(d))
    mf = [matchup_facts(m, wk.moves, 6) for m in wk.matchups]
    return wk, mf

def test_standings_order_and_cut(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    t = standings(wk)
    names = [wk.teams[s.roster_id].name for s in t]
    assert names[:3] == ["Lil Fridge", "London Cooking", "Bo Girds"]
    assert names[-1] == "Pukancun on 3"
    assert [s.in_playoffs for s in t].count(True) == 6

def test_awards_one_player_one_tile(fixture_raw_dir):
    wk, mf = _setup(fixture_raw_dir)
    a = {x.key: x for x in awards(wk, mf)}
    assert a["top_scorer"].line.name == "Trevor Lawrence"
    assert a["mvb"].line.name == "Jayden Daniels"
    assert a["underperformer"].line.name == "Bijan Robinson"
    assert a["game_changer"].line.name == "Tre Tucker"
    assert "Tre Tucker" in a["overachiever"].skipped
    assert a["overachiever"].line.name == "Bhayshul Tuten"
    assert len({x.line.player_id for x in a.values()}) == 5

def test_motw_is_closest(fixture_raw_dir):
    wk, mf = _setup(fixture_raw_dir)
    pick = matchup_of_the_week(wk, mf, standings(wk))
    assert pick.matchup_id == 4 and pick.reason == "Closest Finish"

def test_next_week_two_must_watch(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    nx = next_week(wk, standings(wk))
    assert len(nx) == 6 and sum(n.must_watch for n in nx) == 2

def test_position_ranks(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    tucker = next(r for r in position_ranks(wk) if r.player_id == "10213")
    assert (tucker.position, tucker.rank) == ("WR", 1)
    nabers = next(r for r in position_ranks(wk) if r.player_id == "11632")
    assert nabers.rank == 2
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_facts_league.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write `facts_league.py` and add the models**

"Rank before" for the upset signal uses standings computed from `wins - 1 if won this week` and `losses - 1 if lost this week` for the two teams in the matchup, points_for minus this week's score. Version 1 approximates this way because past weeks are not on disk.

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/models.py src/cornerstone/facts_league.py tests/test_facts_league.py
git commit -m "feat: standings, awards, matchup of the week, next week"
```

---

### Task 6: Fact sheet assembly and the gate checks

**Files:**
- Create: `src/cornerstone/sheet.py`, `tests/test_sheet.py`

**Interfaces:**
- Produces, in `models.py` (add):
  - `Fact(id: str, text: str, numbers: list[str], teams: list[str], players: list[str])`
  - `Chapter(key: str, title: str, fact_ids: list[str], scope_teams: list[str], scope_players: list[str], min_sentences: int, max_sentences: int)`
  - `WeekData(season: int, week: int, dates: str, publish_date: str, teams: dict[int, Team], matchups: list[MatchupFacts], median: MedianFacts, table: list[Standing], awards: list[Award], pick: Pick, next: list[NextMatchup], history: list[SeasonHistory], ranks: list[PositionRank])`
  - `FactSheet(facts: dict[str, Fact], chapters: list[Chapter])`
  - `Bundle(data: WeekData, sheet: FactSheet)`
- `build_bundle(week: Week) -> Bundle`
- `write_bundle(b: Bundle, path: Path) -> None` and `read_bundle(path: Path) -> Bundle`
- `check_week_is_buildable(week_target: int, last_scored: int) -> str | None` returns a message when the week cannot build, else `None`. Messages: `"Sleeper has scored through week {last_scored}. Week {week_target} is not final."` and `"Week {week_target} is a playoff week. Version 1 covers weeks 6 to 14."`
- `week_dates(season_start: date, week: int) -> str` returns `"Oct 15 – Oct 19, 2026"` for week 6. Thursday is `season_start + 1 day + 7 * (week - 1)`. Monday is Thursday + 4.
- Fact ID scheme: `W.*` week-level, `S.{rank}` standings, `MED.*` median, `M{matchup_id}.*` matchup, `AW.{key}` awards, `PICK`, `NX.{a}v{b}`, `HIST.{roster_id}`, `RANK.{player_id}`, `SOS.{roster_id}`. Every fact `text` is one plain sentence with the numbers written as they should appear on the page. `numbers` holds every number in `text` as a string.
- Chapter keys: `motw`, `game_changer`, `awards`, `recap_{matchup_id}` for all six, `median`, `next_week`. Sentence ranges from the spec: motw 4 to 6, game_changer 3 to 5, awards 2 to 4, recap 2 to 3, median 2 to 4, next_week 1 to 2.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_sheet.py
from datetime import date
from cornerstone.sleeper import load_raw
from cornerstone.parse import parse_week
from cornerstone.sheet import build_bundle, write_bundle, read_bundle, check_week_is_buildable, week_dates

def test_week_dates():
    assert week_dates(date(2026, 9, 9), 6) == "Oct 15 – Oct 19, 2026"

def test_gate_messages():
    assert check_week_is_buildable(6, 6) is None
    assert "not final" in check_week_is_buildable(7, 6)
    assert "playoff" in check_week_is_buildable(15, 15)

def test_bundle_roundtrip_and_ids(fixture_raw_dir, tmp_path):
    b = build_bundle(parse_week(load_raw(fixture_raw_dir)))
    assert b.data.dates == "Oct 15 – Oct 19, 2026"
    assert {c.key for c in b.sheet.chapters} >= {"motw", "game_changer", "awards", "median", "next_week", "recap_4"}
    motw = next(c for c in b.sheet.chapters if c.key == "motw")
    assert all(fid in b.sheet.facts for fid in motw.fact_ids)
    assert set(motw.scope_teams) == {"behold the lamb", "Bo Girds"}
    f = b.sheet.facts["MED.value"]
    assert "106.83" in f.text and "106.83" in f.numbers
    write_bundle(b, tmp_path / "facts.json")
    assert read_bundle(tmp_path / "facts.json").data.week == 6
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_sheet.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write `sheet.py` and add the models**

Every chapter's `scope_players` is every player on the teams in `scope_teams`, by full name. League-wide chapters scope all teams. `build_bundle` calls `fetch_news` for the Game Changer only and adds fact `AW.game_changer.news` with the newest item's description cut to 300 characters, when any item exists. Tests run with the real endpoint, and an empty list is a pass. `publish_date` is today in `"Tue Oct 20, 2026"` form.

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/models.py src/cornerstone/sheet.py tests/test_sheet.py
git commit -m "feat: assemble the fact sheet and gate the build"
```

---

### Task 7: Writer

**Files:**
- Create: `src/cornerstone/writer.py`, `src/cornerstone/prompts/vocabulary.md`, `src/cornerstone/prompts/tone.md`, `src/cornerstone/prompts/writer.md`, `tests/test_writer.py`

**Interfaces:**
- Produces, in `models.py` (add):
  - `Sentence(text: str, fact_ids: list[str])`
  - `Blurb(chapter: str, sentences: list[Sentence], attempt: int, fallback: bool)`
- `ClaudeCall = Callable[[str, str, type[BaseModel]], BaseModel]` where the arguments are `(system, user, output_model)`.
- `claude_call(system: str, user: str, output_model: type[BaseModel]) -> BaseModel` in `writer.py`: uses `anthropic.Anthropic().messages.parse(model="claude-opus-5-5", max_tokens=16000, system=system, messages=[{"role": "user", "content": user}], output_format=output_model, output_config={"effort": "high"})` and returns `response.parsed_output`. When `response.stop_reason == "refusal"`, raise `RefusalError`.
- `build_writer_prompt(chapter: Chapter, sheet: FactSheet, feedback: str | None) -> tuple[str, str]` returns `(system, user)`. System is `vocabulary.md` + `tone.md` + `writer.md`. User is the chapter title, the sentence range, every fact in scope as one line `- {id}: {text}`, and the feedback block when present.
- `write_blurb(chapter: Chapter, sheet: FactSheet, call: ClaudeCall, feedback: str | None = None) -> Blurb`.
- `template_blurb(chapter: Chapter, sheet: FactSheet) -> Blurb` returns the first fact's text as one sentence with `fallback=True`.
- Prompt files are exempt from STE. `writer.md` must state: cite one or more fact IDs per sentence, use only numbers that appear in cited facts, use only the vocabulary terms, name teams by team name, never say "decided" or "decider" unless a cited fact ID contains `.driver`, no profanity, no jokes about injuries.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_writer.py
from cornerstone.models import Sentence, Blurb
from cornerstone.sleeper import load_raw
from cornerstone.parse import parse_week
from cornerstone.sheet import build_bundle
from cornerstone.writer import build_writer_prompt, write_blurb, template_blurb

def _sheet(d): return build_bundle(parse_week(load_raw(d))).sheet

def test_prompt_contains_scope_facts_only(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = next(c for c in sheet.chapters if c.key == "recap_4")
    system, user = build_writer_prompt(ch, sheet, None)
    assert "Read recap" not in user
    assert "M4." in user and "M1." not in user
    assert "fact ID" in system

def test_write_blurb_uses_call(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = next(c for c in sheet.chapters if c.key == "median")
    def fake(system, user, model):
        return model(sentences=[Sentence(text="Six teams cleared 106.83.", fact_ids=["MED.value"])])
    b = write_blurb(ch, sheet, fake)
    assert b.chapter == "median" and b.sentences[0].fact_ids == ["MED.value"] and not b.fallback

def test_template_blurb(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = next(c for c in sheet.chapters if c.key == "recap_4")
    b = template_blurb(ch, sheet)
    assert b.fallback and len(b.sentences) == 1
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_writer.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write the three prompt files and `writer.py`**

`vocabulary.md` lists the defined terms from the spec's fact sheet section with one line each: Top Scorer, MVB, Underperformer, Overachiever, Game Changer, Matchup of the Week, margin driver, swing player, bench regret, median game, Must Watch, schedule strength, season high, season low, position rank. It bans: best, star, carried, hero, MVP, clutch, exploded, cooked. `tone.md` is the spec's Tone paragraph plus three example sentences from the approved mockup that passed review and the two that failed, labeled.

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Add one live test and run it once**

```python
@pytest.mark.live
def test_live_write_median(fixture_raw_dir):
    from cornerstone.writer import claude_call
    sheet = _sheet(fixture_raw_dir)
    ch = next(c for c in sheet.chapters if c.key == "median")
    b = write_blurb(ch, sheet, claude_call)
    assert 2 <= len(b.sentences) <= 4 and all(s.fact_ids for s in b.sentences)
```

Run: `uv run pytest -m live tests/test_writer.py -v`
Expected: PASS. Print the sentences in the test output for Brian to read later.

- [ ] **Step 6: Commit**

```bash
git add src/cornerstone/writer.py src/cornerstone/prompts tests/test_writer.py
git commit -m "feat: Claude writer with fact citations"
```

---

### Task 8: Verifier and the retry loop

**Files:**
- Create: `src/cornerstone/verifier.py`, `src/cornerstone/prompts/verifier.md`, `tests/test_verifier.py`

**Interfaces:**
- Produces, in `models.py` (add):
  - `Verdict(index: int, supported: bool, reason: str)`
  - `VerifyOut(verdicts: list[Verdict])`
  - `VerifyResult(chapter: str, code_failures: list[str], verdicts: list[Verdict], passed: bool)`
- `code_check(blurb: Blurb, chapter: Chapter, sheet: FactSheet) -> list[str]` returns one message per failure. Checks, in order: every `fact_id` exists in `sheet.facts` and in `chapter.fact_ids`; every digit number in a sentence appears in the `numbers` of its cited facts, with the week number and next week number always allowed; every league team name that appears in a sentence is in `chapter.scope_teams`; every player full name or last name that matches a league player is in `chapter.scope_players`; no banned word from `vocabulary.md`; "decided" or "decider" appears only when a cited ID contains `.driver`; sentence count is within the chapter's range.
- `build_verifier_prompt(blurb: Blurb, chapter: Chapter, sheet: FactSheet) -> tuple[str, str]`.
- `claude_verify(blurb: Blurb, chapter: Chapter, sheet: FactSheet, call: ClaudeCall) -> list[Verdict]`.
- `verify_blurb(blurb: Blurb, chapter: Chapter, sheet: FactSheet, call: ClaudeCall) -> VerifyResult`.
- `write_and_verify(chapter: Chapter, sheet: FactSheet, call: ClaudeCall) -> tuple[Blurb, list[VerifyResult]]`: write, verify, on failure write again once with feedback built from the failures, verify again, on a second failure return `template_blurb`. Returns the final blurb and every result.
- Numbers are compared as strings after a normalize: strip a trailing `.0`, strip thousands separators.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_verifier.py
from cornerstone.models import Sentence, Blurb, VerifyOut, Verdict
from cornerstone.sleeper import load_raw
from cornerstone.parse import parse_week
from cornerstone.sheet import build_bundle
from cornerstone.verifier import code_check, write_and_verify

def _sheet(d): return build_bundle(parse_week(load_raw(d))).sheet
def _ch(sheet, key): return next(c for c in sheet.chapters if c.key == key)

def test_number_not_in_fact_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir); ch = _ch(sheet, "median")
    b = Blurb(chapter="median", attempt=1, fallback=False,
              sentences=[Sentence(text="Six teams cleared 109.83.", fact_ids=["MED.value"])])
    assert any("109.83" in m for m in code_check(b, ch, sheet))

def test_out_of_scope_player_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir); ch = _ch(sheet, "recap_4")
    fid = ch.fact_ids[0]
    b = Blurb(chapter="recap_4", attempt=1, fallback=False,
              sentences=[Sentence(text="Tre Tucker had nothing to do with this.", fact_ids=[fid])])
    assert any("Tre Tucker" in m for m in code_check(b, ch, sheet))

def test_decided_needs_driver(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir); ch = _ch(sheet, "recap_4")
    non_driver = next(f for f in ch.fact_ids if ".driver" not in f)
    b = Blurb(chapter="recap_4", attempt=1, fallback=False,
              sentences=[Sentence(text="A game decided by a quarterback.", fact_ids=[non_driver])])
    assert any("decided" in m for m in code_check(b, ch, sheet))

def test_two_failures_fall_back(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir); ch = _ch(sheet, "median")
    calls = []
    def fake(system, user, model):
        calls.append(model.__name__)
        if model.__name__ == "VerifyOut":
            return VerifyOut(verdicts=[Verdict(index=0, supported=False, reason="not in facts")])
        return model(sentences=[Sentence(text="Six teams cleared 106.83.", fact_ids=["MED.value"])] * 2)
    blurb, results = write_and_verify(ch, sheet, fake)
    assert blurb.fallback and len(results) == 2 and calls.count("VerifyOut") == 2
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_verifier.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write `verifier.md` and `verifier.py`**

`verifier.md` says: you are a fact checker, you have no stake in the tone, mark each sentence supported only when every claim in it follows from the cited facts, treat a cause claim as unsupported unless a cited fact states that cause, return one verdict per sentence in order.

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/verifier.py src/cornerstone/prompts/verifier.md tests/test_verifier.py
git commit -m "feat: verify blurbs in code and with Claude, fall back on failure"
```

---

### Task 9: Render the week page and the home page

**Files:**
- Create: `src/cornerstone/render.py`, `src/cornerstone/templates/base.html`, `src/cornerstone/templates/week.html`, `src/cornerstone/templates/index.html`, `src/cornerstone/static/style.css`, `src/cornerstone/static/app.js`, `src/cornerstone/static/logo.png`, `src/cornerstone/static/avatar-default.svg`, `tests/test_render.py`

**Interfaces:**
- `render_week(bundle: Bundle, blurbs: dict[str, Blurb], site_dir: Path) -> Path` writes `site_dir/{season}/week-{NN}/index.html`, copies `static/*` to `site_dir/static/`, downloads each team avatar to `site_dir/{season}/week-{NN}/avatars/{roster_id}.{ext}`, where `ext` is the URL's file extension or `jpg` when it has none, with `static/avatar-default.svg` as the fallback when `avatar_url` is `None` or the download fails, and returns the page path.
- `render_index(site_dir: Path) -> Path` scans `site_dir/{season}/week-*/index.html`, reads a `<meta name="cornerstone-summary" content="...">` tag from each, and writes `site_dir/index.html` newest first.
- `week.html` follows `design/mockups/phone-week6-v4.html` chapter by chapter. Max content width 480px, centered. Blurb sentences join with a space. Avatars render as 28px circles before team names in Matchup of the Week, All Matchups, Standings, and Next Week. Brian's row in Standings gets class `me`. When an award key is absent, its tile reads "Projections unavailable this week". The meta summary tag holds `"Week {N} · {dates} · {team A} vs {team B}"`.
- `app.js` holds only the Read recap toggle: a click on `.recap-btn` toggles `.open` on its parent `.mu`.
- `base.html` sets `<title>`, the viewport meta, and links `static/style.css` and `static/app.js` with paths relative to the site root.

- [ ] **Step 1: Copy the logo and write the default avatar**

Run: `cp design/mockups/logo.png src/cornerstone/static/logo.png`. Write `src/cornerstone/static/avatar-default.svg` by hand: a 64 by 64 SVG with one `#ececec` circle.

- [ ] **Step 2: Write the failing tests**

```python
# tests/test_render.py
from cornerstone.models import Sentence, Blurb
from cornerstone.sleeper import load_raw
from cornerstone.parse import parse_week
from cornerstone.sheet import build_bundle
from cornerstone.render import render_week, render_index

def _bundle(d): return build_bundle(parse_week(load_raw(d)))

def _blurbs(bundle):
    return {c.key: Blurb(chapter=c.key, attempt=1, fallback=False,
            sentences=[Sentence(text=f"Blurb for {c.key}.", fact_ids=c.fact_ids[:1])])
            for c in bundle.sheet.chapters}

def test_render_week_has_every_chapter(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    page = render_week(b, _blurbs(b), tmp_path)
    html = page.read_text()
    for s in ("WEEK", "Matchup of the Week", "Game Changer", "Top Scorer", "MVB", "Read recap",
              "The Median Game", "Standings", "Next Week", "Oct 15 – Oct 19, 2026", "Bo Girds"):
        assert s in html
    assert html.count("Read recap") == 6
    assert (tmp_path / "static" / "style.css").exists()

def test_missing_avatar_uses_default(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    for t in b.data.teams.values():
        t.avatar_url = None
    page = render_week(b, _blurbs(b), tmp_path)
    assert "avatar-default.svg" in page.read_text()

def test_index_lists_week(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    render_week(b, _blurbs(b), tmp_path)
    idx = render_index(tmp_path).read_text()
    assert "Week 6" in idx and "2026/week-06/" in idx
```

- [ ] **Step 3: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_render.py -v`
Expected: FAIL, import error.

- [ ] **Step 4: Write the templates, the CSS, the JS, and `render.py`**

Port the CSS from the mockup's `.ph` rules into `style.css` without the phone frame. Keep the names `.mast`, `.chap`, `.dark`, `.lbl`, `.tag`, `.score`, `.blurb`, `.tiles`, `.tile`, `.mu`, `.cta`, `.body`, `.inner`, `.stars`, `.med`, `.kpi`, `.st`, `.nx`, `.foot`. Add `.avatar` for the 28px circle. Avatars download with `httpx` and a 10 second timeout. In tests the download runs against the real CDN. That is accepted. A failed download writes the default.

- [ ] **Step 5: Run the tests to confirm they pass**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 6: Open the rendered page and compare it with the mockup**

Run: `uv run python -c "..."` is not needed. Run: `uv run pytest tests/test_render.py -k every_chapter --basetemp=.tmp` then `open .tmp/test_render_week_has_every_chapter0/2026/week-06/index.html`.
Expected: the page reads like the mockup at phone width. Fix spacing or color by eye before the commit. Delete `.tmp/` after.

- [ ] **Step 7: Commit**

```bash
git add src/cornerstone/render.py src/cornerstone/templates src/cornerstone/static tests/test_render.py
git commit -m "feat: render the week page and the home page"
```

---

### Task 10: CLI pipeline, preview, rewrite, publish

**Files:**
- Create: `src/cornerstone/pipeline.py`, `src/cornerstone/publish.py`, `tests/test_pipeline.py`
- Modify: `src/cornerstone/cli.py`

**Interfaces:**
- `pipeline.py`:
  - `week_dir(repo: Path, season: int, week: int) -> Path` returns `repo/data/{season}/week-{NN}`.
  - `resolve_week(season: int | None, week: int | None) -> tuple[int, int]` reads `fetch_state()` when either is `None`. Week defaults to `display_week`.
  - `run_build(repo: Path, season: int, week: int, call: ClaudeCall, fetch: bool = True) -> Path` runs fetch with `players_cache = repo / "data" / "cache" / "players.json"`, parse, bundle, gate, write and verify every chapter, render week and index, and returns the page path. Writes `facts.json`, `blurbs.json`, `verify.json` in `week_dir`. When `fetch` is `False`, reads `raw/` from disk. Raises `BuildStopped(message)` when the gate returns a message.
  - `run_rewrite(repo: Path, season: int, week: int, chapter: str, call: ClaudeCall) -> Path` reads `facts.json` and `blurbs.json`, rewrites one chapter, writes `blurbs.json` and `verify.json`, re-renders, and returns the page path.
  - `preview(page: Path) -> None` runs `open <page>` and `osascript -e 'display notification "Week N is ready to review" with title "Cornerstone Weekly"'`.
- `publish.py`:
  - `SITE_REPO = Path.home() / "repos" / "cornerstone-fantasy-sleeper-weekly-report-site"` and `SITE_URL = "https://bkwon94.github.io/cornerstone-fantasy-sleeper-weekly-report-site/"`.
  - `run_publish(repo: Path, season: int, week: int, site_repo: Path = SITE_REPO) -> str` does, in order: check `repo/site/{season}/week-{NN}/index.html` exists; in the source repo run `git add site data` and `git commit -m "Week {N} report"`; copy every file under `repo/site/` into `site_repo/` with `shutil.copytree(dirs_exist_ok=True)`; in `site_repo` run `git add -A`, `git commit -m "Week {N}"`, `git push`; return `SITE_URL + f"{season}/week-{NN}/"`. Raises `PublishError` when the page is missing, when `site_repo` is not a git checkout, or when any git command exits non-zero. A source-repo commit with nothing to commit is not an error.
  - Add a test with two `tmp_path` git repos: init both, build from fixtures into the first, call `run_publish` with `site_repo` set to the second and `git push` skipped through a `push: bool = True` flag, then assert the second repo's `HEAD` commit contains `2026/week-06/index.html` and no `src/` directory.
- `cli.py`: `build` calls `resolve_week`, `run_build` with `claude_call`, then `preview`, and prints the page path. Exit 2 with the message on `BuildStopped`. `rewrite` calls `run_rewrite` then `preview`. `publish` prints a one-line confirm prompt `"Publish week {N} to GitHub Pages? [y/N] "` and runs `run_publish` only on `y`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_pipeline.py
import shutil, json, re
import pytest
from cornerstone.models import Sentence, VerifyOut, Verdict
from cornerstone.pipeline import run_build, run_rewrite, week_dir, BuildStopped

def _fake(system, user, model):
    if model.__name__ == "VerifyOut":
        return VerifyOut(verdicts=[Verdict(index=0, supported=True, reason="ok")])
    fid = re.search(r"^- ([A-Z][\w.]*): ", user, re.M).group(1)
    return model(sentences=[Sentence(text="Fact sentence.", fact_ids=[fid])] * 2)

def _repo(tmp_path, fixture_raw_dir):
    raw = week_dir(tmp_path, 2026, 6) / "raw"
    shutil.copytree(fixture_raw_dir, raw)
    return tmp_path

def test_build_from_disk_writes_everything(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    page = run_build(repo, 2026, 6, _fake, fetch=False)
    assert page == repo / "site" / "2026" / "week-06" / "index.html"
    for f in ("facts.json", "blurbs.json", "verify.json"):
        assert (week_dir(repo, 2026, 6) / f).exists()
    assert (repo / "site" / "index.html").exists()

def test_build_stops_on_unscored_week(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    shutil.copytree(week_dir(repo, 2026, 6) / "raw", week_dir(repo, 2026, 7) / "raw")
    with pytest.raises(BuildStopped):
        run_build(repo, 2026, 7, _fake, fetch=False)

def test_rewrite_one_chapter(tmp_path, fixture_raw_dir):
    repo = _repo(tmp_path, fixture_raw_dir)
    run_build(repo, 2026, 6, _fake, fetch=False)
    before = json.loads((week_dir(repo, 2026, 6) / "blurbs.json").read_text())
    run_rewrite(repo, 2026, 6, "median", _fake)
    after = json.loads((week_dir(repo, 2026, 6) / "blurbs.json").read_text())
    assert set(before) == set(after)
```

The `_fake` writer reads a real fact ID from the `- {id}: {text}` lines that Task 7 pins in the user prompt. Two sentences keep every chapter inside its sentence range.

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_pipeline.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write `pipeline.py`, `publish.py`, and wire `cli.py`**

`run_build` with `fetch=False` and no `raw/` on disk raises `BuildStopped("No raw data for week N. Run without --no-fetch.")`. Add `--no-fetch` to the `build` subcommand.

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `uv run pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/pipeline.py src/cornerstone/publish.py src/cornerstone/cli.py tests/test_pipeline.py
git commit -m "feat: build, rewrite, preview, and publish commands"
```

---

### Task 11: GitHub repo, Pages, launchd, and the first live build

**Files:**
- Create: `bin/cornerstone-build`, `launchagents/com.briankwon.cornerstone-weekly.plist`
- Modify: `README.md`

**Interfaces:**
- `bin/cornerstone-build` is a bash wrapper for launchd: `set -euo pipefail`, `source "$HOME/.secrets"`, `export PATH="$HOME/.local/bin:$PATH"`, `cd ~/repos/cornerstone-weekly`, log to `~/Library/Logs/cornerstone-weekly/build.log` with a timestamp per line, then `uv run cornerstone build`. Follow the shape of `~/repos/scripts/slack-channel-digest`.
- The plist runs `/bin/bash /Users/brian.kwon/repos/cornerstone-fantasy-sleeper-weekly-report/bin/cornerstone-build` on `Weekday 2`, `Hour 8`, `Minute 0`, with `RunAtLoad` false and the same `PATH` as the existing plists.

- [ ] **Step 1: Create the private source repo and push**

Run: `gh repo create bkwon94/cornerstone-fantasy-sleeper-weekly-report --private --source=. --remote=origin --push`
Expected: the repo exists, is private, and `main` is pushed.

- [ ] **Step 2: Create the public site repo and turn on Pages**

Run:
```bash
mkdir -p ~/repos/cornerstone-fantasy-sleeper-weekly-report-site && cd ~/repos/cornerstone-fantasy-sleeper-weekly-report-site
git init -b main && touch .nojekyll && printf '# Cornerstone League Weekly\n\nBuilt pages only. Source lives in a private repo.\n' > README.md
git add -A && git commit -m "chore: site placeholder"
gh repo create bkwon94/cornerstone-fantasy-sleeper-weekly-report-site --public --source=. --remote=origin --push
gh api -X POST repos/bkwon94/cornerstone-fantasy-sleeper-weekly-report-site/pages -f build_type=legacy -f 'source[branch]=main' -f 'source[path]=/'
```
Expected: HTTP 201. `gh api repos/bkwon94/cornerstone-fantasy-sleeper-weekly-report-site/pages` shows `"html_url": "https://bkwon94.github.io/cornerstone-fantasy-sleeper-weekly-report-site/"`. Then `cd` back to the source repo.

- [ ] **Step 3: Write the wrapper and the plist, then load the job**

Run: `chmod +x bin/cornerstone-build && cp launchagents/com.briankwon.cornerstone-weekly.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.briankwon.cornerstone-weekly.plist && launchctl list | grep cornerstone`
Expected: the label appears in the list.

- [ ] **Step 4: Run the first live build for week 6**

Run: `uv run cornerstone build --week 6`
Expected: the browser opens `site/2026/week-06/index.html`, a notification fires, `data/2026/week-06/` holds raw, facts, blurbs, and verify files. Read `verify.json` and count fallbacks. Report the count and every fallback chapter to Brian.

- [ ] **Step 5: Stop for Brian's review**

Brian reads the page. He asks for rewrites with `uv run cornerstone rewrite --week 6 --chapter <key>`. He publishes with `uv run cornerstone publish --week 6`. Nothing in this plan pushes the page without that command.

- [ ] **Step 6: Update the README runbook and commit**

Runbook: 1. Tuesday 8:00 the job builds and opens the page. 2. Read it. 3. Rewrite a chapter if needed. 4. Publish. 5. Share the home page link. Add the public URL.

```bash
git add bin launchagents README.md
git commit -m "chore: launchd job, Pages setup, runbook"
```

---

## Later

- Backfill weeks 1 to 5 with an "as of week N" standings layer. Fill `season_avg`, real `schedule_strength`, and the upset signal from history instead of the version 1 approximation.
- Playoff chapter set before week 15.
- A `--dry-run` for the writer that prints the prompts without a call.
