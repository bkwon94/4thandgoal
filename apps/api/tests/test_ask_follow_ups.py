"""
The live route of a short follow-up after a start or sit answer: "you sure?" and "thank you" get an answer, not a miss.
An off-topic ask with the same turns still routes to a miss. Run it with `pytest -m live -s tests/test_ask_follow_ups.py`.
"""
import json
from pathlib import Path

import pytest

from cornerstone_api.ask import route_question
from cornerstone_api.chat_turns import Turn
from league.jev import JEV

QUESTIONS = Path(__file__).parent / "fixtures" / "route-questions.json"
# The turns of a start or sit answer, as the site sends them after "Start Golden or Mumpfield?".
START_SIT_TURNS = [Turn(question="Start Golden or Mumpfield?",
                        answer="Start Konata Mumpfield. His 6.8 projection trails, but the read of his matchup is "
                               "better. Start the rest of your lineup by projection.")]
# Each question, and whether its route must be a miss.
CASES = [("you sure?", False), ("thank you", False), ("write me a poem", True)]


@pytest.mark.live
@pytest.mark.parametrize(("question", "miss"), CASES)
def test_a_follow_up_after_a_start_or_sit_answer_routes_to_a_miss_only_when_off_topic(question: str, miss: bool):
    data = json.loads(QUESTIONS.read_text())
    route = route_question(JEV, question, data["teams"], data["season"], data["week"], START_SIT_TURNS)
    print(f"\n{question!r}: {route.kind} {route.topic} {route.jev.nouls}")
    assert (route.kind == "miss") is miss, f"{question!r} routed to {route.kind}"
