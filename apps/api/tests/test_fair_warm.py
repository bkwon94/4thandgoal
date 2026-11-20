"""
Tests for the fair warm-up of the API (decision 19): the worker fills the fair cache from the live snapshot of a client,
logs one line as it starts and ends, and asks again only after a roster, the chart week, or the trade list changes.
"""
import dataclasses
import logging

import test_api
from fakes import FakeJev
from test_api import _here, with_week_9_chart

from analyzer.fair_cache import FairCache
from cornerstone_api.app import create_app
from cornerstone_api.fair_warm import FairWarmer

SLUG = "cpc"
repo = test_api.repo
settings = test_api.settings
sources = test_api.sources


def _app(settings, sources, jev):
    cpc = with_week_9_chart(_here(sources, settings))
    return create_app(settings, [cpc.client], sources={SLUG: cpc}, jev=jev)


def test_the_app_of_a_test_starts_no_warm_up(settings, sources):
    app = _app(settings, sources, FakeJev())
    assert app.state.fair_warm_thread is None
    assert isinstance(app.state.fair_cache, FairCache) and len(app.state.fair_cache) == 0


def test_a_warm_up_fills_the_cache_and_logs_one_line_as_it_starts_and_ends(settings, sources, caplog):
    jev = FakeJev()
    app = _app(settings, sources, jev)
    warmer = FairWarmer(app.state.served, app.state.fair_cache, jev)
    with caplog.at_level(logging.INFO, logger="cornerstone_api.fair_warm"):
        warmer.warm(app.state.served[SLUG])
    lines = [record.getMessage() for record in caplog.records if record.name == "cornerstone_api.fair_warm"]
    assert len(lines) == 2
    assert lines[0].startswith("Fair warm-up of cpc started: chart week 9, 12 teams")
    held = len(app.state.fair_cache)
    assert held > 1000 and len(jev.requests) > 0
    assert lines[1].startswith(f"Fair warm-up of cpc ended: {held} questions, {held} asked, 0 held, about ")
    # The same rosters and chart week again: no line and no request.
    sent = len(jev.requests)
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="cornerstone_api.fair_warm"):
        warmer.warm(app.state.served[SLUG])
    assert [r for r in caplog.records if r.name == "cornerstone_api.fair_warm"] == [] and len(jev.requests) == sent


def test_a_press_snapshot_with_a_changed_roster_wakes_the_worker(settings, sources):
    jev = FakeJev()
    app = _app(settings, sources, jev)
    served = app.state.served[SLUG]
    warmer = FairWarmer(app.state.served, app.state.fair_cache, jev)
    warmer.warm(served)
    snapshot = served.sources.snapshot(served.client.values.latest_season)
    warmer.check(snapshot)
    assert not warmer.wake.is_set()
    rosters = {rid: list(roster) for rid, roster in snapshot.rosters.items()}
    first, second = sorted(rosters)[:2]
    rosters[second].append(rosters[first].pop())
    warmer.check(snapshot.model_copy(update={"rosters": rosters}))
    assert warmer.wake.is_set()


def test_a_new_trade_on_the_trade_wire_wakes_the_worker(settings, sources):
    jev = FakeJev()
    app = _app(settings, sources, jev)
    warmer = FairWarmer(app.state.served, app.state.fair_cache, jev)
    warmer.trades_seen(SLUG, ["1"])
    assert warmer.wake.is_set()
    warmer.wake.clear()
    warmer.trades_seen(SLUG, ["1"])
    assert not warmer.wake.is_set()
    warmer.trades_seen(SLUG, ["2", "1"])
    assert warmer.wake.is_set()


def test_a_warm_up_asks_no_fair_question_for_norcal_and_still_warms_cpc(settings, sources):
    jev = FakeJev()
    app = _app(settings, sources, jev)
    cpc = app.state.served[SLUG]
    norcal = dataclasses.replace(cpc, client=cpc.client.model_copy(update={"slug": "norcal"}))
    warmer = FairWarmer({SLUG: cpc, "norcal": norcal}, app.state.fair_cache, jev)
    warmer.warm(norcal)
    assert len(jev.requests) == 0 and len(app.state.fair_cache) == 0
    warmer.warm(cpc)
    assert len(jev.requests) > 0 and len(app.state.fair_cache) > 1000


def test_a_press_of_a_client_outside_the_warm_slugs_never_wakes_the_worker(settings, sources):
    jev = FakeJev()
    app = _app(settings, sources, jev)
    cpc = app.state.served[SLUG]
    snapshot = cpc.sources.snapshot(cpc.client.values.latest_season)
    norcal = snapshot.model_copy(update={"client": snapshot.client.model_copy(update={"slug": "norcal"})})
    warmer = FairWarmer(app.state.served, app.state.fair_cache, jev)
    warmer.check(norcal)
    assert not warmer.wake.is_set()


def test_a_trade_wire_answer_of_a_client_outside_the_warm_slugs_never_wakes_the_worker(settings, sources):
    jev = FakeJev()
    app = _app(settings, sources, jev)
    warmer = FairWarmer(app.state.served, app.state.fair_cache, jev)
    warmer.trades_seen("norcal", ["1"])
    assert not warmer.wake.is_set()


def test_an_api_start_after_a_warm_up_loads_the_file_and_asks_no_question_for_a_loaded_key(settings, sources, caplog):
    first_jev = FakeJev()
    first = _app(settings, sources, first_jev)
    FairWarmer(first.state.served, first.state.fair_cache, first_jev).warm(first.state.served[SLUG])
    held = len(first.state.fair_cache)
    assert held > 1000 and (settings.result_cache_dir.parent / "fair" / f"{SLUG}.json").is_file()
    # A second app on the same data folder is an API start after a deploy.
    jev = FakeJev()
    second = _app(settings, sources, jev)
    assert len(second.state.fair_cache) == held
    with caplog.at_level(logging.INFO, logger="cornerstone_api.fair_warm"):
        FairWarmer(second.state.served, second.state.fair_cache, jev).warm(second.state.served[SLUG])
    lines = [record.getMessage() for record in caplog.records if record.name == "cornerstone_api.fair_warm"]
    assert lines[0].endswith(f"12 teams, {held} answers loaded from the file")
    assert jev.requests == []
