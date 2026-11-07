"""
The egg draft of a week: an agent proposes the spots of one egg drop, each with a reason, marked not confirmed.
The draft refuses a spot that repeats a dropped egg, so the commissioner starts each Tuesday from a clean draft.
"""
import json
import re
from collections.abc import Callable
from pathlib import Path

from eggs.conditions import check_action, check_conditions, egg_page
from eggs.eggfile import Spot, append_spots, read_spots

# The prompt of the agent. It names the files to read, so it holds no spot.
PROMPT_FILE = Path(__file__).with_name("draft_prompt.md")
# The catalog of ticket 01 and its survey notes, from the repo root.
CATALOG = ".scratch/easter-eggs/decisions/01-grill-egg-catalog.md"
NOTES = ".scratch/easter-eggs/decisions/01-grill-egg-catalog.notes.md"
LISTENER = "packages/eggs/site/listener/listener.ts"

# The agent: it takes the prompt and answers with its text.
Propose = Callable[[str], str]


class DraftError(Exception):
    """The draft of the agent breaks a rule of the draft, so the egg file stays as it was."""


def dropped_spots(path: Path, week: int) -> list[Spot]:
    """The eggs that dropped before: each confirmed spot of another week of the egg file."""
    return [spot for spot in read_spots(path) if spot.confirmed and spot.week != week]


def draft_prompt(path: Path, week: int, page: Path, size: int) -> str:
    """The prompt of the agent for the draft of `week`, with the built week page and each egg that dropped before."""
    dropped = [{"week": spot.week, "page": spot.page, "target": spot.target, "action": spot.action,
                "conditions": spot.conditions} for spot in dropped_spots(path, week)]
    return PROMPT_FILE.read_text(encoding="utf-8").format(
        week=week, size=size, catalog=CATALOG, notes=NOTES, listener=LISTENER, page=page,
        dropped=json.dumps(dropped, indent=2) if dropped else "None.")


def draft_week(path: Path, week: int, propose: Propose, prompt: str, size: int = 6) -> list[Spot]:
    """Ask the agent for the `size` spots of `week`, check them, and add them to the egg file, marked not confirmed.

    A week that already holds a spot, or a draft that breaks a rule, raises DraftError and writes nothing.
    """
    if any(spot.week == week for spot in read_spots(path)):
        raise DraftError(f"The egg file already holds spots of week {week}. Edit them in {path}.")
    spots = _parse(propose(prompt), week)
    problems = _problems(spots, dropped_spots(path, week), size)
    if problems:
        raise DraftError("The draft writes nothing:\n" + "\n".join(f"- {problem}" for problem in problems))
    append_spots(path, spots)
    return spots


def _parse(text: str, week: int) -> list[Spot]:
    """The spots in the answer of the agent: the one JSON list in its text. Each spot is marked not confirmed."""
    found = re.search(r"\[.*\]", text, re.DOTALL)
    if found is None:
        raise DraftError("The answer of the agent holds no JSON list of spots.")
    try:
        items = json.loads(found.group(0))
        return [Spot(week=week, page=str(item["page"]), target=str(item["target"]), action=str(item["action"]),
                     reason=str(item.get("reason") or "").strip(), conditions=dict(item.get("conditions") or {}),
                     confirmed=False) for item in items]
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as err:
        raise DraftError(f"The answer of the agent is not a list of spots: {err}") from None


def _problems(spots: list[Spot], dropped: list[Spot], size: int) -> list[str]:
    """Each rule of the draft that the spots break: the count, a reason for each, a good action and good conditions
    as the drop checks them, and no repeat."""
    problems = [] if len(spots) == size else [f"The draft holds {len(spots)} spots, not {size}."]
    problems += [f"The spot {spot.target} on {spot.page} has no reason." for spot in spots if not spot.reason]
    for spot in spots:
        try:
            check_action(spot.action)
            check_conditions(spot.conditions)
        except ValueError as err:
            problems.append(f"The spot {spot.target} on {spot.page} is not valid: {err}")
    # A spot repeats when another egg hides on the same target of the same page. Every 404 egg shares one page.
    seen = {(egg_page(spot.page, spot.conditions), spot.target) for spot in dropped}
    for spot in spots:
        key = (egg_page(spot.page, spot.conditions), spot.target)
        if key in seen:
            problems.append(f"The spot {spot.target} on {spot.page} repeats an egg.")
        seen.add(key)
    return problems
