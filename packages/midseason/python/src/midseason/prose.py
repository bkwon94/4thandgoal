"""
The prose of the midseason report: the facts and the prose blocks of each chapter, the roast terms of the writer, and
the write and the check of each blurb through the writer and the verifier of facts. The report has no writer of its own.
"""
import json
from collections.abc import Collection, Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel

from facts.tokens import Nums, fact
from facts.verifier import code_check, page_words, verify_blurb, write_and_verify
from facts.writer import CHECK_ERRORS, ClaudeCall
from league.files import write_bytes_atomic
from league.models import Blurb, Chapter, Fact, FactSheet, Sentence, VerifyResult
from midseason.state import LeagueState
from midseason.values import Roast

# The saved facts of the draft, beside midseason.json in the build folder of the season. The publish checks each blurb
# against them again. The publish never copies this file.
FACTS_FILE = "midseason-facts.json"
ROAST_RULES = Path(__file__).parent / "prompts" / "roast.md"
# The writing notes of every prose block: the number limit, the article before a 0 record, and the gated words that the
# midseason facts never back. Each note keeps the writer off a failure of the code check of facts.
PROSE_NOTES = Path(__file__).parent / "prompts" / "notes.md"
# Two example roasts at hot heat. Only the hot step gets them, as warm softens each roast.
ROAST_HOT_EXAMPLES = Path(__file__).parent / "prompts" / "roast-hot.md"
# A roast block may hold two reaction sentences, so the reactions can carry the heat. The first sentence cites a fact.
ROAST_REACTIONS = 2
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
# The last sentence of a template blurb. A reaction has no digit and no name, so it gives the blurb its sentence with no
# number and makes no claim.
TEMPLATE_REACTION = "The second half starts now."
# The ID prefix of a callout fact of the spread rule.
CALLOUT_PREFIX = "CO."


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


# The prose block of a later chapter: its key, its title, and its facts, in page order after the state.
ChapterFacts = tuple[str, str, list[Fact]]


def prose_sheet(
    week: int, state: LeagueState, roast: Roast, later: Sequence[ChapterFacts] = (), *,
    first: Sequence[ChapterFacts] = (), callouts: Mapping[str, Sequence[Fact]] | None = None,
) -> FactSheet:
    """The fact sheet of the report: every fact and the prose blocks that cite them. Each chapter has one blurb block,
    and a roast block unless the roast is off. `first` holds the facts of each block before the state, such as the
    opener, and `later` the facts of each chapter after the state.

    `callouts` holds the callout facts of the spread rule by chapter key. Each one joins the end of its chapter's
    block. It names the team that holds the callout and each team that the rule moved off it. A moved team keeps its
    facts and its place in the scope, so the blurb can name it, but not as the headline of the callout.
    """
    callouts = callouts or {}
    n = Nums()
    week_fact = fact(WEEK_FACT, f"The report counts week {n(week)} and every week before it.", n, [], [])
    teams = [team.name for team in state.teams]
    # The week fact comes last in each block, so the template blurb of a failed block reads a team fact, not the week.
    blocks = [*first, ("state", "The State of the League", _state_facts(state)), *later]
    facts: list[Fact] = []
    chapters: list[Chapter] = []
    for key, title, chapter_facts in blocks:
        chapter_facts = [*chapter_facts, *callouts.get(key, ())]
        facts += chapter_facts
        ids = [f.id for f in chapter_facts] + [week_fact.id]
        # The players of the facts are the players that the blurb may name, such as the waiver hits.
        players = sorted({p for f in chapter_facts for p in f.players})
        chapters.append(Chapter(key=key, title=title, fact_ids=ids, scope_teams=teams, scope_players=players,
                                min_sentences=3, max_sentences=6))
        if roast != "off":
            # Two sentences at least. The code check fails a roast of reaction sentences only, so each roast cites a
            # fact.
            chapters.append(Chapter(key=key + ROAST_SUFFIX, title=f"The roast of {title[0].lower() + title[1:]}",
                                    fact_ids=ids, scope_teams=teams, scope_players=players, min_sentences=2,
                                    max_sentences=4, max_reactions=ROAST_REACTIONS))
    facts.append(week_fact)
    return FactSheet(facts={f.id: f for f in facts}, chapters=chapters)


def is_roast(key: str) -> bool:
    return key.endswith(ROAST_SUFFIX)


def prose_terms(key: str, roast: Roast) -> list[str]:
    """The extra writer and verifier terms of one prose block: the writing notes on every block, the roast rules and
    the step on a roast block, with the example roasts at hot, and the off line on every block when the roast is off."""
    notes = PROSE_NOTES.read_text(encoding="utf-8").strip()
    if roast == "off":
        return [notes, ROAST_OFF]
    if is_roast(key):
        terms = [notes, ROAST_RULES.read_text(encoding="utf-8").strip(), ROAST_STEPS[roast]]
        if roast == "hot":
            terms.append(ROAST_HOT_EXAMPLES.read_text(encoding="utf-8").strip())
        return terms
    return [notes]


def template_prose(
    chapter: Chapter, sheet: FactSheet, used_words: Collection[str], *, prompts_dir: Path,
) -> Blurb:
    """The template blurb of a failed prose block: fact texts as sentences, then the template reaction, in the
    sentence range of the block. It takes a fact only when the blurb with it still passes the code check, so the
    publish passes the template as it passes a written blurb.
    """
    reaction = Sentence(text=TEMPLATE_REACTION, fact_ids=[])
    # The template grows one fact at a time, so its check opens the sentence range. The last blurb fills the range.
    open_range = chapter.model_copy(update={"min_sentences": 1})
    chosen: list[Sentence] = []
    for fid in chapter.fact_ids:
        if len(chosen) + 1 >= chapter.min_sentences:
            break
        # The week fact is no headline, and a callout fact is a note to the writer, not prose.
        if fid == WEEK_FACT or fid.startswith(CALLOUT_PREFIX):
            continue
        trial = [*chosen, Sentence(text=sheet.facts[fid].text, fact_ids=[fid])]
        blurb = Blurb(chapter=chapter.key, sentences=[*trial, reaction], attempt=0, fallback=True)
        if not code_check(blurb, open_range, sheet, used_words, prompts_dir=prompts_dir):
            chosen = trial
    return Blurb(chapter=chapter.key, sentences=[*chosen, reaction], attempt=0, fallback=True)


def write_prose(
    sheet: FactSheet, roast: Roast, call: ClaudeCall, *, prompts_dir: Path,
) -> tuple[dict[str, Blurb], dict[str, list[VerifyResult]]]:
    """The blurb of each prose block and the verifier results of each attempt, by the key of the prose block.

    A blurb that fails twice is the template blurb of its block, so the build never stops on the writer.
    """
    blurbs: dict[str, Blurb] = {}
    results: dict[str, list[VerifyResult]] = {}
    used: set[str] = set()
    for chapter in sheet.chapters:
        blurb, results[chapter.key] = write_and_verify(
            chapter, sheet, call, used, prompts_dir=prompts_dir, terms=prose_terms(chapter.key, roast))
        # The template of facts is one sentence, too short for a prose block, so the block gets its own template.
        if blurb.fallback:
            blurb = template_prose(chapter, sheet, used, prompts_dir=prompts_dir)
        blurbs[chapter.key] = blurb
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
        except CHECK_ERRORS as err:
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
