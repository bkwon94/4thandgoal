"""
The live route eval of the ask box (AT-17): the 62 questions of decision 09, H6, H13, H18, and H28 go to the real Jev through
the route of ask.py, and the test fails below 52 hits of the 59 questions with an expected route. Run it with `pytest -m live -s`.
The site set (AT-9 of site-answer) holds the 22 site questions and the 18 traps of its decision 01.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from cornerstone_api.ask import Route, route_question
from cornerstone_api.ask_wording import site_page_line
from cornerstone_api.chat_turns import Turn
from league.jev import JEV
from league.jev_port import JevError

QUESTIONS = Path(__file__).parent / "fixtures" / "route-questions.json"
# The spec asks for at least 35 of 40, a share of 87.5%. The bar keeps that share over the 59 scored questions, rounded
# up to 52. It asserts no single probability.
SCORED = 59
HITS_NEEDED = 52
# The spec of site-answer asks for at least 20 of the 22 site questions on the site route, each with its right page,
# and for no one of the 18 traps on the site route. Brian lets one trap reach its page: "show me the power rankings"
# scored 0.78 to 0.81 on the site Noul, and its Site answer links to the same page as its Topic Answer (PRD item 6).
SITE_QUESTIONS = 22
SITE_HITS_NEEDED = 20
TRAPS = 18
TRAP_PAGES = {"show me the power rankings": "site:rankings"}


def _site_pages(pages: list[dict]) -> dict[str, str]:
    """The `site_pages` of the state, from the pages of the fixture as the site sends them."""
    return {page["key"]: site_page_line(page["label"], page["blurb"]) for page in pages}


def _hit(expect: str, route: Route) -> bool:
    if expect.startswith("site:"):
        return route.kind == "site" and f"site:{route.page}" in expect.split("|")
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
    if route.kind == "site":
        return f"site:{route.page}"
    return route.kind


@pytest.mark.live
def test_the_route_eval_hits_at_least_52_of_59():
    data = json.loads(QUESTIONS.read_text())
    teams = data["teams"]
    # The site sends the pages of the client with each question, so the old bar holds with them in the state.
    pages = _site_pages(data["pages"])

    def ask(question: dict) -> Route | str:
        try:
            # A follow-up case holds the earlier turns of its Thread, as the site sends them.
            turns = [Turn(**turn) for turn in question.get("turns", [])]
            return route_question(JEV, question["text"], teams, data["season"], data["week"], turns, pages)
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
    assert scored == SCORED
    assert hits >= HITS_NEEDED


@pytest.mark.live
def test_the_site_set_routes_20_of_22_site_questions_to_their_page_and_keeps_each_trap():
    data = json.loads(QUESTIONS.read_text())
    site = data["site"]
    pages = _site_pages(site["pages"])

    def ask(question: dict) -> Route | str:
        try:
            return route_question(JEV, question["text"], data["teams"], site["season"], site["week"], None, pages)
        except JevError as error:  # a failed request is an error row, never a hit
            return f"ERROR {error}"

    with ThreadPoolExecutor(max_workers=8) as pool:
        routes = list(pool.map(ask, site["questions"]))
    lines = ["| # | Question | Source | Expect | Route | site | Old route | Hit |", "|---|---|---|---|---|---|---|---|"]
    site_hits = site_count = traps_kept = trap_count = old_hits = 0
    for question, route in zip(site["questions"], routes, strict=True):
        expect = question["expect"]
        nouls = route.jev.nouls if isinstance(route, Route) else {}
        is_route = isinstance(route, Route)
        if expect.startswith("site:"):
            site_count += 1
            hit = is_route and _hit(expect, route)
            site_hits += hit
            old = "-"
        else:
            # A trap keeps its old route when the site row does not take it. The old table under it does not change.
            trap_count += 1
            allowed = TRAP_PAGES.get(question["text"])
            hit = is_route and (route.kind != "site" or (allowed is not None and _hit(allowed, route)))
            traps_kept += hit
            old_hit = is_route and _hit(expect, route)
            old_hits += old_hit
            old = "yes" if old_hit else "no"
        score = f"{nouls['asks_for_site']:.2f}" if "asks_for_site" in nouls else "-"
        cells = [str(question["id"]), question["text"], question["source"], expect, _shown(route), score, old,
                 "yes" if hit else "no"]
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |")
    models = sorted({route.jev.model for route in routes if isinstance(route, Route)})
    print("\n".join(lines))
    print(f"\nSite hits: {site_hits} of {site_count}. Traps kept: {traps_kept} of {trap_count}. Traps on their"
          f" expected route: {old_hits} of {trap_count}. Model: {', '.join(models) or 'none'}.")
    assert (site_count, trap_count) == (SITE_QUESTIONS, TRAPS)
    assert site_hits >= SITE_HITS_NEEDED
    assert traps_kept == TRAPS
