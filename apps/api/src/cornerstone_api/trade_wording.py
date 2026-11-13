"""
All the wording of the Jev pick of a typed trade check and of typed trade ideas: the state with the real rosters, the 8
typed questions of the pick, and the 8 of the limit of trade ideas. trade_topics.py reads the answers with code.
"""
import re

from league.jev_port import ChoiceQuestion, NoulQuestion

CONTEXT = ("A manager of this 12-team fantasy football league typed `manager_question` into the ask box of the league "
           "site. The manager asks about a trade of one or two players of `your_team` for one or two players of "
           "another team.")

# The context of trade ideas. The same 8 questions read it: the side whose Noul is sure names the player and the
# direction, a player that the manager gives or a player that the manager gets. The questions of the limit read it too,
# so a follow-up such as "not a WR" reads as a limit on the trade ideas.
IDEAS_CONTEXT = ("A manager of this 12-team fantasy football league typed `manager_question` into the ask box of the "
                 "league site. The manager asks for trade ideas: offers built around one player, a player of "
                 "`your_team` to give or a player of another team to get, or offers with a limit that the manager "
                 "sets, such as a position or a player of `your_team` to keep.")

GIVES_NAMED = "gives_named"
GIVES_PLAYER = "gives_player"
GETS_NAMED = "gets_named"
GETS_PLAYER = "gets_player"
# The second player of a side, such as Devonta Smith in "Kyren Williams for Chase Brown and Devonta Smith". A Choice
# picks one option, so the second player gets a Noul and a Choice of his own.
GIVES_ALSO_NAMED = "gives_also_named"
GIVES_ALSO_PLAYER = "gives_also_player"
GETS_ALSO_NAMED = "gets_also_named"
GETS_ALSO_PLAYER = "gets_also_player"

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
    GIVES_ALSO_NAMED: NoulQuestion(
        instructions="Does `manager_question` name two players of `your_team.players` that the manager would give?",
        yes="The question names two players of `your_team.players` as the players that the manager gives, such as "
            "'Walker and Flowers for Henry'.",
        no="The question names one player of `your_team.players` or none as a player that the manager gives."),
    GETS_ALSO_NAMED: NoulQuestion(
        instructions="Does `manager_question` name two players of `other_teams` that the manager would get?",
        yes="The question names two players of `other_teams` as the players that the manager gets, such as "
            "'Henry for Walker and Flowers'.",
        no="The question names one player of `other_teams` or none as a player that the manager gets."),
}


# The positions of a limit of trade ideas: the trade positions of the analyzer.
LIMIT_POSITIONS = ("QB", "RB", "WR", "TE")
# The key of the Noul of each position that the manager keeps, such as "keeps_wr".
KEEPS_POSITION = {position: f"keeps_{position.lower()}" for position in LIMIT_POSITIONS}
KEEPS_NAMED = "keeps_named"
KEPT_PLAYER = "kept_player"
AIMS_POSITION = "aims_position"
AIM_POSITION = "aim_position"
# The options of the position to get. The key is the position, so code reads it as it is.
POSITION_OPTIONS = {"QB": "QB (quarterback)", "RB": "RB (running back)", "WR": "WR (wide receiver)",
                    "TE": "TE (tight end)"}


def keeps_position_question(position: str) -> NoulQuestion:
    """The Noul of one position that the manager keeps: no offer of the trade ideas sends a player of it away."""
    return NoulQuestion(
        instructions=f"Does the manager say in `manager_question` that the trade ideas must send away no {position} of "
                     "`your_team.players`?",
        yes=f"The manager rules out trading away a {position}, such as 'id rather not trade a {position}', 'not a "
            f"{position}', or 'keep my {position}s'.",
        no=f"The manager says nothing against trading away a {position}, or names a {position} only as a position to "
           f"get, such as 'what about for a {position}'.")


LIMIT_NOULS = {
    KEEPS_NAMED: NoulQuestion(
        instructions="Does `manager_question` name a player of `your_team.players` that the manager wants to keep out "
                     "of each trade?",
        yes="The question names one player of `your_team.players`, by full name, last name, or a nickname, that the "
            "manager will not trade away, such as 'keep Walker' or 'ones without Flowers'.",
        no="The question names no player of `your_team.players` to keep, or names one only as a player to give."),
    AIMS_POSITION: NoulQuestion(
        instructions="Does `manager_question` ask for trade ideas that bring back a player at one position?",
        yes="The manager asks to get a player at one position, such as 'what about for a TE' or 'get me a QB'.",
        no="The question names no position to get, or names a position only to keep it, such as 'not a WR'."),
}


def limit_questions(keeps: dict[str, str]) -> dict[str, NoulQuestion | ChoiceQuestion]:
    """The 8 typed questions of the limit of trade ideas: a Noul per position to keep, a Noul and a Choice for a player
    to keep, and a Noul and a Choice for a position to get. `keeps` holds the text of each player of Your team by its
    key. Each Noul asks whether the question sets that part, because a Choice always picks one."""
    return {
        **{KEEPS_POSITION[position]: keeps_position_question(position) for position in LIMIT_POSITIONS},
        KEEPS_NAMED: LIMIT_NOULS[KEEPS_NAMED],
        KEPT_PLAYER: ChoiceQuestion(instructions="Which player of `your_team.players` does the manager want to keep out "
                                                 "of each trade in `manager_question`?", options=keeps),
        AIMS_POSITION: LIMIT_NOULS[AIMS_POSITION],
        AIM_POSITION: ChoiceQuestion(instructions="Which position does the manager want to get in the trade ideas of "
                                                  "`manager_question`?", options=dict(POSITION_OPTIONS)),
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
    """The 8 typed questions of one pick request: per side, a Noul and a Choice for the first player, and a Noul and a
    Choice for the second player. `gives` and `gets` hold the text of each option by its key. Each Noul asks whether
    the question names that player, because a Choice always picks one."""
    return {
        GIVES_NAMED: NOULS[GIVES_NAMED],
        GIVES_PLAYER: ChoiceQuestion(instructions="Which player of `your_team.players` would the manager give in the "
                                                  "trade in `manager_question`? If the question names two, pick the "
                                                  "one named first.", options=gives),
        GIVES_ALSO_NAMED: NOULS[GIVES_ALSO_NAMED],
        GIVES_ALSO_PLAYER: ChoiceQuestion(instructions="Which player of `your_team.players` would the manager give in "
                                                       "the trade in `manager_question`? If the question names two, "
                                                       "pick the one named last.", options=gives),
        GETS_NAMED: NOULS[GETS_NAMED],
        GETS_PLAYER: ChoiceQuestion(instructions="Which player of `other_teams` would the manager get in the trade in "
                                                 "`manager_question`? If the question names two, pick the one named "
                                                 "first.", options=gets),
        GETS_ALSO_NAMED: NOULS[GETS_ALSO_NAMED],
        GETS_ALSO_PLAYER: ChoiceQuestion(instructions="Which player of `other_teams` would the manager get in the "
                                                      "trade in `manager_question`? If the question names two, pick "
                                                      "the one named last.", options=gets),
    }


def pick_state(question: str, team: str, players: list[str], others: dict[str, list[str]],
               context: str = CONTEXT) -> dict:
    """The state of one pick request: the context, the question, Your team with its players, and each other team with
    its players."""
    return {"context": context, "manager_question": question, "your_team": {"name": team, "players": players},
            "other_teams": others}
