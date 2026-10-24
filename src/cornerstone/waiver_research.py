"""
The research step of the waiver board: per ranked player, a web search for expert takes and news.
The search call is a parameter, so a test injects a fake and the build passes the real Claude call.
"""
import logging
import re
from collections.abc import Callable

import anthropic
from pydantic import ValidationError

from cornerstone.models import Fact, ResearchClaim, ResearchOut, WaiverBoard, WaiverPlayer
from cornerstone.sheet import Nums, fact
from cornerstone.tunables import CLAIMS_PER_PLAYER, RESEARCH_PLAYERS
from cornerstone.writer import RefusalError, WriterError, load_prompt, parse_call

log = logging.getLogger(__name__)

# (system, user) -> the claims on one player. Tests pass a fake in place of Claude.
SearchCall = Callable[[str, str], ResearchOut]

# The drops bucket holds rostered players. A take on a player to drop is not a waiver take, so he gets no search.
DROPS = "drops"

# The dynamic filter version keeps only the relevant parts of each page in the context, so a call reads fewer
# tokens. Three searches find the Yahoo pages and one wider search, and they cap the cost of one player.
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 3}
# A waiver take is a short lookup, not a deep analysis, so the call trades depth for speed and cost.
RESEARCH_EFFORT = "low"

# A claim cites its source by URL, so a claim with no web URL has no citation.
WEB_URL = re.compile(r"^https?://\S+$")


def search_call(system: str, user: str) -> ResearchOut:
    """The real search: one Claude call with the web search tool, parsed into the claims on one player."""
    return parse_call(user, ResearchOut, system, effort=RESEARCH_EFFORT, tools=[WEB_SEARCH_TOOL])


def research_players(board: WaiverBoard) -> list[WaiverPlayer]:
    """The ranked players of every bucket but drops, in bucket order, each once, at most RESEARCH_PLAYERS."""
    seen: dict[str, WaiverPlayer] = {}
    for key, bucket in board.buckets.items():
        if key == DROPS:
            continue
        for p in bucket:
            seen.setdefault(p.player_id, p)
    return list(seen.values())[:RESEARCH_PLAYERS]


def build_research_prompt(p: WaiverPlayer, board: WaiverBoard) -> tuple[str, str]:
    """The system prompt and the user message of the search on one player. The facts let a claim back or dispute them."""
    lines = [
        f"Today is {board.built.date().isoformat()}.",
        f"Player: {p.name}, {p.position}, {p.team}.",
        "",
        "Engine facts:",
        *(f"- {f.text}" for f in p.facts),
        "",
        f"Give at most {CLAIMS_PER_PLAYER} claims.",
    ]
    return load_prompt("research.md"), "\n".join(lines)


def _claims(out: ResearchOut) -> list[ResearchClaim]:
    return [c for c in out.claims if WEB_URL.match(c.url.strip())][:CLAIMS_PER_PLAYER]


def research_facts(p: WaiverPlayer, claims: list[ResearchClaim]) -> list[Fact]:
    """One fact per claim, `WV.research.{player_id}.{n}`: the sentence, the source, and the URL as the citation.

    The numbers hold the digits of the sentence and the source only. The digits of the URL are the citation.
    """
    facts = []
    for i, claim in enumerate(claims, start=1):
        n = Nums()
        text = f"{n.text(claim.text.strip())} ({n.text(claim.source.strip())}) {claim.url.strip()}"
        facts.append(fact(f"WV.research.{p.player_id}.{i}", text, n, [], [p.name]))
    return facts


def research_board(board: WaiverBoard, call: SearchCall) -> WaiverBoard:
    """The board with the research claims and the research facts of each ranked player.

    A failure for one player logs and leaves him with no claim. A failure for every player also sets
    `experts_missing`, and the build goes on.
    """
    players = research_players(board)
    claims: dict[str, list[ResearchClaim]] = {}
    for p in players:
        try:
            out = call(*build_research_prompt(p, board))
            # Any call, real or injected, can come back empty. That is a failure for this player.
            if out is None:
                raise WriterError(f"no parsed output for the research on {p.name}")
            claims[p.player_id] = _claims(out)
        except (RefusalError, WriterError, ValidationError, anthropic.AnthropicError) as err:
            log.warning("research failed for %s, so he has no claim: %s", p.name, err)
    missing = bool(players) and not claims
    if missing:
        log.warning("research failed for every player, so the page says the experts are missing")
    buckets = {
        key: [p.model_copy(update={"research": claims.get(p.player_id, []),
                                   "facts": [*p.facts, *research_facts(p, claims.get(p.player_id, []))]})
              for p in bucket]
        for key, bucket in board.buckets.items()
    }
    return board.model_copy(update={"buckets": buckets, "experts_missing": missing})
