# cornerstone.sheet

## Knows

- It builds the facts of each fact group into the fact sheet of one week, and puts the facts into each chapter.
- It builds the bundle that each chapter reads, and it writes and reads the bundle file.
- The entry: outside this folder, a module imports only `cornerstone.sheet` or `cornerstone.sheet.base`.
- The terms are in `GLOSSARY.md`.

## Ports

- `sheet/assemble.py` calls `provider.sleeper.fetch_news` by default, so the sheet reaches the Sleeper news feed.

## Does not do

- It writes no prose and makes no Claude call. `facts/writer.py` writes each blurb.
- It checks no blurb. `facts/verifier.py` does.
- It holds no odds engine. `cornerstone/odds.py` holds it, and `sheet/base.py` calls it once per build.
- It writes no page. `cornerstone/render.py` writes `page.json`.
- It builds no fact sheet of a proposed trade. `cornerstone/trade_facts.py` does.
