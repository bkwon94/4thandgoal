"""
All the wording of a personal Topic: the instructions of Claude, the prompt of one Topic over its slice, and the line
that asks for a rewrite. The Jev check of each sentence is the check of the free answer, in free_wording.py.
"""
import json

INSTRUCTIONS = """\
You write one short Answer on a 12-team fantasy football league site, about one team.
The prompt gives the Topic and the facts of that team as JSON. Write one paragraph of 2 to 4 short sentences of
plain words.

Rules:
- Use only what the facts say. Give the real ranks, positions, and player names from them.
- A rank in `slot_ranks` or `part_ranks` is the place of the team among the teams of the league, where 1 is
  the best. `projected_rank_at_position` is the place of a player among the players at his position.
- In `slot_ranks`, `depth_means` says what each depth word means. Use those words, not your own.
- In `starters`, a hole is a slot with no player or with a player whose projected rank at his position is worse
  than `starter_line`.
- Never do math on the numbers, and never guess what the facts do not say.
- Never name a tool, a file, a grade formula, or a data source. Never use a heading, a table, or a list.
- Call the person who runs another team "the manager" of that team.
"""

# What each Topic asks of the text. The facts of each Topic are in FACT_GROUPS of personal_facts.py.
TOPIC_ASKS = {
    "weak_spots": "Name the weakest positions of the team and each hole in its lineup, worst first.",
    "stack_up": "Say how the roster stacks up against the league: its grade, its best and its worst part, and its "
                "best and its worst position.",
    "waiver_targets": "Name the players of `waiver_list` that fit the weak spots of the team, and say why each one "
                      "fits. A player in the `trending` bucket is one that many Sleeper leagues add now, so lean on "
                      "those players first. Quote no FAAB bid. If `waiver_list` is empty, say that the waiver list of "
                      "this week is not out, and name the positions to look at.",
}

TOPIC_NAMES = {"weak_spots": "Weak spots", "stack_up": "How you stack up", "waiver_targets": "Waiver targets"}

REWRITE = """\
A check found that these sentences of your Answer do not follow from the facts:
{sentences}
Write the whole Answer again. Keep only what the facts say, with the same rules.
"""


def topic_prompt(topic: str, facts: dict, own: bool) -> str:
    """The prompt of one Topic: what to write, whom it addresses, and the slice as JSON with sorted keys, so the same
    facts give the same prompt."""
    voice = ("The manager of this team asks, so call the team \"your team\" or \"you\"." if own
             else f"The manager of another team asks, so call this team {facts['team']}.")
    return (f"Topic: {TOPIC_NAMES[topic]}.\n{TOPIC_ASKS[topic]}\n{voice}\n\nFacts:\n"
            f"{json.dumps(facts, sort_keys=True, indent=1)}")


def rewrite_prompt(failed: list[str]) -> str:
    return REWRITE.format(sentences="\n".join(f"- {sentence}" for sentence in failed))


def check_question(topic: str, team: str) -> str:
    """The question that the claim check reads as `manager_question`: the Topic and the team it is about."""
    return f"{TOPIC_NAMES[topic]} of {team}"
