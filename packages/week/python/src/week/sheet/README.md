# week.sheet

## Knows

- It builds the facts of each fact group into the fact sheet of one week, and puts the facts into each chapter.
- It builds the bundle that each chapter reads, and it writes and reads the bundle file.
- The entry: outside this folder, a module imports only `week.sheet` or `week.sheet.base`.
- A league with no median game gets no MED facts, no median part in the impact fact, and no Median Game chapter.
- The terms are in `GLOSSARY.md`.

## Ports

- `sheet/port.py` is the chapter port. A source of another package gives its facts, its chapter, and the odds.
- `sheet/assemble.py` calls `provider.sleeper.fetch_news` by default, so the sheet reaches the Sleeper news feed.

## Does not do

- It writes no prose and makes no Claude call. `facts/writer.py` writes each blurb.
- It checks no blurb. `facts/verifier.py` does.
- It holds no odds engine and no rankings chapter. The rankings source gives both through the chapter port.
- It writes no page. `week/page.py` writes `page.json`.
- It builds no fact sheet of a proposed trade. `cornerstone/trade_facts.py` does.
