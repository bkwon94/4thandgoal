"""
The drop step of the publish alone, for the evidence of easter-eggs: the last line that `cornerstone publish` prints.
Run it from apps/pipeline with uv run. It loads the client as the CLI does, then calls drop_after_publish.
"""
import sys
from pathlib import Path

from cornerstone.cli import SleeperProvider, VALUE_MODELS, find_root, load_client, nfl_dir, provider_cache_dir
from cornerstone.egg_drop import drop_after_publish

slug, season, week, egg_file = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
root = find_root(Path.cwd())
provider = SleeperProvider(provider_cache_dir(nfl_dir(root)))
client = load_client(root, slug, season, provider.fetch_settings, VALUE_MODELS)
print(drop_after_publish(client, week, egg_file))
