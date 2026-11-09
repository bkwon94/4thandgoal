"""
The news of the trade players: the Sleeper news feed of each player, kept in memory for 1 hour, as NEWS facts.
It also holds the attribution guard: a Bullet that cites a NEWS fact must name the report, so a rumor stays a rumor.
"""
import logging
import re
import time
from collections.abc import Callable, Iterable
from datetime import UTC, datetime, timedelta

from facts.tokens import Nums, fact
from league.models import Fact
from league.provider.sleeper import fetch_news
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

FACT_PREFIX = "NEWS."
# The trade deadline rumor lives for days, so the sheet reads only the newest items of the last week (decision 08).
NEWS_PER_PLAYER = 2
NEWS_MAX_AGE = timedelta(days=7)
NEWS_MAX_CHARS = 300
# The feed changes within the day, so one hour keeps a read current and spares a second press its calls.
CACHE_SECONDS = 60 * 60
# The sources of the feed as a reader knows them. Another source reads as its key in title case.
SOURCE_NAMES = {"rotoballer": "Rotoballer", "rotowire": "Rotowire", "fantasy_pros": "FantasyPros"}
# A Bullet that cites a NEWS fact holds one of these words, or the source name of the fact.
ATTRIBUTION = re.compile(r"(?<![\w-])(?:reported|reports?|per|according to|rumou?rs?|rumou?red)(?![\w-])",
                         re.IGNORECASE)
SOURCE_IN_TEXT = re.compile(r"^Reported on \S+ by (.+?): ")


class NewsFeed:
    """The news items of each player by id, from `fetch`, each kept for CACHE_SECONDS of `clock`.

    `now` gives the time that the window of NEWS_MAX_AGE ends at. A fetch that raises gives no items, logs, and is
    not kept, so the next press tries again.
    """

    def __init__(self, fetch: Callable[[str], list[dict]] = fetch_news, *,
                 clock: Callable[[], float] = time.monotonic, now: Callable[[], datetime] = lambda: datetime.now(UTC)):
        self.fetch = fetch
        self.clock = clock
        self.now = now
        self._kept: dict[str, tuple[float, list[dict]]] = {}

    def items(self, player_id: str) -> list[dict]:
        kept = self._kept.get(player_id)
        if kept is not None and self.clock() - kept[0] < CACHE_SECONDS:
            log.info("News of player %s from the cache", player_id)
            return kept[1]
        # The endpoint is unofficial and can change with no notice, so no failure of it stops a read.
        try:
            items = self.fetch(player_id)
        except Exception:
            log.exception("The news fetch of player %s failed, so the sheet has no news of him", player_id)
            return []
        log.info("News fetch of player %s: %d items", player_id, len(items))
        self._kept[player_id] = (self.clock(), items)
        return items


# The one feed of the API process, so the cache holds across presses.
NEWS = NewsFeed()


def _published(item: dict) -> datetime | None:
    # "published" is epoch milliseconds, as a number or a string.
    try:
        return datetime.fromtimestamp(int(item.get("published") or 0) / 1000, UTC)
    except (TypeError, ValueError):
        return None


def _cut_at_word(text: str, limit: int) -> str:
    """Cut at the last whitespace before the limit, so no word or number is cut in half."""
    if len(text) <= limit:
        return text
    head = text[:limit]
    space = max(head.rfind(" "), head.rfind("\n"), head.rfind("\t"))
    return (head[:space] if space > 0 else head).rstrip()


def _source(key: str) -> str:
    return SOURCE_NAMES.get(key) or key.replace("_", " ").title() or "an unnamed source"


def news_facts(player_ids: Iterable[str], snapshot: Snapshot, feed: NewsFeed) -> dict[str, Fact]:
    """The NEWS facts of each player by id, such as NEWS.6813.1: the newest NEWS_PER_PLAYER items of the last
    NEWS_MAX_AGE, newest first. An item with no description drops. The URL never reaches the text or the numbers."""
    now = feed.now()
    tz = snapshot.client.tz
    facts: dict[str, Fact] = {}
    for pid in dict.fromkeys(player_ids):
        dated = [(at, item) for item in feed.items(pid) if (at := _published(item)) is not None
                 and now - NEWS_MAX_AGE <= at <= now and (item.get("metadata") or {}).get("description")]
        # The feed promises no order.
        dated.sort(key=lambda pair: pair[0], reverse=True)
        name = snapshot.players[pid].name if pid in snapshot.players else pid
        for n, (at, item) in enumerate(dated[:NEWS_PER_PLAYER], start=1):
            nums = Nums()
            day = nums.text(at.astimezone(tz).date().isoformat())
            description = nums.text(_cut_at_word(item["metadata"]["description"].strip(), NEWS_MAX_CHARS))
            fid = f"{FACT_PREFIX}{pid}.{n}"
            text = f"Reported on {day} by {_source(str(item.get('source') or ''))}: {description}"
            facts[fid] = fact(fid, text, nums, [], [name])
    return facts


def attribution_failures(label: str, text: str, fact_id: str, facts: dict[str, Fact]) -> list[str]:
    """The failure of a Bullet that cites a NEWS fact and does not name the report. Empty for any other Bullet."""
    if not fact_id.startswith(FACT_PREFIX) or ATTRIBUTION.search(text):
        return []
    source = SOURCE_IN_TEXT.match(facts[fact_id].text)
    if source and source.group(1).lower() in text.lower():
        return []
    return [f"{label}: it cites the news fact {fact_id}, so it must say 'reported', 'per', or the source"]
