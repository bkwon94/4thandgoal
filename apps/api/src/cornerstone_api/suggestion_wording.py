"""
All the wording of the lift of the Suggestions: the state of one Jev request over the fact of each Topic of one team,
and one Noul per Topic that asks whether its fact makes it urgent. Code reads each Noul with the cutoffs of the route.
"""
from cornerstone_api.ask_wording import TOPICS
from league.jev_port import NoulQuestion

# The name of each Topic as the site shows it on its Suggestion. Jev reads the Topic and its fact as one line.
TOPIC_NAMES = {
    "week_recap": "Week recap",
    "last_matchup": "Your last matchup",
    "next_matchup": "Your next matchup",
    "power_rankings": "Power rankings",
    "playoff_race": "Playoff race",
    "your_season": "Your season",
    "leaders_trades": "Position leaders and recent trades",
    "waiver_targets": "Waiver targets",
    "stack_up": "How you stack up",
    "weak_spots": "Weak spots",
    "sell_high": "Sell high or buy low",
    "trade_ideas": "Trade ideas",
    "trade_check": "Trade check",
}

CONTEXT = ("The front door of a 12-team fantasy football league site shows a few Suggestions to the manager of one "
           "team. Each Suggestion is one Topic with one fact about that team from this week's league data. The games of "
           "the next fantasy week have not started.")


def lift_key(topic: str) -> str:
    return f"lift_{topic}"


def lift_state(team: str, week: int, facts: dict[str, str]) -> dict:
    """The state of one lift request: the team, the next week, and the fact of each Topic by its key."""
    return {
        "context": CONTEXT,
        "manager_team": team,
        "next_week": week,
        "topics": {key: {"name": TOPIC_NAMES[key], "about": TOPICS[key], "fact": fact} for key, fact in facts.items()},
    }


def lift_questions(facts: dict[str, str]) -> dict[str, NoulQuestion]:
    """One Noul per Topic with a fact: does its fact make it urgent for the manager to open now?"""
    return {
        lift_key(key): NoulQuestion(
            instructions=f"Does the fact in `topics.{key}.fact` make the Topic {TOPIC_NAMES[key]} urgent for the "
                         "manager of `manager_team` to open before the next games?",
            yes="The fact shows something the manager should act on or look at now, such as playoff odds near the "
                "line, a starting position that ranks near the bottom of the league, a hole in the lineup, or a big "
                "drop in the rankings.",
            no="The fact shows a normal week for the team, such as a rank in the middle of the league, a safe lead in "
               "the playoff race, a routine result, or a strength of the roster.")
        for key in facts
    }
