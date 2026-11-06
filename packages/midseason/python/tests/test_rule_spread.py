"""
The rules of the spread rule, on small hand-built headlines: a callout names the #1 team with room, a team with 3
headlines passes a callout to the next team, arcs and awards never move, and a team with none takes a callout.
"""
from facts.tokens import Nums, fact
from league.models import FactSheet
from midseason.prose import prose_sheet
from midseason.review import review_text
from midseason.spread import Callout, Headline, callout_facts, moved_off, spread_rule, spread_warnings
from midseason.state import LeagueState, TeamState

TEAMS = [1, 2, 3, 4]
NAMES = {1: "One", 2: "Two", 3: "Three", 4: "Four"}


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


def test_a_team_with_no_headline_takes_a_callout_from_a_holder_with_1_that_takes_another_callout():
    fixed = [_arc(1, "collapse"), _arc(1, "snakebit")]
    callouts = [Callout(key="draft.steal", chapter="draft", ranking=[2, 3]),
                Callout(key="waivers.hit", chapter="waivers", ranking=[1, 2])]
    headlines = spread_rule(fixed, callouts, [1, 2, 3])
    # Team 3 ranks only for the steal, and team 2 holds only the steal. Team 2 takes the waiver hit from team 1, which
    # keeps its 2 arcs, so team 3 takes the steal.
    assert _holders(headlines) == {"draft.steal": 3, "waivers.hit": 2}
    assert {h.key: h.place for h in headlines if h.kind == "callout"} == {"draft.steal": 2, "waivers.hit": 2}
    assert spread_warnings(headlines, [1, 2, 3], NAMES) == []


def test_a_team_that_no_callout_can_reach_keeps_no_headline_and_the_review_file_warns():
    fixed = [_arc(1, "collapse")]
    headlines = spread_rule(fixed, [Callout(key="trades.top", chapter="trades", ranking=[2])], [1, 2, 3])
    assert _holders(headlines) == {"trades.top": 2}
    warnings = spread_warnings(headlines, [1, 2, 3], NAMES)
    assert warnings == ["Spread rule: Three holds no headline. No callout ranks it with a holder to spare."]
    assert f"Warning. {warnings[0]}" in _review(warnings)


def test_a_callout_that_no_team_has_room_for_names_no_team():
    fixed = [_arc(1, "a"), _arc(1, "b"), _award(1, "c")]
    headlines = spread_rule(fixed, [Callout(key="trades.top", chapter="trades", ranking=[1])], [1])
    assert _holders(headlines) == {}


def _review(warnings: list[str]) -> str:
    return review_text(2026, 8, "hot", FactSheet(facts={}, chapters=[]), {}, {}, "make midseason-publish",
                       warnings=warnings)


def test_a_team_with_more_than_3_arcs_and_awards_keeps_them_takes_no_callout_and_the_review_file_warns():
    fixed = [_arc(1, "collapse"), _arc(1, "snakebit"), _award(1, "mvp"), _award(1, "most-active"),
             _arc(2, "heater"), _arc(3, "turnaround"), _arc(4, "heater")]
    callouts = [Callout(key="waivers.hit", chapter="waivers", ranking=[1, 2, 3, 4])]
    headlines = spread_rule(fixed, callouts, TEAMS)
    assert [h for h in headlines if h.kind != "callout"] == fixed
    assert _holders(headlines) == {"waivers.hit": 2}
    assert _counts(headlines)[1] == 4
    warnings = spread_warnings(headlines, TEAMS, NAMES)
    assert warnings == [("Spread rule: One holds 4 headlines, more than 3: arc.collapse, arc.snakebit, award.mvp, "
                         "award.most-active. Arcs and awards never move.")]
    assert f"Warning. {warnings[0]}" in _review(warnings)


def test_a_moved_team_stays_in_the_scope_and_the_facts_of_its_block_and_the_sheet_names_the_holder():
    state = LeagueState(teams=[TeamState(roster_id=rid, name=name, rank=rid, wins=1, losses=1, ties=0, points_for=1.0,
                                         points_against=1.0, streak=None, playoff_odds=None)
                               for rid, name in ((1, "One"), (2, "Two"))])
    callouts = [Callout(key="luck.most_better", chapter="luck", ranking=[1, 2])]
    headlines = [Headline(kind="callout", key="luck.most_better", chapter="luck", roster_id=2, place=2)]
    notes = callout_facts(headlines, callouts, {1: "One", 2: "Two"})
    later = [("luck", "Schedule luck", [fact("SW.1", "One is lucky.", Nums(), ["One"], []),
                                        fact("SW.2", "Two is lucky.", Nums(), ["Two"], [])])]
    sheet = prose_sheet(1, state, "off", later, callouts=notes)
    luck = next(chapter for chapter in sheet.chapters if chapter.key == "luck")
    assert luck.fact_ids == ["SW.1", "SW.2", "CO.luck.most_better", "W.week"]
    assert luck.scope_teams == ["One", "Two"]
    note = sheet.facts["CO.luck.most_better"]
    assert note.text == ("The callout of the most schedules better than its own names Two. One is not the headline of "
                         "this callout.")
    assert note.teams == ["Two", "One"]
