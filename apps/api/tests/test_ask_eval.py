"""
The live route eval of the ask box (AT-17): the 49 questions of decision 09, H6, and H13 go to the real Jev through the
route of ask.py, and the test fails below 41 hits of the 46 questions with an expected route. Run it with `pytest -m live -s`.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from cornerstone_api.ask import Route, route_question
from league.jev import JEV
from league.jev_port import JevError

QUESTIONS = Path(__file__).parent / "fixtures" / "route-questions.json"
# The spec asks for at least 35 of 40, a share of 87.5%. The bar keeps that share over the 46 scored questions, rounded
# up to 41. It asserts no single probability.
HITS_NEEDED = 41


def _hit(expect: str, route: Route) -> bool:
    if expect.startswith("team:"):
        return route.team == expect.removeprefix("team:")
    if expect.startswith("topic:"):
        return route.kind == "topic" and route.topic == expect.removeprefix("topic:")
    return route.kind == {"free_answer": "free", "miss": "miss", "refuse": "refuse"}[expect]


def _shown(route: Route | str) -> str:
    if isinstance(route, str):
        return route
    if route.kind == "topic":
        return f"topic:{route.topic}"
    if route.kind == "free":
        return f"free (Suggestion {route.suggestion})" if route.suggestion else "free"
    if route.kind == "miss":
        return f"miss [{', '.join(route.closest)}]"
    return route.kind


@pytest.mark.live
def test_the_route_eval_hits_at_least_41_of_46():
    data = json.loads(QUESTIONS.read_text())
    teams = data["teams"]

    def ask(question: dict) -> Route | str:
        try:
            return route_question(JEV, question["text"], teams, data["season"], data["week"])
        except JevError as error:  # a failed request is an error row, never a hit
            return f"ERROR {error}"

    with ThreadPoolExecutor(max_workers=8) as pool:
        routes = list(pool.map(ask, data["questions"]))
    lines = ["| # | Question | Source | Expect | Route | Team | fits | data | about | abuse | Hit |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    hits = scored = 0
    for question, route in zip(data["questions"], routes, strict=True):
        expect = question["expect"]
        nouls = route.jev.nouls if isinstance(route, Route) else {}
        hit = "?" if expect == "judgment" else "yes" if isinstance(route, Route) and _hit(expect, route) else "no"
        if expect != "judgment":
            scored += 1
            hits += hit == "yes"
        team = route.team if isinstance(route, Route) else None
        cells = [str(question["id"]), question["text"], question["source"], expect, _shown(route), team or "-",
                 *(f"{nouls[key]:.2f}" if key in nouls else "-"
                   for key in ("fits_topic", "data_can_answer", "about_league", "abuse")), hit]
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |")
    models = sorted({route.jev.model for route in routes if isinstance(route, Route)})
    print("\n".join(lines))
    print(f"\nHits: {hits} of {scored}. Model: {', '.join(models) or 'none'}.")
    assert scored == 46
    assert hits >= HITS_NEEDED
