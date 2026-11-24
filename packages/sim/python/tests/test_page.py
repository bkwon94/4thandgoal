"""
Tests for the page block of the season sim: a small hand-built league at the seam of season_sim, read through the
page of one team. The real data of CPC and NorCal runs in tests/test_sim.py of the pipeline.
"""
import json
from pathlib import Path

import pytest

from league.league_settings import LeagueSettings
from sim.published import read_week_sim, sim_file, week_sim_file, write_sim, write_week_sim
from sim.season import SetResult, rerun, season_sim

SEASON = 2026
ROSTERS = range(1, 9)
# A league in its regular season: 2 weeks played, 2 weeks left. The records put roster 5 at 4-0 and roster 3 at 0-4.
SCORES = {rid: [100.0 + 7 * rid, 120.0 - 5 * rid] for rid in ROSTERS}
RECORDS = {rid: (2 + rid % 3, 2 - rid % 3, 220.0 + rid, 200.0 + rid) for rid in ROSTERS}
REMAINING = {3: [(1, 2), (3, 4), (5, 6), (7, 8)], 4: [(1, 3), (2, 4), (5, 7), (6, 8)]}
REASONS = {"2 wins ahead of you", "1 win ahead of you", "Level with you", "1 win behind you",
           "In the race for the last spot"}


def _settings(*, median_game: bool) -> LeagueSettings:
    return LeagueSettings(
        team_count=len(ROSTERS), playoff_spots=4, bye_count=2, star_rank_by_position={}, roster_slots=("QB",),
        last_regular_week=4, reception_points=0.5, median_game=median_game, reseed=True,
    )


def _sim(median_game: bool = True, runs: int = 4_000, **kwargs):
    return season_sim(SCORES, RECORDS, REMAINING, season=SEASON, week=2, settings=_settings(median_game=median_game),
                      runs=runs, pages=list(ROSTERS), **kwargs)


@pytest.fixture(scope="module")
def sim():
    return _sim()


def test_the_sim_gives_one_page_for_each_asked_team_and_none_by_default(sim):
    assert sorted(sim.pages) == list(ROSTERS)
    plain = season_sim(SCORES, RECORDS, REMAINING, season=SEASON, week=2, settings=_settings(median_game=True),
                       runs=100)
    assert plain.pages == {}


def test_the_ladder_lists_each_count_of_more_wins_with_the_chance_of_the_final_win_total(sim):
    for rid, page in sim.pages.items():
        # Two weeks left with a median game: 0 to 4 more wins.
        assert [step.more_wins for step in page.ladder] == [0, 1, 2, 3, 4]
        assert page.wins_left == 4 and page.weeks_left == 2
        final_wins = sim.teams[rid].final_wins
        assert {step.more_wins: step.chance for step in page.ladder if step.chance} == {
            wins - RECORDS[rid][0]: chance for wins, chance in final_wins.items()}


def test_the_ladder_odds_rise_with_the_wins_and_the_sentence_names_the_smallest_count_at_90(sim):
    for page in sim.pages.values():
        shown = [step.playoff for step in page.ladder if step.playoff is not None]
        assert shown == sorted(shown)
        at_90 = [step.more_wins for step in page.ladder if step.playoff is not None and step.playoff >= 90]
        assert page.need == (at_90[0] if at_90 else None)
        if page.status == "open" and page.need:
            assert page.sentence == f"Win {page.need} of the 4 left and you're in."


def test_each_week_has_four_results_with_wins_added_of_2_1_1_and_0(sim):
    page = sim.pages[1]
    assert [w.week for w in page.weeks] == [3, 4]
    assert [w.opponent for w in page.weeks] == [2, 3]
    week = page.weeks[0]
    assert [(r.game, r.median, r.wins_added) for r in week.results] == [
        ("win", "above", 2), ("win", "below", 1), ("loss", "above", 1), ("loss", "below", 0)]
    assert sum(r.chance for r in week.results) == pytest.approx(100, abs=0.2)
    # A win and the median each add a win, so the result with two more wins gives the best odds.
    odds = [r.playoff for r in week.results]
    assert odds[0] >= max(odds[1:]) and odds[3] <= min(odds[:3])


def test_a_league_with_no_median_game_has_two_results():
    sim = _sim(median_game=False, runs=1_000)
    week = sim.pages[1].weeks[0]
    assert [(r.game, r.median, r.wins_added) for r in week.results] == [("win", None, 1), ("loss", None, 0)]
    assert [step.more_wins for step in sim.pages[1].ladder] == [0, 1, 2]


def test_the_odds_after_a_loss_match_the_loss_side_of_the_swing(sim):
    # The swing and the page split the same runs on the next-week game, so both give the odds after a loss. The
    # page counts an exact tie as a loss, as a set result does, and the swing leaves it out, so the two can differ
    # by 1 point.
    swings = {(s.a, s.b): s for s in sim.swings}
    for a, b in REMAINING[3]:
        assert abs(sim.pages[a].weeks[0].loss_playoff - swings[(a, b)].a_loss) <= 1
        assert abs(sim.pages[b].weeks[0].loss_playoff - swings[(a, b)].b_loss) <= 1


def test_the_root_for_rows_follow_the_rules_of_the_spec(sim):
    rows_seen = 0
    for rid, page in sim.pages.items():
        for week in page.weeks:
            assert len(week.root_for) <= 3
            lifts = [row.playoff - week.loss_playoff for row in week.root_for]
            assert all(lift >= 1 for lift in lifts)
            assert lifts == sorted(lifts, reverse=True)
            for row in week.root_for:
                assert row.reason in REASONS
                assert rid not in (row.winner, row.loser)
                assert (row.winner, row.loser) in REMAINING[week.week] or (row.loser, row.winner) in REMAINING[week.week]
            rows_seen += len(week.root_for)
    assert rows_seen > 0


NAMED = {2: "2 wins ahead of you", 1: "1 win ahead of you", 0: "Level with you", -1: "1 win behind you"}


def _true_reason(you: int, loser: int, records, spots: int) -> str | None:
    """The one true reason of a row by the real standings, or None when no reason of the five is true. The race
    reason needs a loser within 1 win of the team that holds the last playoff spot."""
    gap = records[loser][0] - records[you][0]
    if gap in NAMED:
        return NAMED[gap]
    table = sorted(records, key=lambda rid: (-records[rid][0], -records[rid][2], -records[rid][3], rid))
    last = records[table[spots - 1]][0]
    return "In the race for the last spot" if abs(records[loser][0] - last) <= 1 else None


def test_the_reason_names_the_gap_in_real_wins_to_the_loser(sim):
    for rid, page in sim.pages.items():
        for week in page.weeks:
            for row in week.root_for:
                assert row.reason == _true_reason(rid, row.loser, RECORDS, 4)


# A spread of real wins from 1 to 8, so some losers sit 3 or more wins from roster 1 and roster 8.
WIDE = {rid: (rid, 8 - rid, 220.0 + rid, 200.0 + rid) for rid in ROSTERS}


GOALS = ["spot", "bye", "seed-1", "seed-2", "seed-3", "seed-4"]


def _hand_status(rid: int, records, reach: int, k: int) -> str:
    """The plain check on wins for the top `k` places, written by hand: Clinched when fewer than k other teams can
    reach the wins of `rid`, Out when k other teams already hold more wins than `rid` can reach."""
    wins = records[rid][0]
    others = [o for o in records if o != rid]
    if sum(records[o][0] + reach >= wins for o in others) < k:
        return "in"
    if sum(records[o][0] > wins + reach for o in others) >= k:
        return "out"
    return "open"


def _hand_seed_status(rid: int, records, reach: int, k: int) -> str:
    """Seed k is Clinched when the top k is sure and the top k - 1 is out of reach. It is Out when the top k is out
    of reach or the top k - 1 is sure."""
    top = _hand_status(rid, records, reach, k)
    above = _hand_status(rid, records, reach, k - 1) if k > 1 else "out"
    if top == "in" and above == "out":
        return "in"
    if top == "out" or above == "in":
        return "out"
    return "open"


@pytest.mark.parametrize("median_game", [True, False])
def test_each_page_holds_the_odds_and_the_status_of_the_spot_the_bye_and_each_seed(median_game):
    wide = season_sim(SCORES, WIDE, REMAINING, season=SEASON, week=2, settings=_settings(median_game=median_game),
                      runs=2_000, pages=list(ROSTERS))
    reach = (2 if median_game else 1) * len(REMAINING)
    statuses = set()
    for rid, page in wide.pages.items():
        assert list(page.goals) == GOALS
        team = wide.teams[rid]
        assert page.goals["spot"].odds == team.playoff and page.goals["bye"].odds == team.bye
        assert page.goals["spot"].status == _hand_status(rid, WIDE, reach, 4)
        assert page.goals["bye"].status == _hand_status(rid, WIDE, reach, 2)
        for k in range(1, 5):
            goal = page.goals[f"seed-{k}"]
            assert goal.status == _hand_seed_status(rid, WIDE, reach, k)
            expected = {"in": 100, "out": 0}.get(goal.status)
            if expected is None:
                assert abs(goal.odds - min(99, max(1, team.seeds.get(k, 0.0)))) <= 1
            else:
                assert goal.odds == expected
        statuses |= {goal.status for goal in page.goals.values()}
    # With 1 win in each week left, roster 8 at 8 wins is sure of a spot. With 2, no team is sure of a Goal.
    assert statuses == ({"out", "open"} if median_game else {"in", "out", "open"})


def test_each_page_opens_on_the_best_goal_with_odds_of_5_or_more_in_the_order_1_seed_bye_spot():
    wide = season_sim(SCORES, WIDE, REMAINING, season=SEASON, week=2, settings=_settings(median_game=True),
                      runs=2_000, pages=list(ROSTERS))
    opened = set()
    for page in wide.pages.values():
        best = next((goal for goal in ("seed-1", "bye", "spot") if page.goals[goal].odds >= 5), "spot")
        assert page.open_goal == best
        opened.add(page.open_goal)
    assert len(opened) > 1


def test_the_board_holds_the_goals_of_every_team_with_no_page_asked():
    wide = season_sim(SCORES, WIDE, REMAINING, season=SEASON, week=2, settings=_settings(median_game=True),
                      runs=2_000, pages=list(ROSTERS))
    plain = season_sim(SCORES, WIDE, REMAINING, season=SEASON, week=2, settings=_settings(median_game=True),
                       runs=2_000)
    assert [row.roster_id for row in plain.board] == list(ROSTERS)
    assert plain.board == wide.board
    for row in wide.board:
        assert row.goals == wide.pages[row.roster_id].goals


def test_the_race_reason_goes_only_to_a_loser_near_the_last_playoff_spot():
    wide = season_sim(SCORES, WIDE, REMAINING, season=SEASON, week=2, settings=_settings(median_game=True),
                      runs=4_000, pages=list(ROSTERS))
    race = 0
    for rid, page in wide.pages.items():
        for week in page.weeks:
            for row in week.root_for:
                assert row.reason == _true_reason(rid, row.loser, WIDE, 4)
                race += row.reason == "In the race for the last spot"
    assert race > 0


# The week 10 sim file of CPC, a saved copy of a real sim step that the What-if tests of the API read.
CPC_WEEK_10 = Path(__file__).resolve().parents[4] / "apps" / "api" / "tests" / "fixtures" / "sim" / "cpc-week-10-sim.json"


@pytest.mark.skipif(not CPC_WEEK_10.is_file(), reason="no week 10 sim file of CPC")
def test_each_reason_of_the_real_cpc_week_10_file_is_true():
    sim = json.loads(CPC_WEEK_10.read_text(encoding="utf-8"))
    records = {int(rid): tuple(record) for rid, record in sim["records"].items()}
    spots = sim["parameters"]["playoff_spots"]
    rows = [(int(you), row) for you, page in sim["pages"].items() for week in page["weeks"] for row in week["root_for"]]
    assert rows
    assert [row["reason"] for _, row in rows] == [_true_reason(you, row["loser"], records, spots) for you, row in rows]


def test_a_result_is_about_when_its_chance_times_the_effective_runs_is_under_400(sim):
    flagged = 0
    for page in sim.pages.values():
        for week in page.weeks:
            for r in week.results:
                assert r.about == (r.chance / 100 * sim.effective_runs < 400)
                flagged += r.about
    # At 4,000 runs a result under 10 percent is about, so the fixture league has both cases.
    assert 0 < flagged < sum(len(w.results) for p in sim.pages.values() for w in p.weeks)


def test_a_set_result_holds_in_the_page_of_your_team():
    sim = _sim(you=1, set_results=[SetResult(week=3, game="win", median="above")], runs=2_000)
    week = sim.pages[1].weeks[0]
    assert week.results[0].chance == 100.0
    assert [r.playoff for r in week.results[1:]] == [None, None, None]
    assert all(r.about for r in week.results[1:])


def test_the_weights_of_the_stored_runs_are_1_with_no_set_result_and_under_1_with_one(sim):
    assert sim.sample_weights == [1.0] * len(sim.sample)
    held = _sim(you=1, set_results=[SetResult(week=3, game="loss", median="below")], runs=500)
    assert len(held.sample_weights) == len(held.sample)
    assert all(0 < w < 1 for w in held.sample_weights)


def test_the_league_fact_names_the_race_for_the_last_spots(sim):
    safe = sum(t.playoff >= 90 for t in sim.teams.values())
    race = sum(10 <= t.playoff < 90 for t in sim.teams.values())
    left = 4 - safe
    if race > left > 0:
        spots = "spot" if left == 1 else f"{left} spots"
        assert sim.fact == f"{race} managers fight for the last {spots}"
    else:
        assert sim.fact == "The playoff field is all but set"


def test_the_week_file_holds_the_pages_and_the_season_file_keeps_its_shape(sim, tmp_path):
    names = {rid: f"Team {rid}" for rid in ROSTERS}
    out = write_week_sim(week_sim_file(sim, names), tmp_path)
    assert out == tmp_path / "2026" / "week-02" / "sim.json"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert {"schema_version", "effective_runs", "sample", "sample_weights", "pages", "fact", "names"} <= set(data)
    assert sorted(data["pages"]) == [str(rid) for rid in ROSTERS]
    assert read_week_sim(out) == week_sim_file(sim, names)
    season = write_sim(sim_file(sim, names), tmp_path).read_text(encoding="utf-8")
    for key in ("effective_runs", "sample_weights", "pages", "fact"):
        assert f'"{key}"' not in season


def test_the_sentence_after_a_set_result_counts_only_the_wins_still_open():
    # Week 3 holds a win over the opponent and the median, so 2 of the 4 wins left are set and 2 stay open.
    sim = _sim(you=1, set_results=[SetResult(week=3, game="win", median="above")], runs=2_000)
    page = sim.pages[1]
    assert page.need is not None and page.need >= 2
    open_need = page.need - 2
    if page.status == "open":
        assert page.sentence == (f"Win {open_need} of the 2 left and you're in." if open_need
                                 else "You're in at 90% or better even with no more wins.")
    # The page of another team holds no set result, so its sentence counts all 4 wins left.
    other = sim.pages[2]
    if other.status == "open" and other.need:
        assert other.sentence == f"Win {other.need} of the 4 left and you're in."


def test_the_sentence_with_every_week_left_set_says_so():
    held = [SetResult(week=3, game="win", median="below"), SetResult(week=4, game="loss", median="above")]
    sim = _sim(you=1, set_results=held, runs=2_000)
    if sim.pages[1].status == "open":
        assert sim.pages[1].sentence == "Every week left is set."


# The same league after its regular season: no regular week left, and a bracket of 4 in weeks 5 and 6. The records
# set the seeds: roster 8 first, then 7, 6, and 5. Roster 1 is out.
FINAL_RECORDS = {rid: (rid, 8 - rid, 400.0 + rid, 380.0 + rid) for rid in ROSTERS}


def _near(whole: int, tenth: float) -> bool:
    """True when a whole percent of the page is the title odds of the team, which has one decimal, rounded."""
    return abs(whole - tenth) <= 0.55


def _playoff_sim(played=None, runs: int = 2_000, **kwargs):
    return season_sim(SCORES, FINAL_RECORDS, {}, season=SEASON, week=4 + len(played or {}),
                      settings=_settings(median_game=True), runs=runs, pages=list(ROSTERS), played=played or {},
                      **kwargs)


def test_a_team_in_the_playoffs_gets_its_title_odds_its_game_and_two_results():
    sim = _playoff_sim()
    top = sim.pages[8].playoffs
    assert top is not None
    assert (top.seed, top.alive, top.week, top.bye, top.champion) == (1, True, 5, False, None)
    assert _near(top.title, sim.teams[8].title)
    assert top.game is not None and (top.game.week, top.game.opponent) == (5, 5)
    win, loss = top.game.results
    assert (win.game, loss.game) == ("win", "loss")
    assert loss.title == 0
    assert win.title is not None and win.title >= top.title
    assert win.chance + loss.chance == pytest.approx(100, abs=0.2)
    assert sim.pages[8].weeks == []


def test_a_team_out_of_the_playoffs_gets_the_bracket_with_the_title_odds_of_each_team_left():
    sim = _playoff_sim()
    out = sim.pages[1].playoffs
    assert out is not None
    assert (out.seed, out.alive, out.game) == (None, False, None)
    assert [(t.roster_id, t.seed, t.alive) for t in out.teams] == [(8, 1, True), (7, 2, True), (6, 3, True),
                                                                    (5, 4, True)]
    assert all(_near(t.title, sim.teams[t.roster_id].title) for t in out.teams)
    # Round 1 has its two games set. The final has no set side, so it offers no result.
    first, final = out.rounds
    assert (first.week, first.played, final.week, final.played) == (5, False, 6, False)
    assert sorted(g.teams for g in first.games) == [(7, 6), (8, 5)]
    assert [g.teams for g in final.games] == [(None, None)]


def test_a_played_round_shows_its_scores_and_winners_and_sets_the_game_of_the_next_round():
    played = {5: {8: 130.0, 5: 100.0, 7: 90.0, 6: 110.0}}
    sim = _playoff_sim(played)
    page = sim.pages[8].playoffs
    assert page is not None and page.week == 6
    first, final = page.rounds
    assert first.played and not final.played
    games = {g.teams: g for g in first.games}
    assert (games[(8, 5)].scores, games[(8, 5)].winner) == ((130.0, 100.0), 8)
    assert (games[(7, 6)].scores, games[(7, 6)].winner) == ((90.0, 110.0), 6)
    assert [g.teams for g in final.games] == [(8, 6)]
    assert page.game is not None and (page.game.week, page.game.opponent) == (6, 6)
    # A team that lost a played game is out, with title odds of 0.
    lost = sim.pages[7].playoffs
    assert lost is not None and (lost.seed, lost.alive, lost.title, lost.game) == (2, False, 0, None)
    assert [t.roster_id for t in page.teams if t.alive] == [8, 6]


def test_after_the_final_the_page_shows_the_final_bracket_and_the_champion():
    played = {5: {8: 130.0, 5: 100.0, 7: 90.0, 6: 110.0}, 6: {8: 95.0, 6: 120.0}}
    sim = _playoff_sim(played, runs=200)
    for rid in ROSTERS:
        page = sim.pages[rid].playoffs
        assert page is not None
        assert (page.champion, page.week, page.game, page.bye) == (6, None, None, False)
        assert all(r.played for r in page.rounds)
        assert page.rounds[-1].games[0].winner == 6
    champion = sim.pages[6].playoffs
    assert champion is not None and champion.title == 100
    assert sim.teams[6].title == 100.0


def test_a_top_seed_with_a_bye_has_no_game_and_no_result_until_its_opponent_is_set():
    six = LeagueSettings(
        team_count=8, playoff_spots=6, bye_count=2, star_rank_by_position={}, roster_slots=("QB",),
        last_regular_week=4, reception_points=0.5, median_game=True, reseed=False,
    )
    sim = season_sim(SCORES, FINAL_RECORDS, {}, season=SEASON, week=4, settings=six, runs=1_000, pages=[8, 6])
    top = sim.pages[8].playoffs
    assert top is not None
    assert (top.seed, top.alive, top.bye, top.week, top.game) == (1, True, True, 5, None)
    # The bye team sits in round 2 with an open side, so no later round offers a result.
    second = top.rounds[1]
    assert any(g.teams[0] == 8 and g.teams[1] is None for g in second.games)
    third = sim.pages[6].playoffs
    assert third is not None and third.game is not None and third.game.opponent == 3


def test_a_set_result_of_a_bracket_game_holds_in_the_playoff_page():
    sim = _playoff_sim(you=8, set_results=[SetResult(week=5, game="win")])
    page = sim.pages[8].playoffs
    assert page is not None and page.game is not None
    win, loss = page.game.results
    assert (win.chance, loss.chance) == (100.0, 0.0)
    assert loss.title is None


def test_the_league_fact_names_the_favorite_in_the_playoffs_and_the_champion_after_the_final():
    names = {rid: f"Team {rid}" for rid in ROSTERS}
    sim = _playoff_sim()
    favorite = max((8, 7, 6, 5), key=lambda rid: sim.teams[rid].title)
    page = sim.pages[1].playoffs
    assert page is not None
    shown = next(t.title for t in page.teams if t.roster_id == favorite)
    assert week_sim_file(sim, names).fact == f"4 teams left, Team {favorite} is the favorite at {shown}%"
    done = _playoff_sim({5: {8: 130.0, 5: 100.0, 7: 90.0, 6: 110.0}, 6: {8: 95.0, 6: 120.0}}, runs=100)
    assert week_sim_file(done, names).fact == "Team 6 is the 2026 champion"


def test_a_played_bracket_week_takes_no_set_result():
    with pytest.raises(ValueError, match="played"):
        _playoff_sim({5: {8: 130.0, 5: 100.0, 7: 90.0, 6: 110.0}}, runs=100, you=8,
                     set_results=[SetResult(week=5, game="win")])


def test_a_rerun_of_a_playoff_week_keeps_its_played_rounds():
    played = {5: {8: 130.0, 5: 100.0, 7: 90.0, 6: 110.0}}
    sim = _playoff_sim(played, runs=300)
    again = rerun(sim, pages=list(ROSTERS))
    assert again.played == sim.played
    assert again.pages == sim.pages
