# cornerstone.sheet

## Knows

- The fact sheet of one week: each fact group, each chapter, and the facts that each chapter may cite.
- The bundle that the writer and the page read, and the bundle file.
- The entry: outside this folder, a module imports only `cornerstone.sheet` or `cornerstone.sheet.base`.
- The terms are in `GLOSSARY.md`.

## Ports

None.

## Does not do

- It writes no prose and makes no Claude call. `cornerstone/writer.py` writes each blurb.
- It checks no blurb. `cornerstone/verifier.py` does.
- It runs no playoff odds engine. `cornerstone/odds.py` runs it, and this folder turns the odds into facts.
- It renders no page. `cornerstone/render.py` writes `page.json`.
- It builds no fact sheet of a proposed trade. `cornerstone/trade_facts.py` does.
