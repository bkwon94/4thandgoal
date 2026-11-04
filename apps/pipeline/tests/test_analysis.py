"""
Tests for the Claude call of the trade analyzer: the fact sheet, the checks, the retry, and the fallback.
They feed the Josh Jacobs trade and the week 6 snapshot to analyze, with a fake in place of Claude.
"""
import logging
import re
import shutil

import pytest
from conftest import with_free_agents
from cpc import cpc_client

from cornerstone import analysis
from cornerstone.analysis import AnalysisOut, analyze
from cornerstone.provider.sleeper import load_raw
from cornerstone.rubric import ProposedTrade, TradeSide, grade
from cornerstone.slow_sources import load_slow_sources
from cornerstone.snapshot import build_snapshot, load_returns, load_snapshot

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
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CLIENT)
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
    snap = build_snapshot(raw, fixture_history_root, chart_week6, slow,
                          returns=load_returns(fixture_history_root.parent / "returns.json"), client=CLIENT)
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


def _side(roster_id, letter=None, reason=None, analysis=None, cited=None):
    return {
        "roster_id": roster_id, "final_letter": letter or JACOBS_CODE_LETTERS[roster_id], "reason": reason,
        "analysis": analysis or ("Garrett Wilson scored 14.2 points per game before the trade. "
                                 "His target share went up. The trade moves him to a new roster."),
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
    assert "14.2 points per game" in facts[f"{WILSON}.ppg"] and "season rank 7 of 90" in facts[f"{WILSON}.ppg"]
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
    assert result.sides[0].analysis.startswith("Garrett Wilson scored 14.2 points per game")
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
    assert [s.analysis for s in result.sides] == ["Analysis unavailable", "Analysis unavailable"]
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
    bad = _response(eleven=_side(11, analysis=analysis, cited=[f"{WILSON}.ppg", f"{WILSON}.value"]))
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
    text = f"Garrett Wilson scored 14.2 points per game before the trade. {sentence} He is a starter."
    fake = FakeClaude(_response(eleven=_side(11, analysis=text)))
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
    text = f"Garrett Wilson scored 14.2 points per game before the trade. {sentence} He is a starter."
    bad = _response(eleven=_side(11, analysis=text))
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
    fake = FakeClaude(_response(eleven=_side(11, analysis=text)))
    assert not analyze(trade, snap, call=fake).fallback
    assert len(fake.calls) == 1


def test_the_points_per_game_fact_names_the_position_rank_and_the_checker_accepts_a_quote_of_it(trade, snap):
    # The hand count of the RB lines in weeks 2 to 5 puts Tuten 15th. Jacobs is due back, so his projection ahead
    # of weeks 7 to 14 puts him 16th.
    fake = FakeClaude(_response(eleven=_side(11, analysis=(
        "Bhayshul Tuten is RB15 by points per game. His snap share went up. He moves to a new roster."),
        cited=[f"{TUTEN}.ppg"])))
    result = analyze(trade, snap, call=fake)
    facts = _facts(fake.calls[0][1])
    assert "Bhayshul Tuten is RB15 by points per game." in facts[f"{TUTEN}.ppg"]
    assert "Josh Jacobs is RB16 by his projection ahead." in facts[f"{JACOBS}.ppg"]
    assert not result.fallback
    assert len(fake.calls) == 1


def test_the_checker_accepts_a_sentence_that_quotes_a_cited_depth_count_or_strength_count(trade, snap):
    # Roster 11 gives Wilson WR12 and gets Vele, so it holds 1 receiver above the line after, from 2.
    # Tuten RB15 and Wilson leave its RB1, RB2, WR1, and WR2 starters, and Jacobs RB16 and Vele come in.
    text = ("Josh Jacobs takes RB2 on this side. WR depth above the line goes from 2 to 1. "
            "Its starters with a position rank of 24 or better go from 4 to 3.")
    fake = FakeClaude(_response(eleven=_side(11, analysis=text,
                                             cited=[f"{JACOBS}.slot", "11.depth.wr", "11.strength"])))
    result = analyze(trade, snap, call=fake)
    facts = _facts(fake.calls[0][1])
    assert facts[f"{JACOBS}.slot"] == "Josh Jacobs takes RB2, which Bhayshul Tuten held before the trade."
    assert facts[f"{VELE}.slot"] == "Devaughn Vele takes WR2, and George Pickens moves to WR1."
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
    fake = FakeClaude(_response(eleven=_side(11, analysis=text, cited=["11.hole.wr2"])))
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
    bad = _response(eleven=_side(11, analysis=text, cited=["11.hole.wr2"]))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, fa_snap, call=fake).fallback
    assert "number 31 is not in the cited facts" in fake.calls[1][1]


def test_a_count_that_no_cited_depth_fact_holds_fails(trade, snap):
    # The depth fact of roster 11 holds 2 and 1, and no breakdown reason holds 38, so a count of 38 is a new number.
    text = "Josh Jacobs takes RB2 on this side. WR depth above the line goes from 38 to 1. He starts."
    bad = _response(eleven=_side(11, analysis=text, cited=[f"{JACOBS}.slot", "11.depth.wr"]))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert "number 38 is not in the cited facts" in fake.calls[1][1]


def test_a_share_percent_from_the_trend_reason_is_allowed(trade, snap):
    # The trend reason of roster 11 gives Tuten's snap share of 64% over weeks 4 and 5. No cited fact holds 64.
    text = ("Garrett Wilson scored 14.2 points per game before the trade. "
            "Bhayshul Tuten took 64% of the snaps over weeks 4 and 5. He starts.")
    fake = FakeClaude(_response(eleven=_side(11, analysis=text, cited=[f"{WILSON}.ppg"])))
    result = analyze(trade, snap, call=fake)
    trend = next(a for a in result.breakdowns[0].adjusters if a.name == "trend and usage")
    assert "Tuten: snap share 64%, up, over weeks 4 and 5." in trend.reason
    assert "64" not in _facts(fake.calls[0][1])[f"{WILSON}.ppg"]
    assert not result.fallback
    assert len(fake.calls) == 1


def test_the_log_line_holds_no_number_from_the_failure(trade, snap, caplog):
    text = "Garrett Wilson is worth 27.5 to this roster. His target share went up. He is a starter."
    bad = _response(eleven=_side(11, analysis=text, cited=[f"{WILSON}.ppg", f"{WILSON}.value"]))
    fake = FakeClaude(bad, bad)
    with caplog.at_level(logging.WARNING, logger="cornerstone.analysis"):
        assert analyze(trade, snap, call=fake).fallback
    # The retry feedback to Claude keeps the full failure text.
    assert "number 27.5 is not in the cited facts" in fake.calls[1][1]
    records = [r.getMessage() for r in caplog.records if r.name == "cornerstone.analysis"]
    assert len(records) == 2
    for message in records:
        assert "failed" in message
        assert not re.search(r"\d", message.split("failed", 1)[1])


@pytest.mark.parametrize("analysis_text", [
    # The period in a name ends no sentence.
    ("Amon-Ra St. Brown is not in the trade. Garrett Wilson starts. His target share went up. "
     "He moves to a new roster. He is a starter."),
    # The period in a decimal ends no sentence.
    ("Garrett Wilson scored 14.2 points per game before the trade. He starts. His target share went up. "
     "He moves to a new roster. He is a starter."),
    # Claude writes the short form of a name, a suffix, and "vs." with a decimal in the same analysis.
    ("St. Brown is not in the trade, and Garrett Wilson scored 14.2 points per game. Harrison Jr. lost snaps. "
     "Garrett Wilson vs. Devaughn Vele is close. St. Brown stays put. He is a starter."),
    # A run of initials ends no sentence, in a full name and in a form the snapshot does not hold.
    ("Garrett Wilson starts. A.J. Brown is not in the trade. D.J. Moore is not in it either. "
     "His target share went up. He is a starter."),
])
def test_a_period_in_a_name_or_a_decimal_ends_no_sentence(trade, snap, analysis_text):
    # Five sentences pass. A miscount gives six, which fails.
    assert "Amon-Ra St. Brown" in {p.name for p in snap.players.values()}
    fake = FakeClaude(_response(eleven=_side(11, analysis=analysis_text)))
    assert not analyze(trade, snap, call=fake).fallback


@pytest.mark.parametrize("analysis", [
    "Garrett Wilson scored 14.2 points per game before the trade. He is a starter.",
    "One. Two. Three. Four. Five. Six.",
])
def test_an_analysis_outside_three_to_five_sentences_fails(trade, snap, analysis):
    bad = _response(twelve=_side(12, analysis=analysis))
    assert analyze(trade, snap, call=FakeClaude(bad, bad)).fallback


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
    from cornerstone.writer import RefusalError

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
    # A sentence count failure on one side must not lead Claude to send that side alone.
    six_sentences = "One. Two. Three. Four. Five. Six."
    fake = FakeClaude(_response(twelve=_side(12, analysis=six_sentences)), _response())
    assert not analyze(trade, snap, call=fake).fallback
    retry = fake.calls[1][1]
    assert "roster 12: the analysis has 6 sentences" in retry
    assert "Give the whole response again with exactly 2 sides: roster 11 first, then roster 12, each once" in retry


def test_a_side_analysis_that_names_its_team_twice_fails(trade, snap):
    team = snap.teams[11].name
    text = f"{team} gets Garrett Wilson. {team} needs a receiver. His target share went up."
    bad = _response(eleven=_side(11, analysis=text))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert f"roster 11 analysis: team {team} is named 2 times" in fake.calls[1][1]


def test_a_side_analysis_that_names_each_team_once_passes(trade, snap):
    text = (f"{snap.teams[11].name} gets Garrett Wilson. {snap.teams[12].name} gives him up. "
            "His target share went up.")
    fake = FakeClaude(_response(eleven=_side(11, analysis=text)))
    assert not analyze(trade, snap, call=fake).fallback


def test_a_side_analysis_that_names_the_other_trade_team_twice_fails(trade, snap):
    team = snap.teams[12].name
    text = f"{team} gives up Garrett Wilson. {team} gets Bhayshul Tuten back. His target share went up."
    bad = _response(eleven=_side(11, analysis=text))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert f"roster 11 analysis: team {team} is named 2 times" in fake.calls[1][1]


@pytest.mark.parametrize("sentence, failure", [
    ("This side grades B after the trade.", "'grades B' names a letter grade"),
    ("The trade moves this side to a grade C.", "'grade C' names a letter grade"),
    ("Its Letter stays the same.", "the word 'Letter' is not allowed"),
    ("This side graded B before the trade.", "'graded B' names a letter grade"),
    ("This side earns an A grade.", "'an A' names a letter grade"),
    ("This side is C-level after the trade.", "'C-level' names a letter grade"),
])
def test_a_letter_grade_in_a_side_analysis_fails(trade, snap, sentence, failure):
    text = f"Garrett Wilson scored 14.2 points per game before the trade. {sentence} He is a starter."
    bad = _response(eleven=_side(11, analysis=text))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert f"roster 11 analysis: {failure}" in fake.calls[1][1]


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
    fake = FakeClaude(_response(eleven=_side(11, analysis=text)))
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
    bad = _response(eleven=_side(11, analysis=UPSIDE_TEXT))
    fake = FakeClaude(bad, bad)
    assert analyze(trade, snap, call=fake).fallback
    assert "roster 11 analysis: 'upside' claims upside" in fake.calls[1][1]


def test_an_upside_claim_passes_when_the_upside_adjuster_credits_a_player(trade, snap, monkeypatch):
    _grade_with_upside(monkeypatch, 1)
    fake = FakeClaude(_response(eleven=_side(11, analysis=UPSIDE_TEXT)))
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
