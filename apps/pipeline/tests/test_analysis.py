"""
Tests for the Claude call of the trade analyzer: the fact sheet, the checks, the retry, and the fallback.
They feed the Josh Jacobs trade and the week 6 snapshot to analyze, with a fake in place of Claude.
"""
import logging
import re
import shutil

import pytest
from conftest import with_free_agents
from cpc import cpc_client, four_week

from analyzer import analysis
from analyzer.analysis import AnalysisOut, analyze, code_only
from analyzer.routes import result_document
from analyzer.rubric import ProposedTrade, TradeSide, grade
from analyzer.trade_facts import trade_fact_sheet
from analyzer.tunables import RECENT_RANK_GAP
from league.paths import returns_path
from league.provider.sleeper import load_raw
from league.slow_sources import load_slow_sources
from league.snapshot import build_snapshot, load_out_for_season, load_returns, load_snapshot

CLIENT = cpc_client()

# The week 6 Josh Jacobs trade: roster 11 gives Bhayshul Tuten and Garrett Wilson to roster 12
# for Jacobs and Devaughn Vele. Roster 12 asked. Chart values: Tuten 3.0, Wilson 27.5, Jacobs 11.5, Vele 55.0.
TUTEN, WILSON, JACOBS, VELE = "12490", "8146", "5850", "11834"
BATEMAN = "7571"


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    """The week 6 snapshot with the slow sources, set back to before the Jacobs trade."""
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    snap = four_week(load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CLIENT))
    rosters = dict(snap.rosters)
    rosters[11] = [pid for pid in rosters[11] if pid not in (JACOBS, VELE)] + [TUTEN, WILSON]
    rosters[12] = [pid for pid in rosters[12] if pid not in (TUTEN, WILSON)] + [JACOBS, VELE]
    return snap.model_copy(update={"rosters": rosters})


@pytest.fixture
def fa_snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    """The snapshot of the snap fixture with Rashod Bateman, a free agent receiver, in the players file."""
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    raw = with_free_agents(load_raw(fixture_raw_dir), {BATEMAN: {
        "full_name": "Rashod Bateman", "position": "WR", "team": "BAL", "status": "Active", "active": True}})
    snap = four_week(build_snapshot(raw, fixture_history_root, chart_week6, slow,
                          returns=load_returns(fixture_history_root.parent / "returns.json"), client=CLIENT))
    rosters = dict(snap.rosters)
    rosters[11] = [pid for pid in rosters[11] if pid not in (JACOBS, VELE)] + [TUTEN, WILSON]
    rosters[12] = [pid for pid in rosters[12] if pid not in (TUTEN, WILSON)] + [JACOBS, VELE]
    return snap.model_copy(update={"rosters": rosters})


@pytest.fixture
def trade():
    return ProposedTrade(season=2026, sides=(TradeSide(roster_id=11, gives=[{"player_id": TUTEN, "to": 12},
                                                                            {"player_id": WILSON, "to": 12}]),
                                             TradeSide(roster_id=12, gives=[{"player_id": JACOBS, "to": 11},
                                                                            {"player_id": VELE, "to": 11}])), asker=12)


def _facts(user: str) -> dict[str, str]:
    """The facts in the user message, by id."""
    return dict(re.findall(r"^- (\S+): (.+)$", user, re.MULTILINE))


class FakeClaude:
    """Records each call and answers from a list of responses, built from the user message of that call."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    def __call__(self, system, user, output_model):
        assert output_model is AnalysisOut
        self.calls.append((system, user))
        return AnalysisOut.model_validate(self.responses[len(self.calls) - 1](_facts(user)))


# The code's final letters for the Jacobs trade: roster 11 grades B and roster 12 grades D.
JACOBS_CODE_LETTERS = {11: "B", 12: "D"}


def _split(text):
    """The sentences of a text, one bullet each. No test text holds a period inside a sentence."""
    return re.split(r"(?<=\.) (?=[A-Z])", text)


def _side(roster_id, letter=None, reason=None, bullets=None, cited=None):
    return {
        "roster_id": roster_id, "final_letter": letter or JACOBS_CODE_LETTERS[roster_id], "reason": reason,
        "bullets": bullets or ["Garrett Wilson scored 14.2 points per game before the trade.",
                               "His target share went up.", "The trade moves him to a new roster."],
        "cited": cited or [f"{WILSON}.ppg", f"{WILSON}.targets"],
    }


def _response(eleven=None, twelve=None, choice="decline"):
    """A response that passes every check, with the given changes. It keeps the code letters, and the code declines."""
    return lambda facts: {
        "sides": [eleven or _side(11), twelve or _side(12)],
        "verdict": {"choice": choice, "reason": "The trade is fair for both sides."},
    }


def test_the_fact_sheet_holds_the_grade_inputs_of_the_traded_players_with_ids(trade, snap):
    fake = FakeClaude(_response())
    analyze(trade, snap, call=fake)
    system, user = fake.calls[0]
    facts = _facts(user)
    # Points per game and season rank, before the trade only.
    assert "14.2 points per game" in facts[f"{WILSON}.ppg"] and "His Season rank is WR7," in facts[f"{WILSON}.ppg"]
    assert "position rank" not in facts[f"{WILSON}.ppg"]
    assert f"{WILSON}.usage" in facts and f"{WILSON}.targets" in facts and f"{WILSON}.redzone" in facts
    # Jacobs is suspended, and the returns file has him back in week 7.
    assert "week 7" in facts[f"{JACOBS}.injury"]
    assert "4-6, 7th of 12" in facts["11.team"] and "a middle team" in facts["11.team"]
    assert "6 RB and 4 WR after the trade" in facts["11.need"] and "12.need" in facts
    assert "27.5" in facts[f"{WILSON}.value"]
    # Trade values cover the traded players only.
    assert sorted(fid for fid in facts if fid.endswith(".value")) == sorted(
        f"{pid}.value" for pid in (TUTEN, WILSON, JACOBS, VELE))
    # The call reads the rubric, the breakdown of both sides, and the code's default verdict.
    assert "# Rubric" in system and "# Analysis rules" in system
    assert "Final letter: B" in user and "Final letter: D" in user and "Roster fit: one step down." in user
    assert "Code's default verdict for Amon-Ra Dawg Your Team: decline." in user


def test_a_good_response_passes_through(trade, snap):
    fake = FakeClaude(_response())
    result = analyze(trade, snap, call=fake)
    assert len(fake.calls) == 1
    assert not result.fallback
    assert [s.final_letter for s in result.sides] == ["B", "D"]
    assert result.sides[0].bullets[0] == "Garrett Wilson scored 14.2 points per game before the trade."
    assert result.sides[0].cited == [f"{WILSON}.ppg", f"{WILSON}.targets"]
    assert result.verdict.choice == "decline" and result.verdict.reason == "The trade is fair for both sides."
    assert not result.verdict_differs
    assert [b.final_letter for b in result.breakdowns] == ["B", "D"]
    assert result.code_verdict.choice == "decline"


def test_a_letter_one_step_off_passes_with_its_reason(trade, snap):
    eleven = _side(11, letter="C", reason="Jacobs has no scored game before the trade.")
    result = analyze(trade, snap, call=FakeClaude(_response(eleven=eleven)))
    assert not result.fallback
    assert result.sides[0].final_letter == "C"
    assert result.sides[0].reason == "Jacobs has no scored game before the trade."
    # The side whose letter stays at the code's letter has no reason.
    assert result.sides[1].final_letter == "D" and result.sides[1].reason is None


def test_a_letter_two_steps_off_retries_then_falls_back_to_the_code(trade, snap):
    far = _response(eleven=_side(11, letter="D", reason="Wilson is a strong receiver."))
    fake = FakeClaude(far, far)
    result = analyze(trade, snap, call=fake)
    assert len(fake.calls) == 2
    # The retry tells Claude what failed.
    assert "Feedback from the last attempt:" in fake.calls[1][1]
    assert "final letter D is 2 steps from the code's B" in fake.calls[1][1]
    assert result.fallback
    assert [s.final_letter for s in result.sides] == ["B", "D"]
    # The fallback gives no bullets, so the page shows the rows alone.
    assert [s.bullets for s in result.sides] == [[], []]
    assert result.verdict == result.code_verdict and not result.verdict_differs


def test_a_retry_that_passes_stands(trade, snap):
    far = _response(eleven=_side(11, letter="D", reason="Wilson is a strong receiver."))
    fake = FakeClaude(far, _response())
    result = analyze(trade, snap, call=fake)
    assert len(fake.calls) == 2 and not result.fallback


@pytest.mark.parametrize("analysis", [
    # Wilson's trade value, from a cited value fact.
    "Garrett Wilson is worth 27.5 to this roster. His target share went up. He is a starter.",
    # The sum of the trade values the side gives: 3 and 27.5.
    "Garrett Wilson scored 14.2 points per game before the trade. The side gives 30.5. He is a starter.",
    # The chart name and its words, with no number.
    "Garrett Wilson scored 14.2 points per game before the trade. His chart tier is high. He is a starter.",
    "Garrett Wilson scored 14.2 points per game before the trade. Peaked in High Skool likes him. He starts.",
])
def test_a_chart_value_sum_or_word_in_the_prose_fails(trade, snap, analysis):
    bad = _response(eleven=_side(11, bullets=_split(analysis), cited=[f"{WILSON}.ppg", f"{WILSON}.value"]))
    fake = FakeClaude(bad, bad)
    result = analyze(trade, snap, call=fake)
    assert len(fake.calls) == 2
    assert result.fallback


def test_a_number_not_in_a_cited_fact_fails(trade, snap):
    # 14.2 is in the facts, but the side cites only the target share fact.
    bad = _response(eleven=_side(11, cited=[f"{WILSON}.targets"]))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert "number 14.2 is not in the cited facts" in fake.calls[1][1]


@pytest.mark.parametrize("sentence", [
    "He tops the depth chart.",
    "The side gets more trade value.",
])
def test_the_depth_chart_and_trade_value_without_a_number_pass(trade, snap, sentence):
    bullets = ["Garrett Wilson scored 14.2 points per game before the trade.", sentence, "He is a starter."]
    fake = FakeClaude(_response(eleven=_side(11, bullets=bullets)))
    assert not analyze(trade, snap, call=fake).fallback
    assert len(fake.calls) == 1


@pytest.mark.parametrize("sentence, word", [
    ("Bhayshul Tuten is a tier two back.", "tier"),
    ("He gives twice the production.", "twice"),
    ("He gives double the production.", "double"),
    ("He ranks high on the PIHS list.", "pihs"),
    ("Kendre Miller is a replacement back.", "replacement"),
    ("Kendre Miller is below the floor.", "floor"),
])
def test_a_banned_word_fails(trade, snap, sentence, word):
    bullets = ["Garrett Wilson scored 14.2 points per game before the trade.", sentence, "He is a starter."]
    bad = _response(eleven=_side(11, bullets=bullets))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert f"the word '{word}' is not allowed" in fake.calls[1][1]


def test_a_number_in_a_breakdown_reason_is_allowed(trade, snap, monkeypatch):
    real_grade = analysis.grade

    def grade_with_a_digit(trade, snapshot):
        first, second = real_grade(trade, snapshot)
        return first, second.model_copy(update={"reason": "The side gets 41 snaps a game."})

    monkeypatch.setattr(analysis, "grade", grade_with_a_digit)
    text = "Garrett Wilson scored 14.2 points per game before the trade. He takes 41 snaps a game. He starts."
    fake = FakeClaude(_response(eleven=_side(11, bullets=_split(text))))
    assert not analyze(trade, snap, call=fake).fallback
    assert len(fake.calls) == 1


def test_the_points_per_game_fact_names_the_season_rank_and_the_checker_accepts_a_quote_of_it(trade, snap):
    # Tuten's 59 points through week 5 put him 16th among the backs. Vele is WR23 by total points, and WR41 by points
    # per game over weeks 2 to 5, so the gap of 18 shows his Recent rank.
    fake = FakeClaude(_response(eleven=_side(11, bullets=[
        "Bhayshul Tuten is RB16 this season.", "Devaughn Vele has a Recent rank of WR41.", "He moves to a new roster."],
        cited=[f"{TUTEN}.ppg", f"{VELE}.ppg"])))
    result = analyze(trade, snap, call=fake)
    facts = _facts(fake.calls[0][1])
    assert "His Season rank is RB16, by total points this season." in facts[f"{TUTEN}.ppg"]
    assert "Recent rank" not in facts[f"{TUTEN}.ppg"]
    assert "His Recent rank is WR41, by points per game over the last 4 weeks." in facts[f"{VELE}.ppg"]
    assert not result.fallback
    assert len(fake.calls) == 1


def test_the_checker_accepts_a_sentence_that_quotes_a_cited_depth_count_or_strength_count(trade, snap):
    # Roster 11 gives Wilson WR12 and gets Vele, so it holds 1 receiver above the line after, from 2.
    # Tuten RB15 and Wilson leave its RB1, RB2, WR1, and WR2 starters, and Jacobs RB16 and Vele come in.
    text = ("WR depth above the line goes from 2 to 1. "
            "Its starters with a position rank of 24 or better go from 4 to 3.")
    fake = FakeClaude(_response(eleven=_side(11, bullets=_split(text), cited=["11.depth.wr", "11.strength"])))
    result = analyze(trade, snap, call=fake)
    facts = _facts(fake.calls[0][1])
    assert facts["11.depth.wr"] == "For Unsolicited Dak Picks, WR depth above the line goes from 2 to 1."
    assert facts["11.strength"] == ("For Unsolicited Dak Picks, the starters at RB1, RB2, WR1, and WR2 with a "
                                    "position rank of 24 or better go from 4 to 3.")
    assert not result.fallback
    assert len(fake.calls) == 1


def test_the_checker_accepts_a_sentence_that_quotes_the_rank_of_the_cited_free_agent(trade, fa_snap):
    # Vele WR40 takes WR2 of roster 11, below the line. Bateman scored 37.3 points in 4 games of weeks 2 to 5,
    # 9.33 a game. 32 receivers have more lineup value, so he is WR33, the best free agent at WR.
    text = ("WR2 is a hole after the trade for this side. The best free agent at WR is Rashod Bateman, WR33. "
            "Waivers can fix the hole.")
    fake = FakeClaude(_response(eleven=_side(11, bullets=_split(text), cited=["11.hole.wr2"])))
    result = analyze(trade, fa_snap, call=fake)
    facts = _facts(fake.calls[0][1])
    assert facts["11.hole.wr2"] == ("For Unsolicited Dak Picks, WR2 is a hole after the trade: Devaughn Vele is WR40. "
                                    "Garrett Wilson held WR1 before the trade. The best free agent at WR is Rashod "
                                    "Bateman, WR33.")
    assert not result.fallback
    assert len(fake.calls) == 1


def test_a_free_agent_rank_that_no_cited_hole_fact_holds_fails(trade, fa_snap):
    text = ("WR2 is a hole after the trade for this side. The best free agent at WR is Rashod Bateman, WR31. "
            "Waivers can fix the hole.")
    bad = _response(eleven=_side(11, bullets=_split(text), cited=["11.hole.wr2"]))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, fa_snap, call=fake).fallback
    assert "number 31 is not in the cited facts" in fake.calls[1][1]


def test_a_count_that_no_cited_depth_fact_holds_fails(trade, snap):
    # The depth fact of roster 11 holds 2 and 1, and no breakdown reason holds 38, so a count of 38 is a new number.
    text = "Josh Jacobs moves to this side. WR depth above the line goes from 38 to 1. He starts."
    bad = _response(eleven=_side(11, bullets=_split(text), cited=["11.depth.wr"]))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert "number 38 is not in the cited facts" in fake.calls[1][1]


def test_a_share_percent_from_the_trend_reason_is_allowed(trade, snap):
    # The trend reason of roster 11 gives Tuten's snap share of 64% over weeks 4 and 5. No cited fact holds 64.
    text = ("Garrett Wilson scored 14.2 points per game before the trade. "
            "Bhayshul Tuten took 64% of the snaps over weeks 4 and 5. He starts.")
    fake = FakeClaude(_response(eleven=_side(11, bullets=_split(text), cited=[f"{WILSON}.ppg"])))
    result = analyze(trade, snap, call=fake)
    trend = next(a for a in result.breakdowns[0].adjusters if a.name == "trend and usage")
    assert "Tuten: snap share 64%, up, over weeks 4 and 5." in trend.reason
    assert "64" not in _facts(fake.calls[0][1])[f"{WILSON}.ppg"]
    assert not result.fallback
    assert len(fake.calls) == 1


def test_the_log_line_holds_no_number_from_the_failure(trade, snap, caplog):
    text = "Garrett Wilson is worth 27.5 to this roster. His target share went up. He is a starter."
    bad = _response(eleven=_side(11, bullets=_split(text), cited=[f"{WILSON}.ppg", f"{WILSON}.value"]))
    fake = FakeClaude(bad, bad)
    with caplog.at_level(logging.WARNING, logger="analyzer.analysis"):
        assert analyze(trade, snap, call=fake).fallback
    # The retry feedback to Claude keeps the full failure text.
    assert "number 27.5 is not in the cited facts" in fake.calls[1][1]
    records = [r.getMessage() for r in caplog.records if r.name == "analyzer.analysis"]
    assert len(records) == 2
    for message in records:
        assert "failed" in message
        assert not re.search(r"\d", message.split("failed", 1)[1])


@pytest.mark.parametrize("bullets", [
    # The period in a name ends no sentence.
    ["Amon-Ra St. Brown is not in the trade.", "Garrett Wilson starts."],
    # The period in a decimal ends no sentence.
    ["Garrett Wilson scored 14.2 points per game before the trade.", "He starts."],
    # Claude writes the short form of a name, a suffix, and "vs." with a decimal in the same bullets.
    ["St. Brown is not in the trade, and Garrett Wilson scored 14.2 points per game.", "Harrison Jr. lost snaps.",
     "Garrett Wilson vs. Devaughn Vele is close."],
    # A run of initials ends no sentence, in a full name and in a form the snapshot does not hold.
    ["A.J. Brown is not in the trade.", "D.J. Moore is not in it either."],
])
def test_a_period_in_a_name_or_a_decimal_ends_no_sentence(trade, snap, bullets):
    # One sentence per bullet passes. A miscount gives two, which fails.
    assert "Amon-Ra St. Brown" in {p.name for p in snap.players.values()}
    fake = FakeClaude(_response(eleven=_side(11, bullets=bullets)))
    assert not analyze(trade, snap, call=fake).fallback


@pytest.mark.parametrize("bullets, failure", [
    (["Garrett Wilson scored 14.2 points per game before the trade."], "roster 12: it has 1 bullets; the range is 2 to 3"),
    (["One.", "Two.", "Three.", "Four."], "roster 12: it has 4 bullets; the range is 2 to 3"),
    (["Garrett Wilson scored 14.2 points per game before the trade. He is a starter.", "His target share went up."],
     "roster 12: bullet 1 has 2 sentences; it needs exactly 1"),
])
def test_a_side_outside_two_to_three_bullets_or_a_bullet_of_two_sentences_fails(trade, snap, bullets, failure):
    bad = _response(twelve=_side(12, bullets=bullets))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert failure in fake.calls[1][1]


def test_a_cited_id_not_in_the_facts_fails(trade, snap):
    bad = _response(twelve=_side(12, cited=[f"{WILSON}.ppg", "T1.12.need"]))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert "fact ID T1.12.need is not in the facts" in fake.calls[1][1]


def test_a_letter_that_differs_with_no_reason_fails(trade, snap):
    bad = _response(twelve=_side(12, letter="C"))
    assert analyze(trade, snap, call=FakeClaude(bad, bad)).fallback


def test_the_verdict_flag_is_set_when_it_differs_from_the_code(trade, snap):
    result = analyze(trade, snap, call=FakeClaude(_response(choice="counter")))
    assert not result.fallback
    assert result.verdict.choice == "counter" and result.code_verdict.choice == "decline"
    assert result.verdict_differs


def test_the_code_sets_the_verdict_flag_so_claude_gives_no_flag(trade, snap):
    assert "differs" not in AnalysisOut.model_json_schema()["$defs"]["VerdictOut"]["properties"]
    fake = FakeClaude(_response())
    analyze(trade, snap, call=fake)
    assert "flag" not in fake.calls[0][0]


def test_the_number_rule_bans_a_trade_value_a_sum_and_a_ratio(trade, snap):
    fake = FakeClaude(_response())
    analyze(trade, snap, call=fake)
    # The prompt wraps its lines, so the check reads it as one line.
    system = " ".join(fake.calls[0][0].split())
    assert "except trade values; never write a trade value, a sum, or a ratio" in system
    for phrase in ("is rejected", "injury picture", "came about"):
        assert phrase not in system


def test_the_letter_rules_guard_the_fairness_state(trade, snap):
    fake = FakeClaude(_response())
    analyze(trade, snap, call=fake)
    # The prompt wraps its lines, so the check reads it as one line.
    system = " ".join(fake.calls[0][0].split())
    assert ("The fairness state is a code rule on the letters that stand. Never move a letter to change it, "
            "and never write win-win, lopsided, or fair about the trade.") in system


def test_an_empty_response_or_a_refusal_falls_back(trade, snap):
    from facts.writer import RefusalError

    def refuse(system, user, output_model):
        raise RefusalError("Claude refused the request for AnalysisOut.")

    assert analyze(trade, snap, call=lambda s, u, m: None).fallback
    assert analyze(trade, snap, call=refuse).fallback


def test_no_chart_value_reaches_the_result(trade, snap):
    result = analyze(trade, snap, call=FakeClaude(_response()))
    text = result.model_dump_json()
    for number in ("27.5", "11.5", "55.0", "30.5", "66.5"):
        assert number not in text
    assert "chart" not in text.lower() and "tier" not in text.lower()


def _three_sides(facts):
    """A response with three sides: roster 11, roster 12, then roster 11 again."""
    good = _response()(facts)
    return {**good, "sides": [*good["sides"], good["sides"][0]]}


def test_a_repeated_side_fails_and_the_retry_names_the_exact_side_shape(trade, snap):
    fake = FakeClaude(_three_sides, _response())
    result = analyze(trade, snap, call=fake)
    assert not result.fallback
    assert len(fake.calls) == 2
    retry = fake.calls[1][1]
    assert "it had rosters 11, 12, 11" in retry
    assert "exactly 2 sides: roster 11 first, then roster 12, each once" in retry


def test_every_retry_names_the_side_shape_with_both_roster_ids(trade, snap):
    # A bullet count failure on one side must not lead Claude to send that side alone.
    four = ["One.", "Two.", "Three.", "Four."]
    fake = FakeClaude(_response(twelve=_side(12, bullets=four)), _response())
    assert not analyze(trade, snap, call=fake).fallback
    retry = fake.calls[1][1]
    assert "roster 12: it has 4 bullets" in retry
    assert "Give the whole response again with exactly 2 sides: roster 11 first, then roster 12, each once" in retry


def test_the_bullets_of_a_side_that_names_its_team_twice_fails(trade, snap):
    team = snap.teams[11].name
    text = f"{team} gets Garrett Wilson. {team} needs a receiver. His target share went up."
    bad = _response(eleven=_side(11, bullets=_split(text)))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert f"roster 11 bullets: team {team} is named 2 times" in fake.calls[1][1]


def test_the_bullets_of_a_side_that_names_each_team_once_passes(trade, snap):
    text = (f"{snap.teams[11].name} gets Garrett Wilson. {snap.teams[12].name} gives him up. "
            "His target share went up.")
    fake = FakeClaude(_response(eleven=_side(11, bullets=_split(text))))
    assert not analyze(trade, snap, call=fake).fallback


def test_the_bullets_of_a_side_that_names_the_other_trade_team_twice_fails(trade, snap):
    team = snap.teams[12].name
    text = f"{team} gives up Garrett Wilson. {team} gets Bhayshul Tuten back. His target share went up."
    bad = _response(eleven=_side(11, bullets=_split(text)))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert f"roster 11 bullets: team {team} is named 2 times" in fake.calls[1][1]


@pytest.mark.parametrize("sentence, failure", [
    ("This side grades B after the trade.", "'grades B' names a letter grade"),
    ("The trade moves this side to a grade C.", "'grade C' names a letter grade"),
    ("Its Letter stays the same.", "the word 'Letter' is not allowed"),
    ("This side graded B before the trade.", "'graded B' names a letter grade"),
    ("This side earns an A grade.", "'an A' names a letter grade"),
    ("This side is C-level after the trade.", "'C-level' names a letter grade"),
])
def test_a_letter_grade_in_a_side_analysis_fails(trade, snap, sentence, failure):
    bullets = ["Garrett Wilson scored 14.2 points per game before the trade.", sentence, "He is a starter."]
    bad = _response(eleven=_side(11, bullets=bullets))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert f"roster 11 bullet 2: {failure}" in fake.calls[1][1]


@pytest.mark.parametrize("reason, failure", [
    ("The asking side grades D, so decline.", "'grades D' names a letter grade"),
    ("The final letter is too low, so decline.", "the word 'letter' is not allowed"),
])
def test_a_letter_grade_in_the_verdict_reason_fails(trade, snap, reason, failure):
    def bad(facts):
        response = _response()(facts)
        response["verdict"]["reason"] = reason
        return response
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert f"verdict reason: {failure}" in fake.calls[1][1]


def test_a_side_that_does_well_in_plain_words_passes(trade, snap):
    text = ("Garrett Wilson scored 14.2 points per game before the trade. This side does well in the trade. "
            "He is a starter.")
    fake = FakeClaude(_response(eleven=_side(11, bullets=_split(text))))
    assert not analyze(trade, snap, call=fake).fallback



def _grade_with_upside(monkeypatch, step):
    """Grade as the code does, with the upside adjuster of roster 11 set to `step`."""
    real_grade = analysis.grade

    def graded(trade, snapshot):
        first, second = real_grade(trade, snapshot)
        adjusters = [a.model_copy(update={"step": step}) if a.name == "upside" else a for a in first.adjusters]
        return first.model_copy(update={"adjusters": adjusters}), second

    monkeypatch.setattr(analysis, "grade", graded)


UPSIDE_TEXT = "Garrett Wilson scored 14.2 points per game before the trade. He has upside. He is a starter."


def test_an_upside_claim_fails_when_the_upside_adjuster_credits_no_one(trade, snap, monkeypatch):
    _grade_with_upside(monkeypatch, 0)
    bad = _response(eleven=_side(11, bullets=_split(UPSIDE_TEXT)))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert "roster 11 bullet 2: 'upside' claims upside" in fake.calls[1][1]


def test_an_upside_claim_passes_when_the_upside_adjuster_credits_a_player(trade, snap, monkeypatch):
    _grade_with_upside(monkeypatch, 1)
    fake = FakeClaude(_response(eleven=_side(11, bullets=_split(UPSIDE_TEXT))))
    assert not analyze(trade, snap, call=fake).fallback

# A three-side trade on the same snapshot: roster 4 sends Nico Collins to roster 11, roster 11 sends Tuten to roster 12
# and Wilson to roster 4, and roster 12 sends Jacobs and Vele to roster 11. Roster 12 asked.
COLLINS = "7569"


@pytest.fixture
def three():
    return ProposedTrade(season=2026, asker=12, sides=[
        TradeSide(roster_id=4, gives=[{"player_id": COLLINS, "to": 11}]),
        TradeSide(roster_id=11, gives=[{"player_id": TUTEN, "to": 12}, {"player_id": WILSON, "to": 4}]),
        TradeSide(roster_id=12, gives=[{"player_id": JACOBS, "to": 11}, {"player_id": VELE, "to": 11}]),
    ])


def _sides_response(trade, snap, rosters):
    """A response that passes every check for the sides of `rosters`, each at the code's final letter."""
    letters = {b.roster_id: b.final_letter for b in grade(trade, snap)}
    return lambda facts: {
        "sides": [_side(roster_id, letter=letters.get(roster_id, "C")) for roster_id in rosters],
        "verdict": {"choice": "decline", "reason": "The trade is fair for both sides."},
    }


def test_a_three_side_output_passes_with_every_side_in_the_order_of_the_trade(three, snap):
    fake = FakeClaude(_sides_response(three, snap, (4, 11, 12)))
    result = analyze(three, snap, call=fake)
    assert len(fake.calls) == 1
    assert not result.fallback
    assert [s.roster_id for s in result.sides] == [4, 11, 12]
    assert [b.roster_id for b in result.breakdowns] == [4, 11, 12]
    assert len(result.standing_letters) == 3


def test_a_two_side_output_for_a_three_side_trade_fails_and_the_retry_names_all_three_sides(three, snap):
    fake = FakeClaude(_sides_response(three, snap, (11, 12)), _sides_response(three, snap, (4, 11, 12)))
    result = analyze(three, snap, call=fake)
    assert len(fake.calls) == 2
    assert not result.fallback
    retry = fake.calls[1][1]
    assert "it had rosters 11, 12" in retry
    assert "exactly 3 sides: roster 4 first, then roster 11, then roster 12, each once" in retry


def test_a_three_side_output_in_the_wrong_order_fails_and_the_retry_names_the_order_of_the_trade(three, snap):
    fake = FakeClaude(_sides_response(three, snap, (12, 4, 11)), _sides_response(three, snap, (4, 11, 12)))
    result = analyze(three, snap, call=fake)
    assert len(fake.calls) == 2
    assert not result.fallback
    retry = fake.calls[1][1]
    assert "it had rosters 12, 4, 11" in retry
    assert "exactly 3 sides: roster 4 first, then roster 11, then roster 12, each once" in retry


def test_the_user_message_names_the_destination_of_each_given_player_and_the_source_of_each_got_player(three, snap):
    fake = FakeClaude(_sides_response(three, snap, (4, 11, 12)))
    analyze(three, snap, call=fake)
    system, user = fake.calls[0]
    team = {roster_id: snap.teams[roster_id].name for roster_id in (4, 11, 12)}
    assert f"Gives: Bhayshul Tuten to {team[12]}, Garrett Wilson to {team[4]}" in user
    assert f"Gets: Nico Collins from {team[4]}, Josh Jacobs from {team[12]}, Devaughn Vele from {team[12]}" in user
    # The rules ask for one side per roster in the order of the user message, for any count of sides.
    assert "one side for each roster in the trade, in the order of the user message" in system


def test_the_prompt_asks_for_two_or_three_bullets_of_one_sentence_each(trade, snap):
    fake = FakeClaude(_response())
    analyze(trade, snap, call=fake)
    # The prompt wraps its lines, so the check reads it as one line.
    system = " ".join(fake.calls[0][0].split())
    assert "Write 2 or 3 bullets for each side. Each bullet is one sentence that makes one claim." in system
    assert "three to five sentences" not in system


# The real 2026 data after week 8, graded in week 9. Trade A: roster 10 gives Omar Cooper Jr. to roster 6 for
# Parker Washington. Roster 10 asks.
SAVED = CLIENT.folder / "data" / "2026"
COOPER, WASHINGTON = "13276", "9487"


@pytest.fixture(scope="module")
def week_9():
    returns_file = returns_path(CLIENT.nfl_dir, 2026)
    return build_snapshot(load_raw(SAVED / "week-08" / "raw"), SAVED / "history", None, trade_week=9,
                          returns=load_returns(returns_file), out_for_season=load_out_for_season(returns_file),
                          client=CLIENT)


@pytest.fixture
def trade_a():
    return ProposedTrade(season=2026, sides=(TradeSide(roster_id=10, gives=[{"player_id": COOPER, "to": 6}]),
                                             TradeSide(roster_id=6, gives=[{"player_id": WASHINGTON, "to": 10}])),
                         asker=10)


def _quote(trade, snapshot, bullets):
    """A response with the code letters and the code verdict, and the bullets for the first side."""
    code = code_only(trade, snapshot)
    letters = {b.roster_id: b.final_letter for b in code.breakdowns}
    plain = ["The trade moves a receiver.", "Both sides get a receiver back."]
    return lambda facts: {
        "sides": [{"roster_id": rid, "final_letter": letters[rid], "reason": None,
                   "bullets": bullets if rid == trade.sides[0].roster_id else plain,
                   "cited": [f"{COOPER}.ppg"]} for rid in letters],
        "verdict": {"choice": code.verdict.choice, "reason": "The trade is close for both sides."},
    }


def test_each_traded_player_carries_his_season_rank_and_his_recent_rank_on_a_large_gap(trade_a, week_9):
    document = result_document(trade_a, week_9, code_only(trade_a, week_9))
    players = {p["player_id"]: p for side in document["trade"]["sides"] for p in side["gives"] + side["gets"]}
    # Cooper: WR60 by total points through week 8, WR18 by points per game over weeks 5 to 8. The gap is 42.
    assert (players[COOPER]["season_rank"], players[COOPER]["recent_rank"]) == ("WR60", "WR18")
    # Washington: WR21 and WR19. The gap is 2, under RECENT_RANK_GAP, so no Recent rank shows.
    assert (players[WASHINGTON]["season_rank"], players[WASHINGTON]["recent_rank"]) == ("WR21", None)
    assert RECENT_RANK_GAP == 12


def test_the_facts_give_the_season_rank_and_the_recent_rank_with_its_label_and_the_checks_accept_them(
        trade_a, week_9):
    bullets = ["Omar Cooper Jr. is WR60 this season.", "His Recent rank is WR18.", "He moves to a new roster."]
    fake = FakeClaude(_quote(trade_a, week_9, bullets))
    result = analyze(trade_a, week_9, call=fake)
    facts = _facts(fake.calls[0][1])
    assert "His Season rank is WR60, by total points this season." in facts[f"{COOPER}.ppg"]
    assert "His Recent rank is WR18, by points per game over the last 4 weeks." in facts[f"{COOPER}.ppg"]
    assert "His Season rank is WR21, by total points this season." in facts[f"{WASHINGTON}.ppg"]
    assert "Recent rank" not in facts[f"{WASHINGTON}.ppg"]
    # No Position rank number: the grade measure is WR27 for Cooper, and no fact gives it.
    assert "27" not in facts[f"{COOPER}.ppg"] and "by points per game." not in facts[f"{COOPER}.ppg"]
    assert not result.fallback and len(fake.calls) == 1


def test_the_fact_sheet_has_no_slot_fact(trade_a, week_9):
    facts = trade_fact_sheet(trade_a, week_9)
    assert not [fid for fid in facts if fid.endswith(".slot")]
    assert not [f.text for f in facts.values() if "sits on the bench" in f.text or " takes " in f.text]
