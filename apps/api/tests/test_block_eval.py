"""
The live block eval of the free answer (H28): 20 loose questions of Bo Girds go through the real route, Claude, and the
Jev check, and the test fails below 17 hits of the expected block kind. Run it with `pytest -m live -s`.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cornerstone_api.app import create_app, load_clients
from cornerstone_api.settings import Settings

REPO = Path(__file__).resolve().parents[3]
PASSPHRASE = "block-eval"
PASS = {"X-League-Passphrase": PASSPHRASE}
ASKER = "Bo Girds"
HITS_NEEDED = 17

# Five loose phrasings per kind. A question that should get text expects no block. The words differ from the rules of
# the free answer on purpose, so a hit comes from the shape of the answer, not from the words of the ask.
CASES: list[tuple[str, str | None]] = [
    ("tell me my top players", "list"),
    ("who are my best guys", "list"),
    ("rank my roster", "list"),
    ("which of my players have scored the most", "list"),
    ("who are the highest scoring teams this season", "list"),
    ("can you compare my roster to Teehee", "table"),
    ("me vs Teehee, whose roster is better", "table"),
    ("how's my roster stack against the Bijan team", "table"),
    ("Gibbs or Bijan Robinson, who has been better", "table"),
    ("put NFC Least and The Blue Tent next to each other", "table"),
    ("tell me about Gibbs", "player"),
    ("how is Lamar Jackson doing", "player"),
    ("what's up with Zay Flowers", "player"),
    ("is Kenneth Walker III any good this year", "player"),
    ("how has Jaylen Waddle played", "player"),
    ("how many points did I score week 3", None),
    ("who won week 1", None),
    ("what's my record", None),
    ("what was the highest score of week 5", None),
    ("who did I play in week 2", None),
]


def _chunks(response) -> list[dict]:
    lines = [line.removeprefix("data: ") for line in response.text.splitlines() if line.startswith("data: ")]
    return [json.loads(line) for line in lines if line != "[DONE]"]


@pytest.mark.live
def test_the_block_eval_hits_at_least_17_of_20(tmp_path):
    clients = [client for client in load_clients(REPO) if client.slug == "cpc"]
    settings = Settings(passphrases={"cpc": PASSPHRASE}, repo=REPO, result_cache_dir=tmp_path / "results",
                        commissioner_keys={"cpc": "block-eval"}, ask_dir=tmp_path / "ask", eggs_dir=tmp_path / "eggs",
                        rate_limit_per_minute=600)
    app = create_app(settings, clients)
    api = TestClient(app)
    season = clients[0].values.latest_season
    # The latest saved week, as the site sends it.
    week = max(int(path.name.removeprefix("week-")) for path in (clients[0].folder / "data" / str(season)).glob("week-*"))
    roster_id = next(rid for rid, name in app.state.askers["cpc"].rosters().items() if name == ASKER)

    def ask(case: tuple[str, str | None]) -> tuple[str, str | None, str]:
        """The route, the block kind, and the text of one question, as the site asks it."""
        body = {"question": case[0], "roster_id": roster_id, "week": week}
        route = api.post("/clients/cpc/ask", json=body, headers=PASS).json()
        if route.get("route") != "free":
            return f"topic:{route.get('topic')}" if route.get("route") == "topic" else str(route.get("route")), None, ""
        chunks = _chunks(api.post("/clients/cpc/ask/free", json=body, headers=PASS))
        blocks = [c["data"]["kind"] for c in chunks if c["type"] == "data-block"]
        text = "".join(c["delta"] for c in chunks if c["type"] == "text-delta").strip()
        return "free", blocks[-1] if blocks else None, text

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(ask, CASES))
    lines = ["| # | Question | Expect | Route | Block | Hit | Text |", "|---|---|---|---|---|---|---|"]
    hits = 0
    for number, ((question, expect), (route, kind, text)) in enumerate(zip(CASES, results, strict=True), start=1):
        hit = kind == expect
        hits += hit
        cells = [str(number), question, expect or "text", route, kind or "-", "yes" if hit else "no", text[:90]]
        lines.append("| " + " | ".join(cell.replace("|", "\\|").replace("\n", " ") for cell in cells) + " |")
    usd = app.state.askers["cpc"].caps.month_usd(datetime.now(clients[0].tz))
    print("\n".join(lines))
    print(f"\nHits: {hits} of {len(CASES)}. Claude cost: ${usd:.2f}.")
    assert hits >= HITS_NEEDED
