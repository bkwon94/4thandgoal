"""
The prose of the midseason report: the facts and the prose blocks of each chapter, the roast terms of the writer, and
the write and the check of each blurb through the writer and the verifier of facts. The report has no writer of its own.
"""
import json
from collections.abc import Collection
from pathlib import Path

import anthropic
from pydantic import BaseModel, ValidationError

from facts.tokens import Nums, fact
from facts.verifier import page_words, verify_blurb, write_and_verify
from facts.writer import ClaudeCall
from league.claude_errors import RefusalError, WriterError
from league.files import write_bytes_atomic
from league.models import Blurb, Chapter, Fact, FactSheet, VerifyResult
from midseason.state import LeagueState
from midseason.values import Roast

# The saved facts of the draft, beside midseason.json in the build folder of the season. The publish checks each blurb
# against them again. The publish never copies this file.
FACTS_FILE = "midseason-facts.json"
ROAST_RULES = Path(__file__).parent / "prompts" / "roast.md"
# The key of the roast prose block of a chapter is the chapter key with this suffix.
ROAST_SUFFIX = ".roast"
# The heat of each roast step, in the writer prompt after the roast rules. PRD, "The prose and the roast".
ROAST_STEPS: dict[Roast, str] = {
    "hot": "Roast: hot. No limit on heat for football decisions.",
    "warm": "Roast: warm. Keep the jokes, but soften each roast: tease the manager, never pile on.",
}
# With the roast off, the report has no roast blocks, and this line overrides the roast of the default voice.
ROAST_OFF = "Roast: off. Write no roast and no joke at a manager's expense. State the facts plainly."
# The week fact lets a blurb name the report week and the week after it, as the verifier allows on a weekly page.
WEEK_FACT = "W.week"


class ProseDraft(BaseModel):
    """The saved facts of the draft: the roast step of the build and the fact sheet of every prose block."""
    roast: Roast
    sheet: FactSheet


def _state_facts(state: LeagueState) -> list[Fact]:
    """The facts of the state of the league: the record and the place, the points, the streak, and the odds."""
    facts = []
    for team in state.teams:
        prefix = f"ST.{team.roster_id}"
        n = Nums()
        record = n.record(team.wins, team.losses) if not team.ties else n.text(f"{team.wins}-{team.losses}-{team.ties}")
        facts.append(fact(f"{prefix}.record", f"{team.name} is {record}, {n.ord(team.rank)} in the standings.", n,
                          [team.name], []))
        n = Nums()
        facts.append(fact(f"{prefix}.points",
                          f"{team.name} has {n(team.points_for)} points for and {n(team.points_against)} points against.",
                          n, [team.name], []))
        if team.streak is not None:
            n = Nums()
            verb = "won" if team.streak.kind == "W" else "lost"
            facts.append(fact(f"{prefix}.streak",
                              f"{team.name} has {verb} {n(team.streak.length)} head-to-head games in a row.",
                              n, [team.name], []))
        if team.playoff_odds is not None:
            n = Nums()
            facts.append(fact(f"{prefix}.odds", f"{team.name} has {n(team.playoff_odds)}% playoff odds.", n,
                              [team.name], []))
    return facts


def prose_sheet(week: int, state: LeagueState, roast: Roast) -> FactSheet:
    """The fact sheet of the report: every fact and the prose blocks that cite them. Each chapter has one blurb block,
    and a roast block unless the roast is off."""
    n = Nums()
    week_fact = fact(WEEK_FACT, f"The report counts week {n(week)} and every week before it.", n, [], [])
    # The week fact comes last, so the template blurb of a failed block reads the first team fact, not the week.
    facts = [*_state_facts(state), week_fact]
    ids = [f.id for f in facts]
    teams = [team.name for team in state.teams]
    chapters = [Chapter(key="state", title="The state of the league", fact_ids=ids, scope_teams=teams,
                        scope_players=[], min_sentences=3, max_sentences=6)]
    if roast != "off":
        # Two sentences at least, and a blurb holds one reaction sentence at most, so each roast cites a fact.
        chapters.append(Chapter(key="state" + ROAST_SUFFIX, title="The roast of the state of the league", fact_ids=ids,
                                scope_teams=teams, scope_players=[], min_sentences=2, max_sentences=4))
    return FactSheet(facts={f.id: f for f in facts}, chapters=chapters)


def is_roast(key: str) -> bool:
    return key.endswith(ROAST_SUFFIX)


def prose_terms(key: str, roast: Roast) -> list[str]:
    """The extra writer and verifier terms of one prose block: the roast rules and the step on a roast block, and the
    off line on every block when the roast is off."""
    if roast == "off":
        return [ROAST_OFF]
    if is_roast(key):
        return [ROAST_RULES.read_text(encoding="utf-8").strip(), ROAST_STEPS[roast]]
    return []


def write_prose(
    sheet: FactSheet, roast: Roast, call: ClaudeCall, *, prompts_dir: Path,
) -> tuple[dict[str, Blurb], dict[str, list[VerifyResult]]]:
    """The blurb of each prose block and the verifier results of each attempt, by the key of the prose block.

    A blurb that fails twice is the template blurb of facts, so the build never stops on the writer.
    """
    blurbs: dict[str, Blurb] = {}
    results: dict[str, list[VerifyResult]] = {}
    used: set[str] = set()
    for chapter in sheet.chapters:
        blurbs[chapter.key], results[chapter.key] = write_and_verify(
            chapter, sheet, call, used, prompts_dir=prompts_dir, terms=prose_terms(chapter.key, roast))
        used |= page_words(blurbs[chapter.key], chapter)
    return blurbs, results


def recheck_prose(
    blurbs: Collection[Blurb], draft: ProseDraft, call: ClaudeCall, *, prompts_dir: Path,
) -> list[str]:
    """One line per blurb that fails the verifier again, with its key and its failures. An empty list passes.

    The publish runs it, so an edit of the draft cannot add an uncited number or claim.
    """
    chapters = {chapter.key: chapter for chapter in draft.sheet.chapters}
    failures: list[str] = []
    used: set[str] = set()
    for blurb in blurbs:
        chapter = chapters.get(blurb.chapter)
        if chapter is None:
            failures.append(f"The blurb {blurb.chapter} has no prose block in {FACTS_FILE}.")
            continue
        try:
            result = verify_blurb(blurb, chapter, draft.sheet, call, used, prompts_dir=prompts_dir,
                                  terms=prose_terms(chapter.key, draft.roast))
        except (RefusalError, WriterError, anthropic.APIError, ValidationError) as err:
            # A failed Claude check is no pass, so the publish refuses and names the blurb.
            failures.append(f"The blurb {blurb.chapter} has no verdict: the Claude check failed: {err}")
            continue
        finally:
            used |= page_words(blurb, chapter)
        if not result.passed:
            reasons = [*result.code_failures,
                       *(f"[{v.index}] {v.reason}" for v in result.verdicts if not v.supported)]
            failures.append(f"The blurb {blurb.chapter} fails the verifier: " + "; ".join(reasons))
    return failures


def write_draft_facts(draft: ProseDraft, season_build: Path) -> Path:
    out = season_build / FACTS_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    write_bytes_atomic(out, (json.dumps(draft.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n").encode())
    return out


def read_draft_facts(season_build: Path) -> ProseDraft:
    return ProseDraft.model_validate_json((season_build / FACTS_FILE).read_text(encoding="utf-8"))
