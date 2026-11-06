"""
The rules of the spread rule, on small hand-built headlines: a callout names the #1 team with room, a team with 3
headlines passes a callout to the next team, arcs and awards never move, and a team with none takes a callout.
"""
from facts.tokens import Nums, fact
from midseason.prose import prose_sheet
from midseason.spread import Callout, Headline, moved_off, spread_rule
from midseason.state import LeagueState, TeamState

TEAMS = [1, 2, 3, 4]


def _arc(roster_id: int, kind: str) -> Headline:
    return Headline(kind="arc", key=f"arc.{kind}", chapter="arcs", roster_id=roster_id)


def _award(roster_id: int, key: str) -> Headline:
    return Headline(kind="award", key=f"award.{key}", chapter="records", roster_id=roster_id)


def _holders(headlines: list[Headline]) -> dict[str, int]:
    return {h.key: h.roster_id for h in headlines if h.kind == "callout"}


def _counts(headlines: list[Headline]) -> dict[int, int]:
    return {rid: sum(h.roster_id == rid for h in headlines) for rid in TEAMS}


def test_a_callout_names_the_first_team_of_its_ranking_with_room():
    fixed = [_arc(1, "collapse"), _arc(2, "heater"), _arc(3, "snakebit"), _arc(4, "heater")]
    headlines = spread_rule(fixed, [Callout(key="luck.most_better", chapter="luck", ranking=[2, 1, 3, 4])], TEAMS)
    assert _holders(headlines) == {"luck.most_better": 2}
    assert next(h for h in headlines if h.kind == "callout").place == 1


def test_a_team_with_3_headlines_passes_the_callout_to_the_next_team_and_keeps_its_arcs_and_awards():
    fixed = [_arc(1, "collapse"), _arc(1, "snakebit"), _award(1, "most-active"), _arc(2, "heater"),
             _arc(3, "turnaround"), _arc(4, "heater")]
    callouts = [Callout(key="luck.most_better", chapter="luck", ranking=[1, 3, 2, 4]),
                Callout(key="luck.biggest_miss", chapter="luck", ranking=[1, 2, 3, 4])]
    headlines = spread_rule(fixed, callouts, TEAMS)
    assert _holders(headlines) == {"luck.most_better": 3, "luck.biggest_miss": 2}
    assert [h for h in headlines if h.kind != "callout"] == fixed
    assert next(h for h in headlines if h.key == "luck.most_better").place == 2
    assert moved_off(headlines, callouts) == {"luck": {1}}


def test_a_team_with_no_headline_takes_the_callout_where_it_ranks_best_from_a_team_with_two_or_more():
    fixed = [_arc(1, "collapse"), _arc(2, "heater"), _arc(3, "turnaround")]
    callouts = [Callout(key="injuries.toll", chapter="injuries", ranking=[1, 2, 3, 4]),
                Callout(key="draft.steal", chapter="draft", ranking=[2, 4, 1, 3])]
    headlines = spread_rule(fixed, callouts, TEAMS)
    # Team 4 ranks 2nd for the steal and 4th for the toll, so it takes the steal from team 2.
    assert _holders(headlines) == {"injuries.toll": 1, "draft.steal": 4}
    assert all(1 <= count <= 3 for count in _counts(headlines).values())
    assert moved_off(headlines, callouts) == {"draft": {2}}


def test_a_callout_that_no_team_has_room_for_names_no_team():
    fixed = [_arc(1, "a"), _arc(1, "b"), _award(1, "c")]
    headlines = spread_rule(fixed, [Callout(key="trades.top", chapter="trades", ranking=[1])], [1])
    assert _holders(headlines) == {}


def test_the_prose_block_of_a_chapter_cannot_name_a_team_that_the_rule_moved_off_its_callout():
    state = LeagueState(teams=[TeamState(roster_id=rid, name=name, rank=rid, wins=1, losses=1, ties=0, points_for=1.0,
                                         points_against=1.0, streak=None, playoff_odds=None)
                               for rid, name in ((1, "One"), (2, "Two"))])
    later = [("luck", "Schedule luck", [fact("SW.1", "One is lucky.", Nums(), ["One"], []),
                                        fact("SW.2", "Two is lucky.", Nums(), ["Two"], []),
                                        fact("SW.both", "One met Two.", Nums(), ["One", "Two"], [])]),
             ("arcs", "Arcs", [fact("ARC.1", "One has an arc.", Nums(), ["One"], [])])]
    sheet = prose_sheet(1, state, "off", later, moved={"luck": {"One"}})
    blocks = {chapter.key: chapter for chapter in sheet.chapters}
    assert blocks["luck"].fact_ids == ["SW.2", "W.week"]
    assert blocks["luck"].scope_teams == ["Two"]
    # The rule moves only the callouts of its chapter, so the arcs still name the team.
    assert "ARC.1" in blocks["arcs"].fact_ids and "One" in blocks["arcs"].scope_teams
