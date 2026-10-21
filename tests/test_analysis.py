"""
Tests for the Claude call of the trade analyzer: the fact sheet, the checks, the retry, and the fallback.
They feed the Josh Jacobs trade and the week 6 snapshot to analyze, with a fake in place of Claude.
"""
import logging
import re
import shutil

import pytest

from cornerstone import analysis
from cornerstone.analysis import AnalysisOut, analyze
from cornerstone.rubric import ProposedTrade, TradeSide
from cornerstone.slow_sources import load_slow_sources
from cornerstone.snapshot import load_snapshot

# The week 6 Josh Jacobs trade: roster 11 gives Bhayshul Tuten and Garrett Wilson to roster 12
# for Jacobs and Devaughn Vele. Roster 12 asked. Chart values: Tuten 3.0, Wilson 27.5, Jacobs 11.5, Vele 55.0.
TUTEN, WILSON, JACOBS, VELE = "12490", "8146", "5850", "11834"


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    """The week 6 snapshot with the slow sources, set back to before the Jacobs trade."""
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow)
    rosters = dict(snap.rosters)
    rosters[11] = [pid for pid in rosters[11] if pid not in (JACOBS, VELE)] + [TUTEN, WILSON]
    rosters[12] = [pid for pid in rosters[12] if pid not in (TUTEN, WILSON)] + [JACOBS, VELE]
    return snap.model_copy(update={"rosters": rosters})


@pytest.fixture
def trade():
    return ProposedTrade(season=2026, sides=(TradeSide(roster_id=11, gives=[TUTEN, WILSON]),
                                             TradeSide(roster_id=12, gives=[JACOBS, VELE])), asker=12)


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
    # Points per game and position rank, before the trade only.
    assert "14.2 points per game" in facts[f"{WILSON}.ppg"] and "position rank 7 of 90" in facts[f"{WILSON}.ppg"]
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
    "Amon-Ra St. Brown is not in the trade. Garrett Wilson starts. His target share went up. "
    "He moves to a new roster. He is a starter.",
    # The period in a decimal ends no sentence.
    "Garrett Wilson scored 14.2 points per game before the trade. He starts. His target share went up. "
    "He moves to a new roster. He is a starter.",
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
