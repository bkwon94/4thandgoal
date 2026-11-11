"""
All the wording of a personal Topic: the instructions of Claude, the prompt of one Topic over its slice, the line that
asks for a rewrite, and the Jev read of a waiver target. The check of each sentence is the free answer check.
"""
import json

from league.jev_port import NoulQuestion

# What each fact of the slices means. Claude reads them as rules of INSTRUCTIONS, and the Jev check reads them in its
# state, so the writer and the check read the same meaning of each fact.
FACT_MEANINGS = {
    "rank": "A rank in `slot_ranks` or `part_ranks` is the place of the team among the teams of the league, where 1 "
            "is the best.",
    "weakest_position": "The weakest position of the team is the position with the worst `rank` in `slot_ranks`, the "
                        "largest number.",
    "grade_as_of": "`grade_as_of` says the grade in `grade` is from the live league today, so say \"as of today\". The "
                   "grade of the managers page is from the last week of the weekly build, so it can differ.",
    "projected_rank_at_position": "`projected_rank_at_position` is the place of a player among the players at his "
                                  "position, so 50 at QB is the 50th QB.",
    "depth_means": "In `slot_ranks`, `depth_means` says what each depth word means.",
    "hole": "In `starters`, a hole is a slot with no player or with a player whose projected rank at his position is "
            "worse than `starter_line`.",
    "can_play_now": "A starter with `can_play_now` false is out now, such as on IR, so his slot is a hole.",
    "weak_starting_slots": "Each entry of `weak_starting_slots` is a slot of the lineup of the players who can play "
                           "now that `starters` does not show: a slot with no player, or the player who plays the slot "
                           "of a starter who is out now. A slot with no player is the weakest spot of the team.",
}

INSTRUCTIONS = """\
You write one short Answer on a 12-team fantasy football league site, about one team.
The prompt gives the Topic and the facts of that team as JSON. Write one paragraph of 2 to 4 short sentences of
plain words.

Rules:
- Use only what the facts say. Give the real ranks, positions, and player names from them.
""" + "".join(f"- {meaning}\n" for meaning in FACT_MEANINGS.values()) + """\
- Use the depth words of `depth_means`, not your own.
- Never do math on the numbers, and never guess what the facts do not say.
- Never name a tool, a file, a grade formula, or a data source. Never use a heading, a table, or a list.
- Call the person who runs another team "the manager" of that team.
"""

# What each Topic asks of the text. The facts of each Topic are in FACT_GROUPS of personal_facts.py.
TOPIC_ASKS = {
    "weak_spots": "Name the weakest positions of the team and each hole in its lineup, worst first. The weakest "
                  "position is the one with the worst `rank` in `slot_ranks`.",
    "stack_up": "Say how the roster stacks up against the league: its grade, its best and its worst part, and its "
                "best and its worst position.",
    "waiver_targets": "Name the first players of `kept_players`, at most 3, best first. Give each one short reason "
                      "in plain words from his facts, such as the player above him who is out, his carries or targets "
                      "of the last week, or the slot of `team_need` he fills, with at most one number. `kind` says if "
                      "he is an add this week or a stash for later weeks. Quote no FAAB bid. If `kept_players` is "
                      "empty, say plainly that no free agent beats the starters of the team this week.",
}

# The two Nouls of the Jev read of one free agent, in one request with one state: the team need and his facts. An add
# and a stash are two judgments, so each has its own Noul, and code keeps a player when either is a yes.
WAIVER_ADD = {
    "text": "Would {player} be a better start for {team} in week {week} than its starter in a slot that takes him?",
    "yes": "{player} has a real role on his NFL team in week {week}, and he would start for {team} over a weak "
           "starter in `team.starters`, a starter on bye that week, or in an empty slot.",
    "no": "{player} is a backup on his NFL team who plays few snaps, or each starter of {team} in a slot that takes "
          "him is a better start in week {week}."}
WAIVER_STASH = {
    "text": "Is {player} worth a bench spot on {team} now, for the weeks after week {week}?",
    "yes": "The role of {player} is growing or opens soon, such as the player above him out for weeks or a rise in his "
           "snaps and touches, so in later weeks he could start over a starter of {team}.",
    "no": "{player} is a backup behind a healthy starter with a small role, so in later weeks he would still sit "
          "behind the starters of {team}."}

TOPIC_NAMES = {"weak_spots": "Weak spots", "stack_up": "How you stack up", "waiver_targets": "Waiver targets"}

REWRITE = """\
A check found that these sentences of your Answer do not follow from the facts:
{sentences}
Write the whole Answer again. Keep only what the facts say, with the same rules.
"""


def topic_prompt(topic: str, facts: dict, own: bool, question: str | None = None) -> str:
    """The prompt of one Topic: what to write, the typed question if the manager typed one, whom it addresses, and the
    slice as JSON with sorted keys, so the same facts give the same prompt."""
    voice = ("The manager of this team asks, so call the team \"your team\" or \"you\"." if own
             else f"The manager of another team asks, so call this team {facts['team']}.")
    typed = "" if question is None else f"The manager asks: \"{question}\". Answer that question from the facts.\n"
    return (f"Topic: {TOPIC_NAMES[topic]}.\n{TOPIC_ASKS[topic]}\n{typed}{voice}\n\nFacts:\n"
            f"{json.dumps(facts, sort_keys=True, indent=1)}")


def rewrite_prompt(failed: list[str]) -> str:
    return REWRITE.format(sentences="\n".join(f"- {sentence}" for sentence in failed))


def check_question(topic: str, team: str, question: str | None = None) -> str:
    """The question that the claim check reads as `manager_question`: the typed question, or else the Topic and the
    team it is about."""
    return question if question is not None else f"{TOPIC_NAMES[topic]} of {team}"


def waiver_questions(player: str, team: str, week: int) -> dict[str, NoulQuestion]:
    """The add Noul and the stash Noul of one free agent for `team` in `week`."""
    fill = {"player": player, "team": team, "week": week}
    return {key: NoulQuestion(q["text"].format(**fill), q["yes"].format(**fill), q["no"].format(**fill))
            for key, q in (("add", WAIVER_ADD), ("stash", WAIVER_STASH))}
