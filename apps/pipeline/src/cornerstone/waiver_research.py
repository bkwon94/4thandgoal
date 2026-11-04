"""
The research step of the waiver board: per ranked player, a web search for research claims.
The search call is a parameter, so a test injects a fake and the build passes the real Claude call.
"""
import logging
from collections.abc import Callable
from pathlib import Path

import anthropic
from pydantic import ValidationError

from cornerstone.sheet.base import Nums, fact
from cornerstone.tunables import CLAIMS_PER_PLAYER, RESEARCH_PLAYERS, RESEARCH_SEARCHES
from cornerstone.verifier import URL
from cornerstone.waiver import DROPS
from cornerstone.writer import RefusalError, WriterError, load_prompt, parse_call
from league.claude_port import Writer
from league.models import Fact, ResearchClaim, ResearchOut, WaiverBoard, WaiverPlayer

log = logging.getLogger(__name__)

# (system, user) -> the claims on one player. Tests pass a fake in place of Claude.
SearchCall = Callable[[str, str], ResearchOut]

# The dynamic filter version keeps only the relevant parts of each page in the context, so a call reads fewer
# tokens. The RESEARCH_SEARCHES searches split as the prompt steps do: one for the Yahoo waiver column, one for
# the Yahoo author pages, one for the wider web, and one spare for a page that gave nothing.
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": RESEARCH_SEARCHES}
# A research claim is a short lookup, not a deep analysis, so the call trades depth for speed and cost.
RESEARCH_EFFORT = "low"


def search_call(system: str, user: str, *, writer: Writer | None = None) -> ResearchOut:
    """The real search: one Claude call with the web search tool, parsed into the claims on one player.

    A writer of None is the one ClaudeWriter of the process. A test passes a ClaudeWriter with a stub client.
    """
    return parse_call(user, ResearchOut, system, effort=RESEARCH_EFFORT, tools=[WEB_SEARCH_TOOL], writer=writer)


def research_players(board: WaiverBoard) -> list[WaiverPlayer]:
    """The ranked players of every bucket but drops, in bucket order, each once, at most RESEARCH_PLAYERS."""
    seen: dict[str, WaiverPlayer] = {}
    for key, bucket in board.buckets.items():
        if key == DROPS:
            continue
        for p in bucket:
            seen.setdefault(p.player_id, p)
    return list(seen.values())[:RESEARCH_PLAYERS]


def build_research_prompt(p: WaiverPlayer, board: WaiverBoard, prompts_dir: Path) -> tuple[str, str]:
    """The system prompt and the user message of the search on one player.
    The facts let a claim back or dispute them."""
    lines = [
        f"Today is {board.built.date().isoformat()}.",
        f"Player: {p.name}, {p.position}, {p.team}.",
        "",
        "Engine facts:",
        *(f"- {f.text}" for f in p.facts),
        "",
        f"Give at most {CLAIMS_PER_PLAYER} claims.",
    ]
    return load_prompt(prompts_dir, "research.md"), "\n".join(lines)


def _claims(out: ResearchOut) -> list[ResearchClaim]:
    # A claim shows its source by URL, so a claim with no web URL is dropped.
    return [c for c in out.claims if URL.fullmatch(c.url.strip())][:CLAIMS_PER_PLAYER]


def research_facts(p: WaiverPlayer, claims: list[ResearchClaim]) -> list[Fact]:
    """One fact per claim, `WV.research.{player_id}.{n}`: the sentence, the source, and the URL the page shows.

    The numbers hold the digits of the sentence and the source only. The digits of the URL are part of the
    address, not a claim, so the verifier skips them.
    """
    facts = []
    for i, claim in enumerate(claims, start=1):
        n = Nums()
        text = f"{n.text(claim.text.strip())} Source: {n.text(claim.source.strip())}, {claim.url.strip()}"
        facts.append(fact(f"WV.research.{p.player_id}.{i}", text, n, [], [p.name]))
    return facts


def research_board(board: WaiverBoard, call: SearchCall, prompts_dir: Path) -> WaiverBoard:
    """The board with the research claims and the research facts of each ranked player.

    A failure for one player logs and leaves him with no claim. A failure for every player also sets
    `experts_missing`, and the build goes on.
    """
    players = research_players(board)
    claims: dict[str, list[ResearchClaim]] = {}
    for p in players:
        try:
            out = call(*build_research_prompt(p, board, prompts_dir))
            # Any call, real or injected, can come back empty. That is a failure for this player.
            if out is None:
                raise WriterError(f"no parsed output for the research on {p.name}")
            claims[p.player_id] = _claims(out)
        except (RefusalError, WriterError, ValidationError, anthropic.AnthropicError) as err:
            log.warning("research failed for %s, so he has no claim: %s", p.name, err)
    missing = bool(players) and not claims
    if missing:
        log.warning("research failed for every player, so the page says the experts are missing")
    buckets: dict[str, list[WaiverPlayer]] = {}
    for key, bucket in board.buckets.items():
        buckets[key] = []
        for p in bucket:
            found = claims.get(p.player_id, [])
            buckets[key].append(
                p.model_copy(update={"research": found, "facts": [*p.facts, *research_facts(p, found)]})
            )
    return board.model_copy(update={"buckets": buckets, "experts_missing": missing})
