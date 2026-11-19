"""Run the facts step and the rankings step of the weekly build of CPC 2026 week 10 from the saved raw data.
It calls the same functions as run_build, with no Claude writer: make_bundle, then _write_rankings with the odds."""
import json
import logging
import sys
from pathlib import Path

from cornerstone.pipeline import _season_history, _write_rankings, fetch_nflverse, make_bundle
from cornerstone.value_models import VALUE_MODELS
from league.client import load_client
from league.paths import nfl_dir, provider_cache_dir
from league.provider.sleeper import SleeperProvider
from league.season_inputs import SeasonInputs

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
root = Path(sys.argv[1])
season, week = 2026, 10
provider = SleeperProvider(provider_cache_dir(nfl_dir(root)))
client = load_client(root, "cpc", season, provider.fetch_settings, VALUE_MODELS)
# The facts step: the default news fetch and the nflverse fetch of the build, on the saved raw week.
bundle, _ = make_bundle(season, week, nflverse=fetch_nflverse(client.nfl_dir), client=client)
odds = {rid: {"playoff": t.playoff, "bye": t.bye, "seed": t.seed, "status": t.status}
        for rid, t in bundle.odds.teams.items()}
Path(sys.argv[2]).write_text(json.dumps({
    "odds": odds,
    "facts": {fid: f.text for fid, f in bundle.sheet.facts.items() if fid.startswith(("ODDS.", "SW."))},
}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
# The rankings step: rankings.json of the build folder, with the odds of the facts step in the rows of week 10.
out = _write_rankings(season, week, bundle.data.teams, SeasonInputs(history=_season_history(client, season, week)),
                      None, bundle.odds, client=client)
print(f"facts step: {len(odds)} teams with odds, written to {sys.argv[2]}")
print(f"rankings step: {out}")
