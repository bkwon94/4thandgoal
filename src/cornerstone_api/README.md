# cornerstone_api

## Knows

- The FastAPI app that serves the trade analyzer to the league site.
- The analyzer routes: the teams of the trade form, the analyze route for a proposed trade, and the find route.
- The refresh route that a daily cron pings.
- The passphrase check, the rate limits, the result cache, the teams cache, and the settings from the environment.
- The terms are in `GLOSSARY.md`.

## Ports

None.

## Does not do

- It holds no grade rule. `cornerstone/rubric.py` grades a proposed trade, and `cornerstone/finder.py` finds the trades.
- It holds no prompt and no Claude check. `cornerstone/analysis.py` and `cornerstone/finder_reasons.py` hold them.
- It imports nothing from the output layer of ADR 0007, so it never writes a page.
- The pipeline package `cornerstone` never imports it.
