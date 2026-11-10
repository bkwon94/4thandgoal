"""
All the Jev wording of the Suggestions: the lift, one Noul per Topic over its fact, and the sell high pick, one Choice
over the players of Your team with their facts side by side. Code reads each answer with the cutoffs of the route.
"""
from cornerstone_api.ask_wording import TOPICS
from league.jev_port import ChoiceQuestion, NoulQuestion

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
                "line, a starting position that ranks near the bottom of the league, a hole in the lineup, a big "
                "drop in the rankings, or a player whose recent scoring runs far above his season.",
            no="The fact shows a normal week for the team, such as a rank in the middle of the league, a safe lead in "
               "the playoff race, a routine result, or a strength of the roster.")
        for key in facts
    }


# The key of the sell high Choice in its request.
SELL_CHOICE = "sell_high_player"

SELL_CONTEXT = ("A 12-team fantasy football league. The manager of one team wants to sell a player of the roster to "
                "another manager while his price is up. Each player of the roster has his facts side by side: his "
                "trade value, his lineup value, his injury, his points per game over the last weeks against the "
                "season, and his schedule ahead.")


def sell_state(team: str, week: int, players: dict[str, dict]) -> dict:
    """The state of the sell high pick: the team, the next week, and each player by his option key, with his name and
    the texts of his facts from the sell sheet."""
    return {"context": SELL_CONTEXT, "manager_team": team, "next_week": week, "players": players}


def sell_questions(options: dict[str, str]) -> dict[str, ChoiceQuestion]:
    """One Choice over the players of the roster. `options` holds the line of each player by his option key. A
    Choice always picks one, so code reads it only when its top option is above the cutoff."""
    return {
        SELL_CHOICE: ChoiceQuestion(
            instructions="Which player of `manager_team` has a recent run that most outpaces his season, so that "
                         "another manager would pay more for him now than his season is worth?",
            options={key: f"{line}: the player in `players.{key}`" for key, line in options.items()}),
    }
