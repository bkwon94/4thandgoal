"""
The review file of the midseason report: each blurb with its prose block, the facts it cites, and the verifier result.
Brian reads it in the build folder of the season before the publish. The publish never copies it.
"""
from collections.abc import Mapping
from pathlib import Path

from league.files import write_bytes_atomic
from league.models import Blurb, FactSheet, VerifyResult
from midseason.values import Roast

REVIEW_FILE = "midseason-review.md"


def _verifier_lines(blurb: Blurb, results: list[VerifyResult]) -> list[str]:
    if not blurb.fallback:
        return [f"Verifier: passed on attempt {blurb.attempt}."]
    lines = [f"Verifier: failed {len(results)} times. The blurb is the template of the block.",
             "It holds fact sentences, then a reaction. Edit it if it reads flat. The publish checks it again."]
    for attempt, result in enumerate(results, start=1):
        reasons = [*result.code_failures, *(f"[{v.index}] {v.reason}" for v in result.verdicts if not v.supported)]
        lines += [f"- Attempt {attempt}: {reason}" for reason in reasons]
    return lines


def review_text(
    season: int, week: int, roast: Roast, sheet: FactSheet, blurbs: Mapping[str, Blurb],
    results: Mapping[str, list[VerifyResult]], publish_command: str,
) -> str:
    """The review file as markdown, one section per prose block in page order."""
    lines = [
        f"# Midseason report {season}, week {week}: review",
        "",
        f"Roast: {roast}. Edit a blurb in midseason.json, then run {publish_command}.",
        "The publish checks each blurb again.",
    ]
    for chapter in sheet.chapters:
        blurb = blurbs[chapter.key]
        cited = list(dict.fromkeys(fid for s in blurb.sentences for fid in s.fact_ids))
        lines += [
            "",
            f"## {chapter.key}: {chapter.title}",
            "",
            f"Prose block: {chapter.min_sentences} to {chapter.max_sentences} sentences, {len(chapter.fact_ids)} facts.",
            "",
            "Blurb:",
            *(f"{i}. {s.text} [{', '.join(s.fact_ids) or 'reaction'}]"
              for i, s in enumerate(blurb.sentences, start=1)),
            "",
            "Cited facts:",
            *(f"- {fid}: {sheet.facts[fid].text}" for fid in cited if fid in sheet.facts),
            "",
            *_verifier_lines(blurb, list(results.get(chapter.key, []))),
        ]
    return "\n".join(lines) + "\n"


def write_review(text: str, season_build: Path) -> Path:
    out = season_build / REVIEW_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    write_bytes_atomic(out, text.encode("utf-8"))
    return out
