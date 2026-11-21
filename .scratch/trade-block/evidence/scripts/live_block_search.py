"""
Evidence script of trade-block AT-1 to AT-5, AT-7, and AT-9: the live cpc snapshot with Bo Girds as the asker.
It builds the snapshot as the API does, runs the Finder search with the fixed FakeJev, and prints what each Then names.
Cam Skattebo stands in for Kenneth Walker III, who is Out with no return week (the Revisions line of ACCEPTANCE.md).
"""
import argparse
import logging
import sys
from datetime import datetime
from functools import partial
from pathlib import Path

from analyzer.cache import finder_cache_key
from analyzer.finder_pick import build_pick_prompt, offer_sheets
from analyzer.finder_search import (
    _out_with_no_return,
    _sends_block,
    in_pool,
    offer_id,
    search,
    value_offers,
)
from analyzer.measures import is_handcuff
from analyzer.trade_news import NewsFeed
from cornerstone_api.sources import Sources
from cornerstone_api.value_models import VALUE_MODELS
from league.chart import chart_values
from league.claude_errors import WriterError
from league.client import load_client
from league.nflverse import http_get
from league.paths import provider_cache_dir
from league.provider.sleeper import SleeperProvider, fetch_settings


def no_claude_read(_png: bytes):
    """The chart reader of the script. The saved week read serves the chart, so no Claude call runs."""
    raise WriterError("the evidence script makes no Claude call")


def scattered_fair(key, question, state):
    """The same answer as `_scattered_fair` of apps/pipeline/tests/test_finder_search.py: a fair answer above NO_AT
    that differs from offer to offer, and a clear yes for each other question."""
    n, _, kind = key.partition("|")
    return 0.31 + (int(n) * 7919 % 61) / 100 if kind == "fair" else 0.9


def find_player(snap, roster, last, position):
    """The player of the roster with the last name and position, else the best-valued other player of that position."""
    for pid in snap.rosters[roster]:
        p = snap.players[pid]
        if p.position == position and last in p.name.split():
            return pid, None
    others = sorted((pid for pid in snap.rosters[roster] if snap.players[pid].position == position
                     and in_pool(snap, pid, roster)),
                    key=lambda pid: -(snap.chart.values.get(pid) or 0) if snap.chart else 0)
    return others[0], f"{last} is not on roster {roster}; the stand-in is {snap.players[others[0]].name}"


def sends(snap, trade):
    return ", ".join(snap.players[pid].name for pid in trade.sides[0].player_ids)


def gets(snap, trade):
    return ", ".join(snap.players[pid].name for pid in trade.sides[1].player_ids)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("section", choices=["at1", "at2", "at3", "at4", "at5", "at7", "at9"])
    # Walker is on the roster but Out with no return week on the live snapshot, so he fails the pool rules. The revision
    # of ACCEPTANCE.md that Brian approved puts Cam Skattebo in his place, and the output names him.
    parser.add_argument("--stand-in", default="12481", help="the player id that takes the Walker slot")
    args = parser.parse_args()
    # The fixed Jev of the tests lives in the pipeline tests folder, so the script reads it from there.
    fake_dir = args.repo / "apps" / "pipeline" / "tests"
    sys.path.insert(0, str(fake_dir))
    from fakes import FakeJev, no_news  # noqa: PLC0415

    logging.basicConfig(level=logging.WARNING)
    client = load_client(args.repo, "cpc", None, fetch_settings, VALUE_MODELS)
    sources = Sources(client, clock=lambda: datetime.now(client.tz),
                      fetch_sleeper=SleeperProvider(provider_cache_dir(client.nfl_dir)).fetch_live,
                      fetch_past=http_get, read_chart=partial(chart_values, read=no_claude_read))
    snap = sources.snapshot(2026)
    asker = next((rid for rid, team in snap.teams.items() if "Bo Girds" in (team.name, team.owner)), 6)
    print(f"Live cpc snapshot: season {snap.season}, trade week {snap.as_of.chart_week if snap.as_of.chart_week else '?'}"
          f", rosters fetched {snap.as_of.rosters_fetched}, chart week {snap.chart.week if snap.chart else None}")
    print(f"Asker: roster {asker}, team {snap.teams[asker].name!r}, manager {snap.teams[asker].owner!r}")
    print(f"Roster {asker} on live Sleeper ({len(snap.rosters[asker])} players):")
    for pid in sorted(snap.rosters[asker], key=lambda pid: snap.players[pid].name):
        p = snap.players[pid]
        print(f"  {p.name} id={pid} {p.position} {p.nfl_team} status={p.injury_status} "
              f"return_week={(snap.returns.get(pid) if isinstance(snap.returns, dict) else pid in snap.returns) if pid in snap.returns else None} "
              f"in_pool={in_pool(snap, pid, asker)}")
    real_walker, _ = find_player(snap, asker, "Walker", "RB")
    rw = snap.players[real_walker]
    print(f"Kenneth Walker III: id={real_walker} status={rw.injury_status} "
          f"out_with_no_return_week={_out_with_no_return(snap, real_walker)} in_pool={in_pool(snap, real_walker, asker)}")
    walker = args.stand_in
    w_note = (f"STAND-IN: {rw.name} is on roster {asker} but fails the pool rules (status {rw.injury_status}, "
              f"no return week), so {snap.players[walker].name} takes the place of Walker in this run "
              f"(ACCEPTANCE.md, Revisions, 2026-11-21)")
    flowers, f_note = find_player(snap, asker, "Flowers", "WR")
    for pid, note in ((walker, w_note), (flowers, f_note)):
        p = snap.players[pid]
        print(f"Block player: {p.name} id={pid} {p.position} {p.nfl_team} chart={snap.chart.values.get(pid)}"
              f" in_pool={in_pool(snap, pid, asker)}" + (f" NOTE: {note}" if note else ""))
    block = [walker, flowers]
    # The name of the player in the Walker slot: the stand-in of --stand-in.
    wname = snap.players[walker].name
    print(f"Fixed Jev: FakeJev of apps/pipeline/tests/fakes.py"
          f"{' with scattered_fair' if args.section in ('at2', 'at9') else ' (yes=0.9 for each question)'}")
    print()

    if args.section == "at1":
        found = search(asker, None, snap, FakeJev(), trade_block=block)
        print(f"search(asker={asker}, partner=None, trade_block=[{walker}, {flowers}])")
        print(f"Count of offers: {len(found.offers)}")
        tally = {f"{wname} only": 0, "Flowers only": 0, "both": 0, "neither": 0}
        for trade in found.offers:
            mine = set(trade.sides[0].player_ids)
            w, f = walker in mine, flowers in mine
            tally["both" if w and f else f"{wname} only" if w else "Flowers only" if f else "neither"] += 1
            assert trade.sides[0].roster_id == asker
        print(f"Asker side of each offer: {tally}")
        print(f"Asker side is roster {asker} in every offer: "
              f"{all(t.sides[0].roster_id == asker for t in found.offers)}")
        print("Each offer, asker side (sends) then partner side (gets):")
        for trade in found.offers:
            print(f"  {offer_id(trade)}  sends [{sends(snap, trade)}]  gets [{gets(snap, trade)}]")

    elif args.section == "at2":
        found = search(asker, None, snap, FakeJev(answer=scattered_fair), trade_block=block)
        print(f"Count of offers: {len(found.offers)}; fair means kept: {len(found.fair_means)}; "
              f"unfair: {len(found.unfair)}")
        print(f"Fair offers that send {wname}: {sum(walker in t.sides[0].player_ids for t in found.offers)}; "
              f"that send Flowers: {sum(flowers in t.sides[0].player_ids for t in found.offers)}")
        print(f"The Shortlist ({len(found.shortlist)} offers):")
        for offer in found.shortlist:
            t = offer.trade
            print(f"  {offer.offer_id} score={offer.score:.2f} sends [{sends(snap, t)}] gets [{gets(snap, t)}]")
        sent = [set(o.trade.sides[0].player_ids) for o in found.shortlist]
        print(f"Shortlist offers that send {wname}: {sum(walker in s for s in sent)}")
        print(f"Shortlist offers that send Flowers: {sum(flowers in s for s in sent)}")

    elif args.section == "at3":
        partners = sorted(rid for rid in snap.rosters if rid != asker)
        offers = [t for rid in partners for t in value_offers(asker, rid, snap, trade_block=block)]
        package = [t for t in offers if {walker, flowers} <= set(t.sides[0].player_ids)]
        print(f"value_offers(asker={asker}, each partner, trade_block=[{walker}, {flowers}]): {len(offers)} offers")
        print(f"Offers that send {wname} and Flowers together: {len(package)}")
        for t in package:
            print(f"  {offer_id(t)} sends [{sends(snap, t)}] gets [{gets(snap, t)}] "
                  f"_sends_block={_sends_block(t, block)}")

    elif args.section == "at4":
        # The roster has no handcuff RB, so the player who fails the pool rules is Walker himself: Out, no return week.
        rbs = [pid for pid in snap.rosters[asker] if snap.players[pid].position == "RB"]
        print(f"RBs of roster {asker}: " + ", ".join(
            f"{snap.players[p].name} (handcuff={is_handcuff(snap, p, asker)})" for p in rbs))
        failed = real_walker
        p = snap.players[failed]
        print(f"Pool-failing block player: {p.name} id={failed} {p.position}, status {p.injury_status}, "
              f"out_with_no_return_week={_out_with_no_return(snap, failed)}, handcuff={is_handcuff(snap, failed, asker)}, "
              f"in_pool={in_pool(snap, failed, asker)}, chart={snap.chart.values.get(failed)}")
        try:
            found = search(asker, None, snap, FakeJev(), trade_block=[failed, walker])
            print(f"search(asker={asker}, partner=None, trade_block=[{failed}, {walker}]) raised no error")
        except Exception as error:  # noqa: BLE001 - the evidence names any error
            print(f"search raised {type(error).__name__}: {error}")
            return
        print(f"Count of offers: {len(found.offers)}; Shortlist: {len(found.shortlist)}")
        print(f"Offers that send {p.name}: {sum(failed in t.sides[0].player_ids for t in found.offers)}")
        print(f"Offers that send {wname} (the stand-in for Walker): "
              f"{sum(walker in t.sides[0].player_ids for t in found.offers)}")
        print("The first 20 offers, asker side (sends) then partner side (gets):")
        for trade in found.offers[:20]:
            print(f"  {offer_id(trade)}  sends [{sends(snap, trade)}]  gets [{gets(snap, trade)}]")

    elif args.section == "at5":
        empty = search(asker, None, snap, FakeJev(), trade_block=[])
        plain = search(asker, None, snap, FakeJev())
        e_ids, p_ids = [offer_id(t) for t in empty.offers], [offer_id(t) for t in plain.offers]
        print(f"Run 1, trade_block=[]: {len(e_ids)} offers, Shortlist {len(empty.shortlist)}")
        print(f"Run 2, no block:       {len(p_ids)} offers, Shortlist {len(plain.shortlist)}")
        print(f"Same offers in the same order: {e_ids == p_ids}")
        print(f"Same Shortlist in the same order: "
              f"{[o.offer_id for o in empty.shortlist] == [o.offer_id for o in plain.shortlist]}")
        print("First 10 offers of each run:")
        for a, b in zip(e_ids[:10], p_ids[:10], strict=True):
            print(f"  {a}  |  {b}")
        print("Shortlist of each run:")
        for a, b in zip(empty.shortlist, plain.shortlist, strict=True):
            print(f"  {a.offer_id}  |  {b.offer_id}")

    elif args.section == "at7":
        plain = finder_cache_key(2026, asker, None, snap)
        print(f"Key, no block:              {plain}")
        print(f"Key, trade_block=[]:        {finder_cache_key(2026, asker, None, snap, trade_block=[])}")
        with_walker = finder_cache_key(2026, asker, None, snap, trade_block=[walker])
        print(f"Key, [{wname}]:  {with_walker}")
        one = finder_cache_key(2026, asker, None, snap, trade_block=[walker, flowers])
        two = finder_cache_key(2026, asker, None, snap, trade_block=[flowers, walker])
        print(f"Key, [{wname}, Flowers]:  {one}")
        print(f"Key, [Flowers, {wname}]:  {two}")
        print(f"{wname} key differs from no-block key: {with_walker != plain}")
        print(f"Two orders give one key: {one == two}")

    elif args.section == "at9":
        found = search(asker, None, snap, FakeJev(answer=scattered_fair), trade_block=block)
        system, user = build_pick_prompt(found, snap, offer_sheets(found, snap, NewsFeed(fetch=no_news)), None)
        print("The first lines of the user message of the pick:")
        for line in user.splitlines()[:3]:
            print(f"  {line}")
        print("The block line: " + next(line for line in user.splitlines() if line.startswith("The Trade block")))
        flat = " ".join(system.split())
        rule = "When the list holds a fair offer for a block player, at least one pick sends him."
        print(f"The prompt holds the rule {rule!r}: {rule in flat}")
        start = flat.index("The user message may name a Trade block")
        print(f"The rule text of the prompt: {flat[start:flat.index('Keep the spread', start) + 50]}")


if __name__ == "__main__":
    main()
