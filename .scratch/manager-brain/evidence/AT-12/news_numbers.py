"""
Print the NEWS facts of Jonathan Taylor (6813) from the real Sleeper news feed, with their numbers.
It uses the real NewsFeed and news_facts of the analyzer on the live week 9 roster data of cpc.
"""
import argparse
from pathlib import Path

from analyzer.trade_news import NewsFeed, news_facts
from cornerstone.cli import VALUE_MODELS, _saved_snapshot, find_root
from league.client import load_client
from league.paths import nfl_dir, provider_cache_dir
from league.provider.sleeper import SleeperProvider

root = find_root(Path.cwd())
client = load_client(root, "cpc", 2026, SleeperProvider(provider_cache_dir(nfl_dir(root))).fetch_settings, VALUE_MODELS)
snapshot = _saved_snapshot(argparse.Namespace(season=2026, week=8, chart=None), client)
feed = NewsFeed()
print(f"now: {feed.now().isoformat()}")
for fid, f in news_facts(["6813"], snapshot, feed).items():
    print(f"{fid}: {f.text}\n  numbers={f.numbers}")
