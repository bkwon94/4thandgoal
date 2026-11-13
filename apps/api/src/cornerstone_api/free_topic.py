"""
The Topic block of a free answer: the block of one Topic of the site for Your team, as a data tool result and as the
ready block that code builds, with no Jev read and no analyzer run. A block that needs one stays out.
"""
import json
from typing import Literal, get_args

import httpx

from cornerstone_api.free_tools import SeasonData
from cornerstone_api.free_wording import LINEUP_BY_PROJECTION, TOPIC_MEANINGS
from cornerstone_api.next_matchup import league_spread, matchup_card
from cornerstone_api.personal_facts import PersonalTopic
from cornerstone_api.personal_wording import FACT_MEANINGS
from league.paths import week_label

# The Topics whose block code builds with no Jev read and no analyzer run. The waiver list, the sell list, the trade
# card, the comparison of two players, and the lineup with its Swaps each need one, so a free answer gives them as text.
TopicBlock = Literal["week_recap", "last_matchup", "power_rankings", "playoff_race", "your_season", "weak_spots",
                     "stack_up", "start_sit", "next_matchup"]
# The league Topics, whose block the weekly build writes in topics.json.
LEAGUE_TOPICS = ("week_recap", "last_matchup", "power_rankings", "playoff_race", "your_season")
# The personal Topics, whose block the live league gives: the bye grid of weak_spots and the slot rank bars of stack_up.
GRADE_TOPICS: dict[str, PersonalTopic] = {"weak_spots": "weak_spots", "stack_up": "stack_up"}
TOPICS_FILE = "topics.json"


def _league(data: SeasonData, topic: str, roster_id: int) -> dict:
    """The Answer of a league Topic for the roster, from the Topics file of the latest published week up to the week of
    the answer. The weekly build wrote its facts, its checked text, and its block."""
    if data.client_folder is None:
        return {"error": "The weekly league Topics are not available."}
    season_dir = data.client_folder / "published" / str(data.season)
    for week in range(data.week, 0, -1):
        path = season_dir / week_label(week) / TOPICS_FILE
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        week = payload.get("week", week)
        answers = payload["teams"].get(str(roster_id), [])
        answer = next((each for each in answers if each["topic"] == topic), None)
        if answer is None:
            return {"error": f"Week {week} has no {topic} for this team."}
        block = answer.get("block")
        result = {"week": week, "fact": answer.get("fact"), "stats": answer.get("stats"), "rows": answer.get("rows"),
                  "text": answer.get("text")}
        # A week that the weekly build wrote before the blocks has its facts and no block, so the answer is text.
        return result if block is None else {**result, "card": block, "block": block}
    return {"error": f"No week up to week {data.week} has the weekly league Topics."}


def _grade(data: SeasonData, topic: PersonalTopic, roster_id: int) -> dict:
    """The facts and the block of weak_spots or stack_up for the roster, from the live league that stack_up reads."""
    if data.fetch_personal is None:
        return {"error": "The live roster grades are not available."}
    try:
        facts = data.fetch_personal(topic, roster_id)
    except ValueError:
        return {"error": "The live roster grades did not load."}
    block = facts.block["block"]
    return {"team_facts": facts.slice, "what_each_fact_means": FACT_MEANINGS, "card": block, "block": block}


def _live(data: SeasonData, topic: str, roster_id: int) -> dict:
    """The lineup by projection of the live week, or the live matchup card by projection, for the roster."""
    try:
        week = data.live_week()
    except (ValueError, httpx.HTTPError):
        return {"error": "The live week did not load."}
    if topic == "start_sit":
        facts = week.facts(roster_id)
        return {"team_facts": facts.slice, "by_projection": LINEUP_BY_PROJECTION, "block": facts.block}
    spread = None if data.client_folder is None else league_spread(data.client_folder, data.season)
    card = matchup_card(week, roster_id, spread, None)
    if card is None:
        return {"error": f"Your team has no game in week {week.raw.state.display_week}."}
    block = card.model_dump(mode="json")
    # The time of the read changes with each request, so it stays out of the result, and a kept answer still matches.
    shown = {key: value for key, value in block.items() if key != "read_at"}
    return {"week": week.raw.state.display_week, "card": shown, "by_projection": LINEUP_BY_PROJECTION, "block": block}


def topic_block(data: SeasonData, topic: str) -> dict:
    """The facts of one Topic for Your team, with the block of the same facts under `block`."""
    if topic not in get_args(TopicBlock):
        return {"error": f"The topic is one of {', '.join(get_args(TopicBlock))}."}
    if data.roster_id is None:
        return {"error": "This answer has no team."}
    roster_id = data.roster_id
    if topic in LEAGUE_TOPICS:
        result = _league(data, topic, roster_id)
    elif topic in GRADE_TOPICS:
        result = _grade(data, GRADE_TOPICS[topic], roster_id)
    else:
        result = _live(data, topic, roster_id)
    if "error" in result:
        return result
    return {"topic": topic, "team": data.teams.get(roster_id, f"roster {roster_id}"),
            "what_each_field_means": TOPIC_MEANINGS, **result}
