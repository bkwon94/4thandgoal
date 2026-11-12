"""
The waiver targets of one team, live: the free agents by hard rules, the facts of each one and of the team need, and
the Jev judgment of each one in waves. Code keeps only the hard rules and the cost cap. Jev decides who is worth a claim.
"""
import logging
from dataclasses import dataclass

from analyzer.jev_waves import JevWaves, WaveRequest
from analyzer.trade_jev import TRADE_POSITIONS, YES_AT, weak_starting_slots
from cornerstone_api.personal_wording import waiver_questions
from league.history import player_points
from league.jev_port import Jev, JevError
from league.lineup import allowed_positions, lineup_now
from league.projection import next_week, rest_of_season
from league.provider.raw import RawTrending
from league.ranks import OUT_STATUSES, STATUS_WORDS
from league.snapshot import Snapshot, SnapshotPlayer

log = logging.getLogger(__name__)

# The cost cap of the candidates, not a judgment: each candidate is one Jev request, and one run must stay under about
# 60 requests with the claim check. So the pool takes the most added free agents of the day, then the best week
# projections at each position, then the best rest of season projections at each position, for a stash who is out now.
# The union holds at most 16 + 4 x (6 + 2) = 48 players.
TOP_BY_ADDS = 16
TOP_BY_WEEK_PER_POSITION = 6
TOP_BY_REST_PER_POSITION = 2
# The weeks of the usage facts of each candidate, the last weeks with stats, so Jev sees a role grow or shrink.
RECENT_WEEKS = 3
# The weeks from the trade week on in which a starter on bye leaves a slot that a free agent can fill.
BYE_WEEKS_AHEAD = 3
# The rows of the block and the players that Claude reads, best first by the Jev score. The Answer is 2 to 4
# sentences, so it cannot name more, and the card stays one screen on a phone.
KEPT_MAX = 8


def _by_week(snapshot: Snapshot) -> dict[int, dict[str, float]]:
    """The projections ahead by week and player id, from the trade week on. No file gives no projections."""
    by_week: dict[int, dict[str, float]] = {}
    for pid, weeks in (snapshot.projections_ahead or {}).items():
        for week, points in weeks.items():
            if week >= snapshot.week:
                by_week.setdefault(week, {})[pid] = points
    return by_week


def week_projection(by_week: dict[int, dict[str, float]], snapshot: Snapshot, pid: str) -> float:
    """The projection of the trade week. The waiver package counts from the week before, so it reads week N here."""
    return next_week(by_week, pid, snapshot.week - 1)


def rest_projection(by_week: dict[int, dict[str, float]], snapshot: Snapshot, pid: str) -> float:
    """The sum of the projections from the trade week to the last season week of the client."""
    return rest_of_season(by_week, pid, snapshot.week - 1, snapshot.client)


def candidates(snapshot: Snapshot, trending: list[RawTrending]) -> list[SnapshotPlayer]:
    """The free agents worth a Jev read, by hard rules only: on no roster now, at a trade position, with a week or a
    rest of season projection above 0, inside the cost cap. The order is the order of the cap, for one key."""
    by_week = _by_week(snapshot)
    adds = {row.player_id: row.count for row in trending}
    pool = [player for position in TRADE_POSITIONS for player in snapshot.free_agents.get(position, [])
            if week_projection(by_week, snapshot, player.player_id) > 0
            or rest_projection(by_week, snapshot, player.player_id) > 0]
    picked: dict[str, SnapshotPlayer] = {}

    def take(players: list[SnapshotPlayer]) -> None:
        for player in players:
            picked.setdefault(player.player_id, player)

    added = [player for player in pool if adds.get(player.player_id, 0) > 0]
    take(sorted(added, key=lambda p: (-adds[p.player_id], p.player_id))[:TOP_BY_ADDS])
    for position in TRADE_POSITIONS:
        at = [player for player in pool if player.position == position]
        take(sorted(at, key=lambda p: (-week_projection(by_week, snapshot, p.player_id), p.player_id))
             [:TOP_BY_WEEK_PER_POSITION])
        take(sorted(at, key=lambda p: (-rest_projection(by_week, snapshot, p.player_id), p.player_id))
             [:TOP_BY_REST_PER_POSITION])
    return list(picked.values())


def _bye(snapshot: Snapshot, nfl_team: str | None) -> int | None:
    schedule = None if snapshot.schedules is None or nfl_team is None else snapshot.schedules.get(nfl_team)
    return None if schedule is None else schedule.bye_week


def _status(player: SnapshotPlayer) -> str:
    return STATUS_WORDS.get(player.injury_status or "", player.injury_status or "healthy")


def _out_now(snapshot: Snapshot, player: SnapshotPlayer) -> bool:
    """True when the player cannot play now: an out status of the injury report, or out for the season."""
    return player.injury_status in OUT_STATUSES or player.player_id in snapshot.out_for_season


def _recent(snapshot: Snapshot, pid: str) -> list[dict]:
    """The points, the snap share, the targets, and the carries of each of the last weeks with stats."""
    through = snapshot.as_of.stats_through
    weeks = []
    for week in range(through - RECENT_WEEKS + 1, through + 1):
        past = snapshot.stats.weeks.get(week)
        line = None if past is None else past.stats.get(pid)
        if past is None or not line:
            weeks.append({"week": week, "played": False})
            continue
        team_snaps = line.get("tm_off_snp", 0.0)
        weeks.append({"week": week, "played": True, "points": player_points(past, pid),
                      "snap_share_percent": round(100 * line.get("off_snp", 0.0) / team_snaps) if team_snaps else None,
                      "targets": int(line.get("rec_tgt", 0.0)), "carries": int(line.get("rush_att", 0.0))})
    return weeks


def _above(snapshot: Snapshot, player: SnapshotPlayer) -> list[SnapshotPlayer]:
    """The players above him on the depth chart of his NFL team at his position, from the one right above him up to the
    starter. The snapshot joins the chart to Sleeper ids, as the sneaky bucket of the waiver board reads it."""
    chain: list[SnapshotPlayer] = []
    seen = {player.player_id}
    ahead = snapshot.ahead_on_chart.get(player.player_id)
    while ahead is not None and ahead.player_id not in seen:
        chain.append(ahead)
        seen.add(ahead.player_id)
        ahead = snapshot.ahead_on_chart.get(ahead.player_id)
    return chain


def _on_chart(snapshot: Snapshot, player: SnapshotPlayer) -> bool:
    gsis = (snapshot.id_map or {}).get(player.player_id)
    chart = (snapshot.depth_charts or {}).get(player.nfl_team or "", {}).get(player.position, [])
    return gsis is not None and gsis in chart


def _depth(snapshot: Snapshot, player: SnapshotPlayer) -> dict:
    """The depth chart facts of one free agent: his place, each player above him and whether he is out now, and
    whether every player above him is out. With no chart, or off the chart, the facts say so."""
    above = _above(snapshot, player)
    if snapshot.depth_charts is None:
        return {"depth_chart": "none"}
    if not above and not _on_chart(snapshot, player):
        return {"depth_chart": "not listed"}
    return {"depth_chart_place": len(above) + 1,
            "players_above": [{"name": p.name, "status": _status(p), "out_now": _out_now(snapshot, p),
                               "return_week": snapshot.returns.get(p.player_id)} for p in reversed(above)],
            "every_player_above_is_out": bool(above) and all(_out_now(snapshot, p) for p in above)}


def _starters(snapshot: Snapshot, roster_id: int, by_week: dict[int, dict[str, float]]) -> list[dict]:
    """The starters of the best lineup of the players who can play now, each with his week projection and his bye."""
    rows = []
    for slot in lineup_now(snapshot.rosters[roster_id], snapshot):
        if slot.player is None:
            rows.append({"slot": slot.name, "allows": sorted(allowed_positions(slot.roster_slot)), "player": None})
            continue
        player = snapshot.players[slot.player]
        if player.position not in TRADE_POSITIONS:
            continue
        rows.append({"slot": slot.name, "allows": sorted(allowed_positions(slot.roster_slot)), "player": player.name,
                     "position": player.position, "week_projection": week_projection(by_week, snapshot, slot.player),
                     "bye_week": _bye(snapshot, player.nfl_team)})
    return rows


def team_need(snapshot: Snapshot, roster_id: int) -> dict:
    """The need facts of the team: its weak starting slots, its starters with their week projections, the weakest
    starter at each position, and each starter whose bye falls in the next weeks. A starter on IR fills no slot."""
    by_week = _by_week(snapshot)
    starters = _starters(snapshot, roster_id, by_week)
    weakest: dict[str, dict | None] = {}
    for position in TRADE_POSITIONS:
        # A slot of his own position with no player who can play now is the weakest start there.
        empty = next((s for s in starters if s["player"] is None and s["allows"] == [position]), None)
        at = [s for s in starters if s["player"] is not None and s["position"] == position]
        weakest[position] = (
            {"slot": empty["slot"], "player": None} if empty is not None
            else None if not at
            else {key: min(at, key=lambda s: (s["week_projection"], s["slot"]))[key]
                  for key in ("slot", "player", "week_projection")})
    last = snapshot.week + BYE_WEEKS_AHEAD - 1
    byes = [{"slot": s["slot"], "player": s["player"], "bye_week": s["bye_week"]} for s in starters
            if s["player"] is not None and s["bye_week"] is not None and snapshot.week <= s["bye_week"] <= last]
    return {"name": snapshot.teams[roster_id].name, "weak_starting_slots": weak_starting_slots(snapshot, roster_id),
            "starters": starters,
            "weakest_starter_by_position": weakest,
            "starter_byes_ahead": byes}


def candidate_facts(snapshot: Snapshot, player: SnapshotPlayer, trending: list[RawTrending],
                    starters: list[dict]) -> dict:
    """The facts of one free agent: who he is, the projections, the last weeks, the Sleeper adds, the depth chart, and
    each starter of the team whom he outprojects this week in a slot that takes his position."""
    by_week = _by_week(snapshot)
    pid = player.player_id
    week = week_projection(by_week, snapshot, pid)
    adds = next((row.count for row in trending if row.player_id == pid), 0)
    beats = [f"{s['slot']}: {s['player']} ({s['week_projection']})" for s in starters
             if s["player"] is not None and player.position in s["allows"] and week > s["week_projection"]]
    empty = [s["slot"] for s in starters if s["player"] is None and player.position in s["allows"]]
    return {"player_id": pid, "name": player.name, "position": player.position, "nfl_team": player.nfl_team,
            "status": _status(player), "bye_week": _bye(snapshot, player.nfl_team),
            "week_projection": week, "rest_of_season_projection": rest_projection(by_week, snapshot, pid),
            "last_weeks": _recent(snapshot, pid), "sleeper_adds_last_day": adds,
            **_depth(snapshot, player),
            "starters_he_outprojects_this_week": beats, "empty_slots_he_fits": empty}


def waiver_facts(snapshot: Snapshot, roster_id: int, trending: list[RawTrending]) -> tuple[dict, list[dict]]:
    """The team need and the facts of each candidate, the input of the Jev read and of the key of the Answer."""
    need = team_need(snapshot, roster_id)
    return need, [candidate_facts(snapshot, player, trending, need["starters"])
                  for player in candidates(snapshot, trending)]


@dataclass(frozen=True)
class Judged:
    """The Jev read of the candidates: the kept players best first, each with his kind, and the cost of the read."""

    kept: list[dict]
    requests: int
    input_tokens: int


def judge(jev: Jev, week: int, need: dict, players: list[dict]) -> Judged:
    """One Jev request per candidate, in waves: is he a real add this week, and is he a clear stash for later weeks.

    Code reads the cutoff only: a player is kept when either answer is above the yes line, best first by the higher
    answer. A failed request raises JevError, because a failed read is never a no.
    """
    requests = {
        player["player_id"]: WaveRequest(state={"week": week, "team": need, "player": _shown(player)},
                                         questions=waiver_questions(player["name"], need["name"], week))
        for player in players}
    answers = JevWaves(jev).ask(requests, "waiver targets")
    failed = [key for key, answer in answers.items() if answer is None]
    if failed:
        raise JevError(f"{len(failed)} of {len(answers)} waiver reads failed")
    tokens = sum(answer.input_tokens or 0 for answer in answers.values() if answer is not None)
    scored = []
    read = []
    for player in players:
        answer = answers[player["player_id"]]
        assert answer is not None
        add, stash = answer.nouls["add"], answer.nouls["stash"]
        read.append(f"{player['name']} {add:.2f}/{stash:.2f}")
        if max(add, stash) > YES_AT:
            kind = "add this week" if add > YES_AT else "stash for later weeks"
            scored.append((max(add, stash), {**_shown(player), "kind": kind}))
    scored.sort(key=lambda item: (-item[0], item[1]["name"]))
    log.info("The waiver read: %d requests, %d input tokens, %d of %d kept", len(requests), tokens, len(scored),
             len(players))
    # The add and the stash answer of each player read, so a run shows why a free agent stayed or left.
    log.info("The waiver answers, add/stash: %s", "; ".join(read))
    return Judged(kept=[player for _, player in scored[:KEPT_MAX]], requests=len(requests), input_tokens=tokens)


def _shown(player: dict) -> dict:
    """The facts of a player as Jev and Claude read them: every fact but the Sleeper id."""
    return {key: value for key, value in player.items() if key != "player_id"}


# The kind of the data block of the waiver targets: one row per kept free agent, and his why opens in place.
WAIVER_LIST_KIND = "waiver_list"
# The slot of a free agent who beats no starter and fits no empty slot, such as a stash who is out now.
BENCH = "Bench"


def slot_he_fills(need: dict, player: dict) -> str:
    """The slot that a kept free agent takes: an empty slot that allows his position, else the slot of the starter with
    the lowest week projection that he outprojects, else the bench."""
    if player["empty_slots_he_fits"]:
        return player["empty_slots_he_fits"][0]
    beaten = [s for s in need["starters"] if s["player"] is not None and player["position"] in s["allows"]
              and player["week_projection"] > s["week_projection"]]
    return min(beaten, key=lambda s: (s["week_projection"], s["slot"]))["slot"] if beaten else BENCH


def _why(need: dict, player: dict, slot: str) -> list[str]:
    """The why of one kept free agent in plain lines from his facts: the read of Jev first, then his status, the slot,
    the depth chart, the Sleeper adds, and the rest of the season. Code picks no player here. It only says what the facts say."""
    lines = ["Worth a claim this week." if player["kind"] == "add this week" else "A stash for later weeks."]
    if player["status"] != "healthy":
        lines.append(f"Status now: {player['status']}.")
    if slot in player["empty_slots_he_fits"]:
        lines.append(f"Fills your empty {slot} slot.")
    elif slot != BENCH:
        starter = next(s for s in need["starters"] if s["slot"] == slot)
        lines.append(f"Projects {player['week_projection']:.1f} this week, over {starter['player']} at "
                     f"{starter['week_projection']:.1f} in your {slot} slot.")
    if player.get("every_player_above_is_out"):
        lines.append("Every player above him on the depth chart is out.")
    if player["sleeper_adds_last_day"] > 0:
        lines.append(f"{player['sleeper_adds_last_day']:,} adds across Sleeper in the last day.")
    lines.append(f"{player['rest_of_season_projection']:.1f} projected points for the rest of the season.")
    return lines


def waiver_rows(need: dict, kept: list[dict]) -> list[dict]:
    """The rows of the waiver list, best first as Jev kept them: who he is, his week projection, the slot he fills, the
    kind of the claim, and his why."""
    rows = []
    for player in kept:
        slot = slot_he_fills(need, player)
        rows.append({"name": player["name"], "position": player["position"], "nfl_team": player["nfl_team"],
                     "projection": player["week_projection"], "slot": slot,
                     "kind": "add" if player["kind"] == "add this week" else "stash",
                     "why": _why(need, player, slot)})
    return rows
