# Trade Grade v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Grade each side of each trade from facts that end the week before the trade, write one blurb per trade, and show each trade as a card that opens and closes.

**Architecture:** New helpers in `history.py` compute each player's season up to week N-1: points per game, position rank by season points, snap share, target share, and red-zone use. `sheet.py` turns them into per-trade facts and one chapter `trade_{n}` per trade, with only `T{n}.` facts. The writer, the code check, and the verifier already work per chapter. The writer gets the new rules 18 and 19, and the page gets a card per trade with a recap-style panel.

**Tech Stack:** Python 3.11, `uv`, Pydantic, Jinja2, `pytest`. No new dependency.

**Spec:** `design/specs/2026-10-20-trade-grade-v2-design.md` (the addendum, binding). It amends the Trades chapter of `design/specs/2026-10-20-history-trades-drops-design.md`. Read both. The trade model, the window, the late rule, and the swing come from the second file and do not change.

## Global Constraints

- "Before the trade" means weeks 1 to N-1, with N the week of the page. This holds for every trade in the window, late or not.
- No grade input reads week N data. Only the `impact` and `swing` facts carry week N numbers.
- A fact that needs a window the data cannot fill is absent, never wrong.
- Build every new fact with `_fact(fid, text, n, teams, players)`. Put every number in the text through `n(...)`, `n.ord(...)`, or `n.record(...)`. The tests `test_every_number_appears_in_its_text` and `test_every_number_token_in_text_is_in_numbers` in `tests/test_sheet.py` run on `tbundle` and `dbundle` and must pass.
- Give each new term one line in `src/cornerstone/prompts/vocabulary.md`, with the text in Task 2 and Task 3.
- Writer rules 15 to 17 do not change: at most two numbers per sentence, digits only, no counts.
- The grade stays Claude's opinion. The note `Grades are Tina's opinion from the fact sheet, not a computed score.` stays on the page.
- Every chapter holds at 390px with no horizontal scroll.
- No mock mode. Tests use the recorded data under `tests/fixtures/` and inject callables. No network and no Claude call in a test.
- Prose, comments, docstrings, and commit messages follow Simplified Technical English. Prompt files and blurbs are exempt.
- Commit at the end of every task. Write the subject as one plain imperative sentence. End the message with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Never use `--no-verify`.
- Nothing publishes without `cornerstone publish`. No task runs it. Brian runs it.
- The work lands on the branch `history-trades-drops`, on top of `a29268e`.

## Review Focus

1. A week in 1 to N-1 with empty stats is an outage of the Sleeper stats endpoint. The profile facts must go away, not shrink to fewer games. Tests in Task 1 and Task 2.
2. A player with no scored game before the trade, such as Josh Jacobs (`5850`), must get a `got` fact with no number and no usage facts, and the card must render him with no ppg. Tests in Task 2 and Task 6.
3. Week N data must not leak into a grade input. A week 6 injury entry, or the week 6 points, must not appear in a profile, usage, or injury fact. Tests in Task 2 and Task 3.
4. A player in two trades in one week gets facts in both chapters. Brian Robinson (`8154`) is in T4 and T6. Test in Task 3.
5. A late trade keeps its profile, team, and impact facts. Its `impact` fact names the old roster that started the player. Test in Task 2.

## File Structure

| File | Change | Responsibility |
| --- | --- | --- |
| `src/cornerstone/models.py` | Modify | `PastWeek.positions`, `PastWeek.nfl_teams`, `UsageShare` |
| `src/cornerstone/parse.py` | Modify | Fill the two new `PastWeek` maps in `parse_past_week` |
| `src/cornerstone/history.py` | Modify | Pre-trade player helpers with a `through` week; `player_trend` gains `through` |
| `src/cornerstone/sheet.py` | Modify | The pre-trade trade facts and one chapter per trade |
| `src/cornerstone/writer.py` | Modify | The template fallback per trade |
| `src/cornerstone/render.py`, `templates/week.html`, `static/style.css`, `static/app.js` | Modify | Card per trade with ppg, grade letters, button, and panel |
| `src/cornerstone/prompts/vocabulary.md`, `writer.md` | Modify | New terms; rules 18 and 19 |
| `tests/test_history.py`, `test_trades.py`, `test_writer.py`, `test_verifier.py`, `test_render.py` | Modify | Tests for each task |

---

### Task 1: Pre-trade player helpers

**Files:**
- Modify: `src/cornerstone/models.py`, `src/cornerstone/parse.py:172-197`, `src/cornerstone/history.py`
- Test: `tests/test_history.py`

**Interfaces:**
- Produces, in `models.py`:
  - `PastWeek` gains `positions: dict[str, str] = {}` and `nfl_teams: dict[str, str] = {}`, keyed by player id. `parse_past_week` fills them from each stats row: `row["player"]["position"]` and `row["team"]`. Skip a row with no value.
  - `UsageShare(percent: int, weeks: int, direction: Literal["up", "down", "flat"] | None)`. `weeks` is the count of weeks in `percent`. `direction` is `None` when the player has fewer than 4 share weeks.
- Produces, in `history.py`:
  - `SHARE_SWING = 5`: percentage points for "up" or "down".
  - `stats_complete(history: History, through: int) -> bool`: every week 1 to `through` is present and has a non-empty `stats` map.
  - `scored_weeks(history: History, player_id: str, through: int) -> list[int]`: weeks 1 to `through` with `stats[pid]["gp"] > 0`.
  - `points_per_game(history: History, player_id: str, through: int) -> tuple[float, int] | None`: `(ppg, games)`. `None` when `stats_complete` is false. `(0.0, 0)` with no scored week. Sum `player_points` over the scored weeks as `Decimal`, divide by the count, and round half up to 1 decimal.
  - `season_rank(history: History, player_id: str, through: int) -> tuple[int, int] | None`: `(rank, of)`. Sum `pts_half_ppr` over weeks 1 to `through` for every player id in the stats files. The player's position is his `positions` value in the latest week that has one. `of` counts the players with that position. `rank` is 1 plus the count of totals above his. `None` when `stats_complete` is false or he has no position.
  - `snap_share(history: History, player_id: str, through: int) -> UsageShare | None`: `off_snp` over `tm_off_snp`.
  - `target_share(history: History, player_id: str, through: int) -> UsageShare | None`: `rec_tgt` over the sum of `rec_tgt` of every player with the same `nfl_teams` value in that week.
  - `red_zone(history: History, player_id: str, through: int) -> tuple[int, int] | None`: `(rec_rz_tgt, rush_rz_att)` summed over weeks 1 to `through`. `None` when `stats_complete` is false or the player has no scored week.
  - `share_direction(recent: float, prior: float) -> Literal["up", "down", "flat"]`.
  - `player_trend(history: History, player_id: str, through: int | None = None) -> int | None`. `None` means `history.week`, so the callers of today do not change.

The share algorithm, which the tests alone do not fix:

```python
weeks = [w for w in scored_weeks(h, pid, through) if denominator(w) > 0]
if not stats_complete(h, through) or not weeks:
    return None
def pct(ws): return 100 * sum(numerator(w) for w in ws) / sum(denominator(w) for w in ws)
if len(weeks) < 4:
    return UsageShare(percent=round_half_up(pct(weeks)), weeks=len(weeks), direction=None)
recent, prior = weeks[-2:], weeks[-4:-2]
return UsageShare(percent=round_half_up(pct(recent)), weeks=2,
                  direction=share_direction(pct(recent), pct(prior)))
```

`share_direction` compares the unrounded percents: "up" when `recent - prior >= SHARE_SWING`, "down" when `prior - recent >= SHARE_SWING`, else "flat".

- [ ] **Step 1: Write the failing tests**

The fixture cut holds about 240 players a week, not about 770. The target share and the `of` count are therefore larger than on real data. The values below are from the fixtures.

```python
def _h(fixture_history_root, fixture_raw_dir):
    return load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)

def test_past_week_keeps_position_and_nfl_team(fixture_history_root, fixture_raw_dir):
    h = _h(fixture_history_root, fixture_raw_dir)
    assert h.weeks[5].positions["12501"] == "WR" and h.weeks[5].nfl_teams["12501"] == "GB"

def test_golden_profile_through_week_5(fixture_history_root, fixture_raw_dir):
    # Week 5: 47 of 61 snaps, 7 targets, 3 red-zone targets, 17.3 points.
    h = _h(fixture_history_root, fixture_raw_dir)
    assert points_per_game(h, "12501", 5) == (13.3, 5)
    assert season_rank(h, "12501", 5) == (11, 90)
    assert snap_share(h, "12501", 5) == UsageShare(percent=83, weeks=2, direction="flat")
    assert target_share(h, "12501", 5) == UsageShare(percent=32, weeks=2, direction="flat")
    assert red_zone(h, "12501", 5) == (7, 0)
    assert player_trend(h, "12501", through=5) == 3

def test_tuten_profile_ignores_week_6(fixture_history_root, fixture_raw_dir):
    # He scored 22.7 in week 6. Through week 5 the average is 59.2 over 5 games.
    h = _h(fixture_history_root, fixture_raw_dir)
    assert points_per_game(h, "12490", 5) == (11.8, 5)
    assert season_rank(h, "12490", 5) == (16, 77)
    assert snap_share(h, "12490", 5) == UsageShare(percent=64, weeks=2, direction="up")
    assert target_share(h, "12490", 5) == UsageShare(percent=11, weeks=2, direction="flat")
    assert red_zone(h, "12490", 5) == (1, 12)
    assert player_trend(h, "12490", through=5) == 1

def test_fewer_than_4_weeks_has_no_direction(fixture_history_root, fixture_raw_dir):
    h = _h(fixture_history_root, fixture_raw_dir)
    assert points_per_game(h, "7569", 5) == (17.7, 3)
    assert snap_share(h, "7569", 5) == UsageShare(percent=71, weeks=3, direction=None)

def test_no_scored_game(fixture_history_root, fixture_raw_dir):
    h = _h(fixture_history_root, fixture_raw_dir)
    assert points_per_game(h, "5850", 5) == (0.0, 0)
    assert snap_share(h, "5850", 5) is None and red_zone(h, "5850", 5) is None

def test_ppg_rounds_half_up(fixture_history_root, fixture_raw_dir):
    # Patrick Mahomes: 85.58 over 4 games is 21.395.
    assert points_per_game(_h(fixture_history_root, fixture_raw_dir), "4046", 5) == (21.4, 4)

def test_stats_outage_removes_the_profile(fixture_history_root, fixture_raw_dir):
    h = _h(fixture_history_root, fixture_raw_dir)
    h.weeks[2].stats = {}
    assert points_per_game(h, "12490", 5) is None
    assert season_rank(h, "12490", 5) is None
    assert snap_share(h, "12490", 5) is None and target_share(h, "12490", 5) is None

def test_share_direction():
    assert share_direction(55, 50) == "up"
    assert share_direction(50, 55) == "down"
    assert share_direction(54.9, 50) == "flat"
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_history.py -v`
Expected: FAIL with an import error for `points_per_game`.

- [ ] **Step 3: Write the two `PastWeek` fields, `UsageShare`, the parse change, and the helpers**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/models.py src/cornerstone/parse.py src/cornerstone/history.py tests/test_history.py
git commit -m "Add the pre-trade player helpers for points, rank, and usage" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Pre-trade profile, team, need, and impact facts

**Files:**
- Modify: `src/cornerstone/sheet.py:593-702`, `src/cornerstone/render.py:93-114`, `src/cornerstone/templates/week.html:61`, `src/cornerstone/prompts/vocabulary.md`
- Test: `tests/test_trades.py`, `tests/test_render.py`, `tests/test_verifier.py`

**Interfaces:**
- Consumes: the Task 1 helpers, `season_records` from `facts_league.py`, `Context.before`.
- Produces: the fact IDs below. `through` is `c.week.week - 1` in every one.

| ID | When | Text |
| --- | --- | --- |
| `T{n}.{rid}.got.{pid}` | `points_per_game` gives games > 0 | `{team} got {name}: {ppg} points per game over {g} games before the trade, position rank {r} of {of} by season points.` Drop the rank clause when `season_rank` is `None`. |
| same | games is 0 | `{team} got {name}: no scored game before the trade.` |
| same | `points_per_game` is `None` | `{team} got {name}.` |
| `T{n}.{rid}.gave.{pid}` | as `got` | the same three shapes with `gave` |
| `T{n}.{rid}.team` | `c.history` is complete | `{team} was {w}-{l}, {rank} of 12, before the trade.` with `w`, `l` from `season_records(c.history, N-1)` and `rank` from `c.before` |
| `T{n}.{rid}.need` | trade not late | `{team} has {n} {POS} and {n} {POS} after the trade and {k} open roster spot(s).` The depth and the spots do not change from part 2. |
| `T{n}.{rid}.impact.{pid}` | player has a line this week; `rid` is the roster that got him | started: `{name} scored {pts} this week for {team}.` bench: `{name} scored {pts} this week on the bench for {team}.` `{team}` is `c.line_owner[pid]`. |
| `T{n}.{rid}.swing` | unchanged | unchanged |

- The `got` and `gave` facts append the trend sentence `_trend_text(...)` when `player_trend(c.history, pid, through=N-1)` is not `None`. They no longer append the pre-game sentence, because that report is from week N.
- A late trade gets `team` and `impact` facts. It still gets no `need` and no `swing`.
- `render.py` `_trades` reads each player's ppg from the `got` fact: `fact.numbers[0]` when `" points per game" in fact.text`, else `None`. The card item key is `ppg`, in place of `points`. The template prints `p.ppg`. The label comes in Task 6.

Vocabulary lines, added under the trade terms:

```
- **points per game**: half-PPR points over the weeks with a scored game, weeks 1 to N-1.
- **position rank by season points**: among every player at the position in Sleeper's weekly stats, weeks 1 to N-1.
- **trade impact**: what the traded players scored in the week of the trade. It never feeds the grade.
```

- [ ] **Step 1: Write the failing tests, and replace the part 2 tests they contradict**

Remove `test_got_facts`, `test_need_fact`, `test_got_fact_without_history`, `test_got_fact_drops_the_season_total_when_a_week_has_no_stats`, and `test_got_fact_keeps_the_season_total_when_roster_points_cover_the_week` from `tests/test_trades.py`. Keep `_got_tuten`. The tests below replace them.

```python
def test_got_and_gave_facts_end_before_the_trade(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12.got.12490"].text == (
        "Amon-Ra Dawg Your Team got Bhayshul Tuten: 11.8 points per game over 5 games before the trade, "
        "position rank 16 of 77 by season points. Bhayshul Tuten has missed projection in 2 of the last 3 weeks.")
    assert f["T5.12.gave.11834"].text == (
        "Amon-Ra Dawg Your Team gave Devaughn Vele: 9.9 points per game over 5 games before the trade, "
        "position rank 23 of 90 by season points. Devaughn Vele has missed projection in 2 of the last 3 weeks.")
    assert f["T3.4.got.7569"].text == (
        "Pukancun on 3 got Nico Collins: 17.7 points per game over 3 games before the trade, "
        "position rank 21 of 90 by season points.")
    assert f["T5.11.got.5850"].text == "Unsolicited Dak Picks got Josh Jacobs: no scored game before the trade."
    assert f["T5.11.got.5850"].numbers == []

def test_no_profile_fact_says_this_week(dbundle):
    profile = re.compile(r"T\d+\.\d+\.(got|gave)\.\d+")
    texts = [f.text for fid, f in dbundle.sheet.facts.items() if profile.fullmatch(fid)]
    assert texts and not any("this week" in t or "final NFL injury report" in t for t in texts)

def test_got_fact_without_history(fixture_raw_dir, tbundle):
    f = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [], trades=tbundle.data.trades).sheet.facts
    assert f["T5.12.got.12490"].text == "Amon-Ra Dawg Your Team got Bhayshul Tuten."
    assert "T5.12.team" not in f

def test_got_fact_drops_the_profile_on_a_stats_outage(fixture_raw_dir, fixture_history_root, tbundle):
    text = _got_tuten(fixture_raw_dir, fixture_history_root, tbundle, keep_points=True)
    assert text.startswith("Amon-Ra Dawg Your Team got Bhayshul Tuten.") and "points per game" not in text

def test_team_facts(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12.team"].text == "Amon-Ra Dawg Your Team was 4-6, 8th of 12, before the trade."
    assert f["T5.11.team"].text == "Unsolicited Dak Picks was 4-6, 7th of 12, before the trade."
    assert f["T6.8.team"].text == "Return of T Mac was 4-6, 9th of 12, before the trade."

def test_need_fact_has_no_record(tbundle):
    assert tbundle.sheet.facts["T5.12.need"].text == (
        "Amon-Ra Dawg Your Team has 5 RB and 5 WR after the trade and 1 open roster spot.")

def test_need_clamps_open_spots_at_zero(tbundle):   # keep the part 2 test as it is

def test_impact_facts(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12.impact.12490"].text == "Bhayshul Tuten scored 22.7 this week for Amon-Ra Dawg Your Team."
    assert f["T5.11.impact.11834"].text == "Devaughn Vele scored 5.7 this week on the bench for Unsolicited Dak Picks."

def test_late_trade_keeps_profile_team_and_impact(tbundle):
    # Braelon Allen went to roster 7 after his game, so roster 8 started him.
    f = tbundle.sheet.facts
    assert f["T6.7.impact.11576"].text == "Braelon Allen scored 11.4 this week for Return of T Mac."
    assert "T6.7.got.11576" in f and "T6.7.team" in f
    assert not any(fid.startswith("T6.") and fid.endswith((".swing", ".need")) for fid in f)

def test_vocabulary_has_the_profile_terms():
    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    for term in ("points per game", "position rank by season points", "trade impact"):
        assert f"**{term}**" in text
```

In `tests/test_render.py`, change the last line of `test_trades_section_order_and_cards` to `assert "Bhayshul Tuten" in html and "11.8" in html`.

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_trades.py tests/test_render.py -v`
Expected: FAIL on `T5.12.got.12490`, which still says "22.7 this week".

- [ ] **Step 3: Rewrite `_player_trade_fact` and `_need_fact`; add `_team_fact` and `_impact_fact`; wire them in `trade_facts`; change `_trades` and the template; add the vocabulary lines**

The split of the old `trade_facts` into helpers is the builder's call.

- [ ] **Step 4: Run all tests**

Run: `uv run pytest`
Expected: all pass. The number tests in `tests/test_sheet.py` cover the new facts through `tbundle` and `dbundle`.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/sheet.py src/cornerstone/render.py src/cornerstone/templates/week.html src/cornerstone/prompts/vocabulary.md tests/
git commit -m "Grade trades from the season before the trade" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Usage, red-zone, and injury facts before the trade

**Files:**
- Modify: `src/cornerstone/sheet.py`, `src/cornerstone/prompts/vocabulary.md`
- Test: `tests/test_trades.py`

**Interfaces:**
- Consumes: `snap_share`, `target_share`, `red_zone`, `UsageShare` from Task 1. `_weeks(count, n)` in `sheet.py`.
- Produces: one set of facts per trade and per moved player with a line this week. `through` is N-1.

| ID | When | Text |
| --- | --- | --- |
| `T{n}.{pid}.usage` | `snap_share` not `None`, direction set | `{name}'s snap share was {s} percent over the last 2 weeks before the trade, {up/down/flat} from the 2 weeks before that.` |
| same | direction `None` | `{name}'s snap share was {s} percent over {k} games before the trade.` |
| `T{n}.{pid}.targets` | position RB, WR, or TE, and `target_share` not `None` | the same two shapes with `target share` |
| `T{n}.{pid}.redzone` | position QB, RB, WR, or TE, and `red_zone` not `None` | `{name} had {a} red-zone target(s) and {b} red-zone carr(y/ies) this season before the trade.` |
| `T{n}.{pid}.injury` | `c.nfl.injuries` not `None`, and listed in week N-1 | `{name} was listed {status} on the NFL injury report in week {N-1}, and in {k} this season before the trade.` with `{k}` from `_weeks(count, n)` |
| same | not listed in N-1, count > 0 | `{name} was on the NFL injury report in {k} this season before the trade.` |

- The position is `c.lines[pid].position`.
- The injury count is the count of weeks 1 to N-1 in `c.nfl.injuries[pid]`. A week N entry never counts.
- The facts carry `teams=[]` and `players=[name]`.

Vocabulary lines:

```
- **snap share**: offensive snaps over the team's offensive snaps. The fact gives the share over the last 2 weeks before the trade, against the 2 weeks before those. Up or down means a change of 5 percentage points or more; else flat.
- **target share**: targets over the targets of every player on his NFL team in Sleeper's stats. Sleeper's stats cover QB, RB, WR, TE, K, and DEF. Same weeks and same up or down rule as snap share.
- **red-zone use**: targets and carries inside the 20.
- **injury before the trade**: the nflverse report through week N-1. The week N pre-game report is after the trade and never feeds the grade.
```

- [ ] **Step 1: Write the failing tests**

```python
def _injured(fixture_raw_dir, fixture_history_root):
    # The week 6 "Out" is after the trade, so no injury fact may count it.
    nfl = NflverseWeek(sources={}, gsis={}, drops=None,
                       injuries={"12490": {4: "Questionable", 5: "Questionable", 6: "Out"}, "8146": {3: "Questionable"}})
    return _trade_bundle(fixture_raw_dir, fixture_history_root, nfl=nfl).sheet.facts

def test_usage_facts(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12490.usage"].text == (
        "Bhayshul Tuten's snap share was 64 percent over the last 2 weeks before the trade, up from the 2 weeks before that.")
    assert f["T5.12490.targets"].text == (
        "Bhayshul Tuten's target share was 11 percent over the last 2 weeks before the trade, flat from the 2 weeks before that.")
    assert f["T3.7569.usage"].text == "Nico Collins's snap share was 71 percent over 3 games before the trade."

def test_redzone_fact(tbundle):
    assert tbundle.sheet.facts["T5.12490.redzone"].text == (
        "Bhayshul Tuten had 1 red-zone target and 12 red-zone carries this season before the trade.")

def test_quarterback_has_no_target_share(tbundle):
    f = tbundle.sheet.facts
    assert "T4.4046.usage" in f and "T4.4046.targets" not in f

def test_no_scored_game_has_no_usage(tbundle):
    assert not any(fid.startswith("T5.5850.") for fid in tbundle.sheet.facts)

def test_player_in_two_trades_gets_facts_in_both(tbundle):
    f = tbundle.sheet.facts
    assert "T4.8154.usage" in f and "T6.8154.usage" in f

def test_injury_facts_end_at_week_5(fixture_raw_dir, fixture_history_root):
    f = _injured(fixture_raw_dir, fixture_history_root)
    assert f["T5.12490.injury"].text == (
        "Bhayshul Tuten was listed Questionable on the NFL injury report in week 5, and in 2 weeks this season before the trade.")
    assert f["T5.8146.injury"].text == "Garrett Wilson was on the NFL injury report in 1 week this season before the trade."
    assert "T5.11834.injury" not in f

def test_no_injury_facts_without_nflverse(tbundle):
    assert not any(fid.endswith(".injury") for fid in tbundle.sheet.facts)

def test_vocabulary_has_the_usage_terms():
    for term in ("snap share", "target share", "red-zone use", "injury before the trade"):
        assert f"**{term}**" in text
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_trades.py -v`
Expected: FAIL with a `KeyError` on `T5.12490.usage`.

- [ ] **Step 3: Write the usage, red-zone, and injury facts, wire them in `trade_facts`, and add the vocabulary lines**

One function or three is the builder's call.

- [ ] **Step 4: Run all tests**

Run: `uv run pytest`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/sheet.py src/cornerstone/prompts/vocabulary.md tests/test_trades.py
git commit -m "Add snap share, target share, red-zone, and injury facts before each trade" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: One chapter per trade

**Files:**
- Modify: `src/cornerstone/sheet.py:64-72,807-810,893-900`, `src/cornerstone/render.py:96`
- Test: `tests/test_trades.py`, `tests/test_verifier.py`, `tests/test_writer.py`, `tests/test_render.py`

**Interfaces:**
- Consumes: every `T{n}.` fact from Tasks 2 and 3.
- Produces:
  - `SENTENCE_RANGES["trade"] = (3, 5)`. The `"trades"` entry goes away.
  - One chapter per trade, key `trade_{n}`, title `_join([c.team(r) for r in trade.roster_ids])`. Its `fact_ids` are every fact ID that starts with `f"T{n}."`, and nothing else: no `S.` IDs. Its scope is the rosters of that trade. `grade_keys` is `[f"T{n}.{r}" for r in trade.roster_ids]`. The chapters sit where the `trades` chapter was, after the recaps and before `median`, in trade order.
  - `_trade_ids(facts, n: int) -> list[str]`: the IDs that start with `f"T{n}."`. `T1.` never takes `T10.`.
  - `render.py` `_trades` reads the grades of trade `n` from `blurbs.get(f"trade_{n}")`. It shows no grade when the key is absent.

- [ ] **Step 1: Write the failing tests, and move the part 2 tests to the new keys**

```python
def test_one_chapter_per_trade(tbundle):
    keys = [c.key for c in tbundle.sheet.chapters]
    trade_keys = [k for k in keys if k.startswith("trade")]
    assert trade_keys == [f"trade_{n}" for n in range(1, 7)]
    assert keys.index("trade_1") > keys.index("recap_6") and keys.index("trade_6") < keys.index("median")

def test_trade_chapter(tbundle):
    ch = next(c for c in tbundle.sheet.chapters if c.key == "trade_5")
    assert ch.title == "Unsolicited Dak Picks and Amon-Ra Dawg Your Team"
    assert ch.grade_keys == ["T5.11", "T5.12"]
    assert (ch.min_sentences, ch.max_sentences) == (3, 5)
    assert set(ch.fact_ids) == {fid for fid in tbundle.sheet.facts if fid.startswith("T5.")}
    assert ch.scope_teams == ["Unsolicited Dak Picks", "Amon-Ra Dawg Your Team"]

def test_trade_chapters_take_no_week_facts(dbundle):
    for ch in (c for c in dbundle.sheet.chapters if c.key.startswith("trade_")):
        n = ch.key.removeprefix("trade_")
        assert ch.fact_ids and all(fid.startswith(f"T{n}.") for fid in ch.fact_ids)

def test_three_team_chapter_title(fixture_raw_dir, fixture_history_root):
    # Build with the week 5 three-team trade only, as test_three_team_trade does.
    assert ch.title == "To Infinity and Bijan, Return of T Mac and Amon-Ra Dawg Your Team"
    assert ch.grade_keys == ["T1.7", "T1.8", "T1.12"]

def test_no_trades_no_trade_chapter(hbundle):
    assert not any(c.key.startswith("trade") for c in hbundle.sheet.chapters)

def test_trade_ids_take_one_trade(tbundle):
    facts = {**tbundle.sheet.facts, "T10.sides": tbundle.sheet.facts["T1.sides"], "TOTAL.x": tbundle.sheet.facts["T1.sides"]}
    ids = _trade_ids(facts, 1)
    assert "T1.sides" in ids and "T10.sides" not in ids and "TOTAL.x" not in ids
```

Remove `test_trades_chapter`, `test_no_trades_no_chapter`, and `test_trades_chapter_takes_trade_facts_only` from `tests/test_trades.py`. The tests above replace them. Move the other part 2 tests to the new keys:

- `tests/test_verifier.py`: `_ch(sheet, "trades")` becomes `_ch(sheet, "trade_1")` in `test_trade_swing_passes_the_cost_and_decided_gates`, and `_ch(sheet, "trade_5")` in the two T5 swing tests and in `_graded`. The blurb chapter name follows. `test_missing_grade_fails` and `test_extra_grade_fails` keep their assertions.
- `tests/test_writer.py`: `_trades` returns the `trade_5` chapter. `test_trades_prompt_lists_grade_keys` asserts `"Grade keys: T5.11, T5.12" in user`. `test_trades_template_lists_the_sides` asserts `[s.fact_ids for s in b.sentences] == [["T5.sides"]]`.
- `tests/test_render.py`: `blurbs["trades"]` becomes `blurbs["trade_5"]`. `del blurbs["trades"]` deletes every `trade_` key. The template test sets each `trade_{n}` to its template. The counts of "No grade" stay 11 and 12.

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_trades.py tests/test_verifier.py tests/test_writer.py tests/test_render.py -v`
Expected: FAIL, no chapter `trade_5`.

- [ ] **Step 3: Write the per-trade chapters, `_trade_ids(facts, n)`, the sentence range, and the grade lookup in `_trades`**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest`
Expected: all pass. A trade chapter with the part 2 template still cites `T{n}.sides`, because it is the first fact of the chapter.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/sheet.py src/cornerstone/render.py tests/
git commit -m "Give each trade its own chapter with only its own facts" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Writer rules and the template fallback per trade

**Files:**
- Modify: `src/cornerstone/prompts/writer.md` (rules 18 and 19), `src/cornerstone/writer.py:94-103`
- Test: `tests/test_writer.py`, `tests/test_verifier.py`

**Interfaces:**
- Consumes: the `trade_{n}` chapters and their `grade_keys` from Task 4.
- Produces:
  - `template_blurb` for a chapter whose key starts with `trade_`: one sentence, the `T{n}.sides` fact, cited by its ID, no grades, `fallback=True`. It finds the fact by ID, not by position.
  - `build_writer_prompt`, `write_blurb`, and `code_check` do not change. They already work per chapter.

Rules 18 and 19 in `writer.md` are replaced by the text below, word for word, each on one line as the other rules are. Rules 20 and 21 stay.

```
18. In a trade chapter, grade each side on value at the moment of the trade, from the fact sheet only: points per game and position rank before the trade, the trend, snap share, target share, red-zone use, the injury report before the trade, the team's record and standing before the trade, and its roster need. A team near the bottom of the standings earns credit for a move. A team near the top earns credit for an upside bet such as a player back from injury or suspension. Never let `impact` or `swing` facts move a grade. Give an honest grade: one letter, A, B, C, D, or F. A trade can be a C for both sides. Put each grade in `grades` under a key from the "Grade keys" line. Give the reason in the sentences.
19. In a trade chapter, write the grade reasons first. Then at most one sentence on how the trade played out this week, from the `impact` or `swing` facts.
```

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_writer.py
def test_writer_rules_18_and_19(tbundle):
    system, _ = build_writer_prompt(_trades(tbundle), tbundle.sheet, None)
    assert "18. In a trade chapter, grade each side on value at the moment of the trade" in system
    assert "Never let `impact` or `swing` facts move a grade." in system
    assert ("19. In a trade chapter, write the grade reasons first. Then at most one sentence on how "
            "the trade played out this week, from the `impact` or `swing` facts.") in system
    assert "With more than two trades" not in system and "In the Trades chapter" not in system
    assert "20. Never put a number on a draft pick." in system
    assert "Put at most two numbers in a sentence." in system and "Write every number as digits" in system

def test_trade_template_finds_the_sides_fact(tbundle):
    ch = next(c for c in tbundle.sheet.chapters if c.key == "trade_6")
    shuffled = ch.model_copy(update={"fact_ids": list(reversed(ch.fact_ids))})
    b = template_blurb(shuffled, tbundle.sheet)
    assert [s.fact_ids for s in b.sentences] == [["T6.sides"]]
    assert b.sentences[0].text == tbundle.sheet.facts["T6.sides"].text
    assert b.fallback and b.grades == {}

# tests/test_verifier.py
def test_grade_from_another_trade_fails(tbundle):
    assert _grade_failures(tbundle, **{"T1.4": "C"}) == ["[0] grade for T1.4 is not a trade side"]
```

Remove `test_writer_rules_hold_the_grade_rule`. `test_writer_rules_18_and_19` replaces it.

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_writer.py tests/test_verifier.py -v`
Expected: FAIL on the rule 18 text and on the shuffled template.

- [ ] **Step 3: Replace rules 18 and 19, and change `template_blurb`**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/prompts/writer.md src/cornerstone/writer.py tests/test_writer.py tests/test_verifier.py
git commit -m "Tell the writer to grade each trade at the moment of the trade" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: A trade card that opens and closes

**Files:**
- Modify: `src/cornerstone/render.py:93-114`, `src/cornerstone/templates/week.html:52-71`, `src/cornerstone/static/style.css:93-125`, `src/cornerstone/static/app.js`
- Test: `tests/test_render.py`

**Interfaces:**
- Consumes: the `trade_{n}` blurbs and the `got` facts.
- Produces:
  - `_trades` gives each card `{"sides": [...], "blurb": str}`. A side is `{"team", "grade", "players": [{"name", "ppg"}], "picks"}`. `grade` is `None` when the blurb of trade `n` is absent or is a fallback. `blurb` is the blurb text of `trade_{n}`, or the text of the `T{n}.sides` fact when that blurb is absent.
  - Card markup, inside `<div class="trade">`: the side rows with the grade beside each team name, then the button, then the panel. The grade sits outside the panel, so it shows on the closed card.
    - Player row: `<li><span>{name}</span><b>{ppg} <span class="ppg">ppg</span></b></li>`. A player with no ppg has no `<b>`.
    - Button: `<button class="cta recap-btn" type="button" aria-expanded="false"><span class="open-label">Read the grade</span><span class="close-label">Hide the grade</span><span class="chev"></span></button>`.
    - Panel: `<div class="body"><div class="inner"><p class="blurb">{blurb}</p></div></div>`.
  - The chapter-wide blurb paragraph goes away. The label `Trades` and the opinion note stay.
  - `app.js` toggles `open` on `b.closest('.mu, .trade')`.
  - `style.css` gives `.trade` the `.mu` button, label, chevron, panel, hover, and reduced-motion rules. The builder picks the selectors within the existing tokens.

- [ ] **Step 1: Write the failing tests**

```python
def _section(html):
    return html[html.index('id="trades"'):html.index(">All Matchups<")]

def _card(html, n):
    return _section(html).split('class="trade"')[n]

def test_trade_cards_have_a_button_and_a_panel(tbundle, tmp_path):
    s = _section(render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png).read_text())
    assert s.count("Read the grade") == 6 and s.count("Hide the grade") == 6
    assert s.count('aria-expanded="false"') == 6 and s.count('class="body"') == 6
    assert "Blurb for trade_5." in _card(s, 5)

def test_grade_shows_outside_the_panel(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    blurbs["trade_5"].grades = {"T5.11": "C", "T5.12": "A"}
    card = _card(render_week(tbundle, blurbs, tmp_path, _fake_png).read_text(), 5)
    assert card.index('<span class="grade">A</span>') < card.index('class="body"')

def test_card_shows_ppg_not_this_week(tbundle, tmp_path):
    s = _section(render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png).read_text())
    assert '11.8 <span class="ppg">ppg</span>' in s
    assert "22.7" not in s
    assert "<li><span>Josh Jacobs</span></li>" in s

def test_fallback_card_shows_no_grade_and_the_template(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    blurbs["trade_5"] = template_blurb(next(c for c in tbundle.sheet.chapters if c.key == "trade_5"), tbundle.sheet)
    card = _card(render_week(tbundle, blurbs, tmp_path, _fake_png).read_text(), 5)
    assert card.count("No grade") == 2
    assert tbundle.sheet.facts["T5.sides"].text in card

def test_card_without_a_blurb_holds_the_sides_text(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    del blurbs["trade_5"]
    card = _card(render_week(tbundle, blurbs, tmp_path, _fake_png).read_text(), 5)
    assert card.count("No grade") == 2 and tbundle.sheet.facts["T5.sides"].text in card

def test_app_js_toggles_trade_cards(tbundle, tmp_path):
    render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png)
    assert ".trade" in (tmp_path / "static" / "app.js").read_text()
```

`test_trades_opinion_note` and `test_no_trades_no_section` stay as they are.

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `uv run pytest tests/test_render.py -v`
Expected: FAIL, no "Read the grade".

- [ ] **Step 3: Write the card context, the markup, the CSS, and the `app.js` change**

- [ ] **Step 4: Run all tests**

Run: `uv run pytest`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cornerstone/render.py src/cornerstone/templates/week.html src/cornerstone/static/ tests/test_render.py
git commit -m "Show each trade as a card that opens to its grade" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Smoke render of week 6 from disk

**Files:**
- Create: `$SCRATCH/smoke_v2.py`, where `$SCRATCH` is the session scratchpad directory. It stays out of the repo.

This task makes no Claude call. It reads the saved `raw/`, `raw/nflverse.json`, the history, and the old `blurbs.json`.

- [ ] **Step 1: Write the smoke script**

The script takes the repo and an output directory. It reads `build.fetched` from `data/2026/week-06/verify.json` with `read_verify`. It calls `make_bundle(repo, 2026, 6, news=lambda pid: [], fetched=<that time>)`. With no `nflverse` callable, `make_bundle` loads the saved `raw/nflverse.json`. It writes `facts.json` to the output directory. It renders the page with the old `blurbs.json` and `fetch_bytes=lambda url: None`. It prints the page path, `record.sources`, and the text of every fact of `trade_5`. Then it asserts:

```python
trade = [c for c in bundle.sheet.chapters if c.key.startswith("trade_")]
assert [c.key for c in trade] == [f"trade_{n}" for n in range(1, 7)]
assert not any(f.startswith(("H.", "P.", "S.", "I.")) for c in trade for f in c.fact_ids)
html = page.read_text()
assert html.count("Read the grade") == 6 and html.count("No grade") == 12
```

- [ ] **Step 2: Run it**

Run: `uv run python $SCRATCH/smoke_v2.py . $SCRATCH/smoke`
Expected: no error, and five `True` sources. The old `blurbs.json` has no `trade_` key, so every card shows "No grade". The `trade_5` facts hold `T5.12490.usage` with the text `Bhayshul Tuten's snap share was 64 percent over the last 2 weeks before the trade, up from the 2 weeks before that.` `T5.12.got.12490` starts with `Amon-Ra Dawg Your Team got Bhayshul Tuten: 11.8 points per game over 5 games before the trade`. The rank and the target share differ from the fixture values, because the real stats hold every player.

- [ ] **Step 3: Check the page**

Open `$SCRATCH/smoke/site/2026/week-06/index.html` at 390px wide. Expected: 6 trade cards, each with its two team rows, the ppg labels, and the `Read the grade` button. A tap opens the panel with the sides sentence, and a second tap closes it. The page has no horizontal scroll.

- [ ] **Step 4: Run the full suite and commit any fix**

Run: `uv run pytest`
Expected: all pass. Commit a fix only if the smoke run needed one, with a subject that names the fix. Else no commit is due.

---

### Task 8: Rebuild week 6 for Brian's review

**Files:**
- Data: `data/2026/week-06/`, `data/2026/history/week-06/`, `site/2026/week-06/`, `site/index.html`

Warning: this rebuild rewrites every chapter. It replaces the `recap_1` text that Brian asked for in `6bfdf4d`. Tell Brian in Step 4.

- [ ] **Step 1: Build week 6 from the saved raw data**

Run: `uv run cornerstone build --week 6 --season 2026 --no-fetch`
Expected: the page path. This step calls Claude for 17 chapters, so `ANTHROPIC_API_KEY` must be set.

- [ ] **Step 2: Check the build record and list the fallbacks**

Read `data/2026/week-06/verify.json`. Expected: `build.fetched` is still `2026-10-20T11:58:45.187196-04:00`, `build.sources` holds five `True` values, and `facts.json` holds 6 trades. List each chapter with `"fallback": true` in `blurbs.json`. List each `trade_{n}` blurb whose `grades` is empty. A fallback is not an error, but Brian gets the list.

- [ ] **Step 3: Commit the rebuild as a new commit on top**

```bash
git add data/2026/week-06 data/2026/history/week-06 site
git commit -m "Rebuild week 6 with a grade per trade from the season before it" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

Do not amend or rebase an earlier commit.

- [ ] **Step 4: Stop for Brian**

Tell Brian the page is ready for review. Give him the fallback list from Step 2, and say that `recap_1` is rewritten too. Do not run `cornerstone publish`. Brian runs `uv run cornerstone publish --week 6 --season 2026` after his review. A fix after the review uses `uv run cornerstone rewrite --week 6 --season 2026 --chapter trade_{n}`.
