# 03: Where does the live feed of trades get its data?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The event shows the trades of the league as Sleeper accepts them. The site is a static export, and transaction history comes from the weekly build. The spec must choose the data path and the refresh time.

Find out if the Sleeper transactions endpoint lets a browser read it across origins, and its rate limit. Compare a browser read with a read through the API on Fly, for cost and for load. Find which fields show a trade: the teams, the players, the time, and its status. Write the findings at `decisions/03-research-trade-feed-source.notes.md`.

## Decision

Brian agreed on 2026-11-18. The findings are in `decisions/03-research-trade-feed-source.notes.md`.

1. A new route on the Fly API reads the Sleeper transactions of the current week with a query string, so the Sleeper CDN cache does not delay it. The route keeps its answer for 30 s. It checks the passphrase and does not count against the limit of 30 requests per minute per IP, because the phones at the dinner may share one IP.
2. The Trade wire lists every trade of the season, newest first by `status_updated`. The trades of week 11 go at the top with a "new" mark, so the wire is not empty while week 11 has no trade.
3. Each trade shows the teams, the players, and the FAAB. The trade parser keeps the FAAB field, which it drops now. No draft picks: CPC is a redraft league, from Brian.
4. The site polls the route every 60 s while the tab is visible. The poll stops at the Lock. After the Lock, the wire stays as the list of the trades of Deadline week.

A trade shows about 30 to 90 s after Sleeper accepts it, at no extra cost. The spec still sets the note for a failed read and the case of a pending or vetoed trade, which the sample did not hold.
