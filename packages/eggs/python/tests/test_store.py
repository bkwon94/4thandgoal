"""
Tests for the store of the egg hunt on a real SQLite file in a temp folder.
The routes test the rest through the API app, so these cover only the tie of two claims at once.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo

from eggs.store import AlreadyClaimed, EggStore

NOW = datetime(2026, 11, 10, 9, 0, tzinfo=ZoneInfo("America/New_York"))
T1 = {"page": "/midseason/2026/", "target": "luck-3", "action": "tap2", "conditions": {"theme": "light"}, "letter": "C"}


def test_two_claims_of_one_egg_at_once_give_one_claim(tmp_path):
    store = EggStore(tmp_path / "cpc.sqlite")
    egg = store.drop(9, [T1], NOW)[0]

    def claim(roster_id):
        try:
            store.claim(egg.id, roster_id, "CORNERSTONE", None, NOW)
            return True
        except AlreadyClaimed:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(claim, [3, 12]))
    assert sorted(results) == [False, True]
    assert len(store.claims()) == 1


def test_the_store_reads_one_egg_and_the_claim_of_one_egg_by_its_id(tmp_path):
    store = EggStore(tmp_path / "cpc.sqlite")
    egg = store.drop(9, [T1, {**T1, "target": "luck-12", "letter": "A"}], NOW)[1]
    assert store.egg(egg.id) == egg
    assert store.egg(egg.id + 100) is None
    assert store.claim_of(egg.id) is None
    store.claim(egg.id, 3, "CORNERSTONE", None, NOW)
    assert store.claim_of(egg.id) == store.claims()[0]
    assert store.claim_of(egg.id - 1) is None
    store.undo(egg.id, NOW)
    assert store.claim_of(egg.id) is None
