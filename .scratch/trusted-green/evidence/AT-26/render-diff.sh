#!/bin/bash
# render-diff.sh: run page-json of cpc and norcal 2026 week 10 in tg-base and tg-head, then diff the render files by JSON path.
set -e
for c in cpc norcal; do
  for w in tg-base tg-head; do
    (cd $w && uv run --quiet --exact --package cornerstone cornerstone page-json --client $c --season 2026 --week 10 >/dev/null)
  done
  python3 -B -c "
import sys; sys.path.insert(0, 'tg-head/scripts'); import rebuild
from pathlib import Path
for name in rebuild.RENDER_FILES:
    week = rebuild.Week('$c', 2026, 10)
    d = rebuild.file_diff(rebuild.build_week(Path('tg-base'), week) / name, rebuild.build_week(Path('tg-head'), week) / name)
    print(f'{week} {name}: {len(d)} diffs', *d)
"
done
