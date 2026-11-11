"""
The Suggestions of Your team, the head start of the top personal Suggestion, and the check of the keys of kept Answers.
Jev picks the sell high player and lifts a Topic when its fact is urgent. Code keeps the cutoffs, the order, the pick.
"""
import json
import logging
from typing import cast, get_args

import anyio
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai.models import Model

from analyzer.routes import ServedClient
from analyzer.sell_facts import sell_sheet, sheet_players
from cornerstone_api.answer_store import AnswerStore
from cornerstone_api.ask import YES, Asker, ClientAsker
from cornerstone_api.ask_wording import TOPICS
from cornerstone_api.personal_facts import PersonalTopic, trade_ideas_fact
from cornerstone_api.personal_topics import Live, claude_answer, load_live
from cornerstone_api.suggestion_wording import (
    SELL_CHOICE,
    SELL_NOUL,
    lift_key,
    lift_questions,
    lift_state,
    sell_questions,
    sell_state,
)
from cornerstone_api.trade_topics import TradeTopic, trade_key
from cornerstone_api.trade_wording import option_keys
from league.jev_port import Jev, JevError
from league.paths import week_label
from league.ranks import recent_points_per_game, season_points_per_game
from league.tunables import LINEUP_WEEKS

logger = logging.getLogger(__name__)

router = APIRouter()

# The front door shows 3 Suggestions plus "More" (decision 02).
SUGGESTION_COUNT = 3
# The 3 personal Topics, which the API builds live. The head start builds only one of them.
PERSONAL: tuple[PersonalTopic, ...] = ("weak_spots", "stack_up", "waiver_targets")
# The file of the weekly build with the Answers and the facts of the 7 league Topics of each team.
TOPICS_FILE = "topics.json"
# The trade Topics, whose key covers the rosters that the Answer read.
TRADE_TOPICS: tuple[str, ...] = get_args(TradeTopic)
# The Answers in one key check. A Thread of one week holds far fewer personal Answers.
CHECK_MAX = 50

# The keys of the head starts in flight, so two opens at once build one Answer. The app runs one event loop.
_building: set[str] = set()


class SuggestionsRequest(BaseModel):
    """The body of the Suggestions: Your team, the 13 Topics in the order of the day of the manager, and the fact of
    each Topic that the manager opened. The browser knows the day and keeps the opened Topics (decision 02)."""

    model_config = ConfigDict(extra="ignore")

    roster_id: int
    order: list[str] = Field(min_length=1, max_length=len(TOPICS))
    opened: dict[str, str] = Field(default_factory=dict, max_length=len(TOPICS))


class KeyItem(BaseModel):
    """One personal or trade Answer of the Thread: its Topic, the roster id of Your team, the team it is about or None
    for Your team, and its key. The team of a trade Answer is its partner, or None for trade ideas with no partner and
    for sell high."""

    topic: PersonalTopic | TradeTopic
    roster_id: int
    team: int | None = None
    key: str = Field(max_length=128)


class CurrentRequest(BaseModel):
    """The body of the key check: the personal and trade Answers of the Thread, each with its key."""

    answers: list[KeyItem] = Field(max_length=CHECK_MAX)


def league_facts(live: Live, roster_id: int) -> dict[str, str]:
    """The fact of each league Topic of the team, from the Topics file of the latest published week up to now."""
    snapshot = live.snapshot
    season_dir = snapshot.client.folder / "published" / str(snapshot.season)
    for each in range(snapshot.week, 0, -1):
        path = season_dir / week_label(each) / TOPICS_FILE
        if path.exists():
            teams = json.loads(path.read_text(encoding="utf-8"))["teams"]
            return {answer["topic"]: answer["fact"] for answer in teams.get(str(roster_id), [])}
    return {}


def _who(live: Live, pid: str) -> str:
    player = live.snapshot.players[pid]
    return f"{player.name} ({player.position}, {player.nfl_team})" if player.nfl_team else player.name


def sell_high_fact(jev: Jev, live: Live, roster_id: int) -> tuple[str | None, dict[str, float], float | None]:
    """The fact of the sell high Suggestion: the player whose recent run Jev reads as most past his season, with his
    points per game over the recent weeks and the season. Code gives the facts side by side and screens no player.
    The Choice spreads its weight over the roster, so the Noul in the same request carries the cutoff: a Noul at or
    below YES is unsure, so sell high has no fact this time. The probability of each option and the Noul come back
    too, for the log of a run. A failed request raises JevError."""
    snapshot = live.snapshot
    players = sheet_players(snapshot, roster_id)
    if not players:
        return None, {}, None
    sheet = sell_sheet(snapshot, roster_id)
    keys = option_keys({pid: snapshot.players[pid].name for pid in players})
    state = sell_state(snapshot.teams[roster_id].name, snapshot.week, {
        keys[pid]: {"name": snapshot.players[pid].name,
                    "facts": [fact.text for fact_id, fact in sheet.items() if fact_id.split(".")[0] == pid]}
        for pid in players})
    answers = jev.ask(state, sell_questions({keys[pid]: _who(live, pid) for pid in players}))
    probabilities = answers.choices[SELL_CHOICE]
    clear = answers.nouls[SELL_NOUL]
    if clear <= YES:
        return None, probabilities, clear
    top = max(probabilities, key=lambda option: probabilities[option])
    pid = next(pid for pid, key in keys.items() if key == top)
    # The same rounding as the trend fact of the sell sheet, so the chip and the fact that Jev read say one number.
    recent = float(round(recent_points_per_game(snapshot, pid), 1))
    season = float(round(season_points_per_game(snapshot, pid), 1))
    fact = f"{snapshot.players[pid].name}: {recent} a game over {LINEUP_WEEKS} weeks, {season} for the season"
    return fact, probabilities, clear


def pick(order: list[str], urgent: list[str], facts: dict[str, str], opened: dict[str, str]) -> list[str]:
    """The hard rule of the pick: the urgent Topics first, then the order of the day. A Topic needs a fact to show, and
    a Topic opened at the same fact waits until its fact changes."""
    ranked = [*urgent, *(key for key in order if key not in urgent)]
    return [key for key in ranked if key in facts and opened.get(key) != facts[key]][:SUGGESTION_COUNT]


async def head_start(asker: Asker, store: AnswerStore, live: Live, topic: PersonalTopic, roster_id: int,
                     model: Model | None) -> None:
    """Build the Answer of `topic` for Your team on open, so the tap streams it back kept (decision 11). It runs after
    the Suggestions response. The route asks the league cap first. A kept Answer of the same key builds nothing."""
    facts, key = live.key(topic, roster_id, roster_id)
    if key in _building or await anyio.to_thread.run_sync(store.get, key) is not None:
        return
    _building.add(key)
    try:
        logger.info("The head start builds the personal Topic %s on open", topic)
        your_team = live.snapshot.teams[roster_id].name
        async for _ in claude_answer(asker, store, topic, facts, key, True, your_team, model, None):
            pass
    finally:
        _building.discard(key)


@router.post("/suggestions")
async def suggestions(body: SuggestionsRequest, asker: ClientAsker, served: ServedClient, request: Request,
                      tasks: BackgroundTasks) -> dict:
    """The Suggestions of Your team: the fact of each Topic, the lift Noul of each, the urgent Topics, and the 3
    picks. When the top pick is a personal Topic, its Answer builds after the response. A failed Jev call is a 503."""
    if any(key not in TOPICS for key in [*body.order, *body.opened]) or len(set(body.order)) != len(body.order):
        raise HTTPException(status_code=422, detail="Unknown Topic.")
    live = await load_live(served, asker.season, request.app.state.live[request.path_params["slug"]])
    if body.roster_id not in live.snapshot.rosters:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    facts = await anyio.to_thread.run_sync(league_facts, live, body.roster_id)
    for topic in PERSONAL:
        facts[topic] = (await anyio.to_thread.run_sync(live.facts, topic, body.roster_id)).block["fact"]
    # The trade check has no weekly fact, so it stays in "More" only.
    ideas = trade_ideas_fact(live.snapshot, body.roster_id)
    if ideas is not None:
        facts["trade_ideas"] = ideas
    team = live.snapshot.teams[body.roster_id].name
    try:
        sell, sell_choice, sell_clear = await anyio.to_thread.run_sync(sell_high_fact, asker.jev, live,
                                                                       body.roster_id)
        if sell is not None:
            facts["sell_high"] = sell
        answers = await anyio.to_thread.run_sync(asker.jev.ask, lift_state(team, live.snapshot.week, facts),
                                                 lift_questions(facts))
    except JevError as error:
        logger.warning("The lift of the Suggestions failed (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="The Suggestions did not load.") from None
    lifts = {topic: answers.nouls[lift_key(topic)] for topic in facts}
    # The cutoff is the hard rule of the spec: only a lift above YES is urgent. The most urgent leads.
    urgent = sorted((topic for topic, p in lifts.items() if p > YES), key=lambda topic: -lifts[topic])
    picks = pick(body.order, urgent, facts, body.opened)
    top = picks[0] if picks else None
    start = top if top in PERSONAL else None
    # The head start counts toward the league cap only, so only the league cap stops it (decision 04). A check with no
    # team reads only the league cap, because no roster has the id None.
    if start is not None and (hit := await anyio.to_thread.run_sync(asker.caps.check, None, asker.clock())) is not None:
        logger.info("The head start of %s stopped at the %s cap, with no Claude call", start, hit.cap)
        start = None
    if start is not None:
        store: AnswerStore = request.app.state.kept[request.path_params["slug"]]
        tasks.add_task(head_start, asker, store, live, start, body.roster_id, request.app.state.personal_model)
    # The sell high Noul joins the lift Nouls in the log, so a run shows why sell high has a fact or none.
    nouls = answers.nouls if sell_clear is None else {**answers.nouls, SELL_NOUL: sell_clear}
    return {"picks": picks, "facts": facts, "lifts": lifts, "urgent": urgent, "head_start": start,
            "jev": {"model": answers.model, "nouls": nouls, "choices": {SELL_CHOICE: sell_choice}}}


@router.post("/personal/current")
async def current(body: CurrentRequest, asker: ClientAsker, served: ServedClient, request: Request) -> dict:
    """Whether the key of each Answer of the Thread is still the key of its data now. It costs nothing: no Claude call
    and no Jev call. A stale personal Answer gets the time that the store kept it, for the stale line. The store keeps
    no trade Answer, so the site keeps the time of its read from the stream."""
    live = await load_live(served, asker.season, request.app.state.live[request.path_params["slug"]])
    rosters = live.snapshot.rosters
    if any(item.roster_id not in rosters or (item.team is not None and item.team not in rosters)
           for item in body.answers):
        raise HTTPException(status_code=422, detail="Pick your team again.")
    store: AnswerStore = request.app.state.kept[request.path_params["slug"]]

    def check(item: KeyItem) -> dict:
        if item.topic in TRADE_TOPICS:
            key = trade_key(cast(TradeTopic, item.topic), rosters, item.roster_id, item.team)
            return {"key": item.key, "current": key == item.key, "kept_at": None}
        subject = item.roster_id if item.team is None else item.team
        _, key = live.key(cast(PersonalTopic, item.topic), item.roster_id, subject)
        return {"key": item.key, "current": key == item.key, "kept_at": store.kept_at(item.key)}

    return {"answers": [await anyio.to_thread.run_sync(check, item) for item in body.answers]}
