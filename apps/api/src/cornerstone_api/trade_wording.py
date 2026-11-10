"""
All the wording of the Jev pick of a typed trade check: the state with the real rosters, and the 4 typed questions.
The trade check in trade_topics.py reads the answers with code. Change a question here and run a live pick again.
"""
import re

from league.jev_port import ChoiceQuestion, NoulQuestion

CONTEXT = ("A manager of this 12-team fantasy football league typed `manager_question` into the ask box of the league "
           "site. The manager asks about a trade of a player of `your_team` for a player of another team.")

GIVES_NAMED = "gives_named"
GIVES_PLAYER = "gives_player"
GETS_NAMED = "gets_named"
GETS_PLAYER = "gets_player"

NOULS = {
    GIVES_NAMED: NoulQuestion(
        instructions="Does `manager_question` name a player of `your_team.players` that the manager would give?",
        yes="The question names one player of `your_team.players`, by full name, last name, or a nickname, as the "
            "player that the manager gives.",
        no="The question names no player of `your_team.players`, or names only a position, such as 'my RB'."),
    GETS_NAMED: NoulQuestion(
        instructions="Does `manager_question` name a player of a team in `other_teams` that the manager would get?",
        yes="The question names one player of a team in `other_teams`, by full name, last name, or a nickname, as the "
            "player that the manager gets.",
        no="The question names no player of `other_teams`, or names only a position, such as 'their WR'."),
}


def player_line(name: str, position: str, nfl_team: str | None, team: str | None = None) -> str:
    """One player as the state and an option show him: the name, the position, the NFL team, and the team of the
    league for a player of another team."""
    line = f"{name} ({position}, {nfl_team or 'no NFL team'})"
    return f"{line}, on {team}" if team else line


def option_keys(names: dict[str, str]) -> dict[str, str]:
    """The option key of each player id: the name in lower case, with each run of other signs as one "_".

    Option names reach Jev, so a key that reads as the name helps it more than a player id. Two players with one name
    each get the player id after the name, so each key stays unique.
    """
    keys = {pid: re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") for pid, name in names.items()}
    taken = list(keys.values())
    return {pid: key if taken.count(key) == 1 else f"{key}_{pid.lower()}" for pid, key in keys.items()}


def pick_questions(gives: dict[str, str], gets: dict[str, str]) -> dict[str, NoulQuestion | ChoiceQuestion]:
    """The 4 typed questions of one pick request: a Noul and a Choice per side. `gives` and `gets` hold the text of
    each option by its key. The Noul asks whether the question names a player, because a Choice always picks one."""
    return {
        GIVES_NAMED: NOULS[GIVES_NAMED],
        GIVES_PLAYER: ChoiceQuestion(instructions="Which player of `your_team.players` would the manager give in the "
                                                  "trade in `manager_question`?", options=gives),
        GETS_NAMED: NOULS[GETS_NAMED],
        GETS_PLAYER: ChoiceQuestion(instructions="Which player of `other_teams` would the manager get in the trade in "
                                                 "`manager_question`?", options=gets),
    }


def pick_state(question: str, team: str, players: list[str], others: dict[str, list[str]]) -> dict:
    """The state of one pick request: the question, Your team with its players, and each other team with its players."""
    return {"context": CONTEXT, "manager_question": question, "your_team": {"name": team, "players": players},
            "other_teams": others}
