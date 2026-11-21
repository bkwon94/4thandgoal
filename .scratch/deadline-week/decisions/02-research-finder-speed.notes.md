# 02 notes: where the Finder spends its time

Ticket: `02-research-finder-speed.md`. Map: `../MAP.md`.
Worktree: `.claude/worktrees/deadline-week`, branch `deadline-week`. Each repo source is a file of this repo, read on 2026-11-18.
The live runs called TypeSafe and the Claude API from the Mac on 2026-11-18, on the saved CPC data of week 10 (stats through week 10, the latest saved week).
A throwaway script in the session scratchpad wrapped the Jev and Claude calls. It changed no product code, and it is deleted. These notes name rosters by roster id only.

## Summary

- The Advisor pick call costs the most: 17 to 21 s for one call. The Jev steps of the search take about 2 to 3 s in all.
- In each of the 2 presses, the first pick call failed a guard on the offer id, so a second full pick call ran. Each press took about 42 to 43 s. That retry alone costs about 18 to 21 s.
- Without the retry, a press is about 22 to 26 s. So 35 s or less is reachable without a stream, if the id failure goes away.
- The pick time follows the output tokens (about 2,200 to 2,650 per call, at about 115 to 130 tokens per second). The input of about 23k tokens is a small part.
- Low effort is no cut. It wrote 249 output tokens in 3.5 s, and no pick and no near idea stood, so the press fell back to fact lines.
- One pick call per partner, in parallel, gives the first result at about 10 s. The slowest partner, with 4 offers, takes about 18 s.
- The front door route `trade-ideas` already streams step lines over its own event stream. A per-partner stream adds one part kind on the API and one handler on the site.

## 1. The chain and its calls

The route: `packages/analyzer/python/src/analyzer/routes.py:356-410`. `_find` checks the result cache, counts one grade, runs `finder_search`, then `finder_pick`, then caches the document unless it fell back.

The search: `packages/analyzer/python/src/analyzer/finder_search.py:386-499`. It runs three Jev waves in sequence, and each wave sends one request per partner at the same time.

1. The Partner filter: one request per partner, 4 questions each. With no partner, that is 11 requests (`:421-423`).
2. The targets: one request per partner that passed, one question per pool player of both sides (`:437-439`).
3. Code builds the offers from the targets (`:457`), or the wider pass builds at most 12 (`:461-471`). No call.
4. The Shortlist: one request per partner with offers, the fair and the need questions of each offer (`:478-480`). The 10 best by product stay.

The pacer: `packages/analyzer/python/src/analyzer/jev_waves.py`. The limits are 80 requests per second and 100,000 tokens per second (`:18-20`). A press sends at most 11 requests and about 27k tokens per wave, so each step is one wave. Each wave waits until 1 s after the start of the last wave (`:76-79`). So the targets and the Shortlist each wait for the rest of that second.

The pick: `packages/analyzer/python/src/analyzer/finder_pick.py:322-367`.

1. One sheet per Shortlist offer, built one after the other (`:339`). Each sheet reads the news of its players.
2. One Advisor call for all 10 offers, through `call_with_retry` (`:340-342`). A failure of the whole response retries the full call once with feedback (`packages/facts/python/src/facts/writer.py:306-330`).
3. A repair call per failed pick, all at the same time, at low effort (`:289-314`). No repair ran in these presses.
4. One Jev check request per pick and per near idea, one after the other, log only (`:353-357`).

The Advisor call: Sonnet 5.5 (`claude-sonnet-5-5`) at medium effort, route `trade_ideas` (`packages/facts/python/src/facts/writer.py:60`, `:83`, `:103`). The system prompt has a one-hour cache (`:58`). `max_tokens` is 16000 (`:216`).

## 2. The time of each step

Two presses with no partner. Roster 1 asked first, then roster 7. Roster 7 had no partner pass the filter, so its offers came from the wider pass.

| Step | Press 1 (roster 1) | Press 2 (roster 7) |
| --- | --- | --- |
| Partner filter: 11 requests, 44 questions | 0.24 s | 0.35 s |
| Targets | 0.66 s: 4 requests, 84 questions | 0 s: no partner passed |
| Offers built by code | 39 offers | 11 offers, wider pass |
| Shortlist | 0.65 s: 4 requests, 117 questions | 0.10 s: 11 requests, 33 questions |
| Search in all, with the wave waits | 2.93 s | 2.17 s |
| 10 offer sheets, one after the other | 1.04 s | 1.79 s |
| Pick call 1, failed the id guard | 21.4 s: 22.8k in, 2,641 out | 18.1 s: 23.7k in, 2,256 out |
| Pick call 2, the retry | 17.4 s: 22.8k in, 2,215 out | 20.0 s: 23.8k in, 2,649 out |
| Jev checks, log only | 0.34 s: 4 requests | 0.37 s: 5 requests |
| Press in all | 43.1 s | 42.4 s |
| Result | 1 pick, 3 near ideas | 2 picks, 3 near ideas |
| Cost | $0.143 | $0.147 |

A single Jev request took 0.06 to 0.35 s. The Jev work of a search is under 1 s. The rest of the search time is the 1 s spacing of the waves.

The step that costs the most is the Advisor pick call. One call is about 40 to 50% of a press, and the retry doubles it to about 90%.

The snapshot load took 1.8 s on the Mac. The API keeps the snapshot in memory, so a press on Fly does not pay it each time.

### Why the retry ran

Both first calls broke the guard in `response_failures`: "pick #: offer ... is not on the shortlist" (`finder_pick.py:183-185`). The log masks the numbers. One failure shows the text "offer Offer #:#-#:#", so the Advisor copied the "Offer " label of the prompt into the id. The other shows "#-#:#", an id with a part missing.

The prompt labels each offer `Offer {offer.offer_id}` (`finder_pick.py:151`), and an id is long, such as `4:7569-12:10236+8146` (`finder_search.py:350-352`).
In the per-partner test, 2 of 4 first calls failed the same guard. So 4 of the 6 first calls at medium effort failed it.

## 3. The cuts, with the time saved

Each cut keeps the judgment of its step. The estimates come from the numbers above.

| Cut | Time saved per press | Judgment kept? | Notes |
| --- | --- | --- | --- |
| Stop the id retry. Give each offer a short label, such as `A` to `J`, and map it back in code. Or strip an "Offer " prefix before the guard. | 17 to 21 s when the first call fails, which was 2 of 2 presses here | Yes. The Advisor reads the same offers. | The biggest cut. A press goes from about 42 s to about 22 to 26 s. Research 01 may touch the same guard. |
| One Advisor call per partner, in parallel | About 2 to 8 s against one call with no retry. Wall time is the slowest partner: 18 s here for 4 offers. | Mostly. Each call picks within one partner, so the cross-partner pick of the top 3 moves to code or to a short last step. | It is also the base of a stream: the first result came at 10.6 s. |
| Build the 10 offer sheets at the same time | About 1 to 1.5 s | Yes. Same facts. | The news fetch of each sheet runs one after the other now. |
| Let a small wave go without the 1 s wait. A token-bucket count of the second, not a fixed gap. | About 1 to 1.5 s | Yes. Same questions. | A press uses about 11 requests and 27k tokens of the 80 and 100k per second. |
| Run the log-only Jev checks after the Answer goes out, or as one request | About 0.3 s | Yes. They only log. | Small. |
| A smaller pick prompt | About 1 to 2 s | Yes, if no fact drops. | The input is already deduplicated (`finder_pick.py:147-154`). Output time is most of the call. |
| Lower effort for the pick | About 14 to 17 s | **No.** | Low effort gave 249 output tokens and no pick and no near idea stood. The press fell back. Do not use. |
| A faster model, such as Haiku | Not measured | Unknown | It needs the backtest of ticket 05 first. It risks the voice and the guards. |
| Prewarm the result cache per team for the week | The whole press, about 22 to 43 s, on a hit | Yes | See below. |

### The result cache

A cache already exists. `finder_cache_key` (`packages/analyzer/python/src/analyzer/cache.py:172-197`) keys a no-partner search on the content of every roster, and `_find` serves a hit with no call (`routes.py:388-391`).
In deadline week, each trade or waiver move in any roster changes the key of every team. So a hit is rare unless the cache is filled again after each move.
A prewarm of all 12 teams costs about 12 × $0.07 to $0.14, so $0.85 to $1.70 for each roster change. That is an extra cost, so it needs Brian to agree (memory: no extra cost).

## 4. Can a press end in 35 s with no stream?

Yes, if the id retry goes away. One pick call took 17 to 21 s, and the rest of the press took 4 to 5 s. So a press with no retry is about 22 to 26 s on the Mac.
The margin is about 9 to 13 s. A retry for another guard, or a repair call, can still pass 35 s. A repair runs at low effort and in parallel, so it adds about one short call.
With the sheet cut and the wave cut, a press is about 20 to 23 s.

The press on Fly can be slower than on the Mac. These runs did not time a press on Fly.

## 5. A stream of results per partner

### The API now

- The plain route `POST /find` gives one JSON document and no stream (`routes.py:356-362`).
- The front door route `POST /trade-ideas` streams (`apps/api/src/cornerstone_api/trade_topics.py:401-447`). It does not use `VercelAIAdapter`. It runs the press in a thread, puts each part on a queue, and sends each as a `data:` line of a `text/event-stream` (`stream`, `:265-297`). The parts are `data-step` for each stage line, then `data-key` and `data-answer` with the whole document.
- `VercelAIAdapter` of Pydantic AI drives only the free answer and the personal Topics (`apps/api/src/cornerstone_api/claude_stream.py:1-16`). It streams the text of one Claude run. The Finder pick is a structured output, so this adapter is not the fit.

### The site now

- The analyzer page calls `postFind` with a plain `fetch` of JSON (`packages/analyzer/site/lib/api.ts:163-165`) from `packages/analyzer/site/form/trade-finder.tsx:136`. Its timeout is 60 s (`:20`). It shows nothing until the whole document comes.
- The front door reads the trade stream with its own reader, `readParts` and `streamTrade` (`apps/site/src/app/front-door/trade-api.ts:96-135`). It is not `useChat`.
- Only the free answer uses `useChat` with `DefaultChatTransport` (`apps/site/src/app/front-door/free-answer.tsx:7-8`, `:56-64`).

### How a stream per partner would work

On the API:

1. Run the search as now. It takes about 2 to 3 s and sends its step lines.
2. Split the Shortlist by partner.
3. Start one pick call per partner at the same time, each on its own offers, with its own guards and repair.
4. As each call ends, send one new part, such as `data-partner`, with the picks and the near ideas of that partner.
5. After the last partner, rank the picks across partners. Use the Shortlist score in code, or one short Advisor call. Send `data-answer` with the whole document, and cache it.

The `stream` helper of `trade_topics.py` already fits this: the work thread calls `emit` once per partner. The plain `/find` route needs a stream route of its own for the analyzer page, or the analyzer page moves to the trade-ideas stream.

On the site:

1. Add the new part kind to the part schema of `trade-api.ts`, and a handler such as `onPartner` in `TradeEvents`.
2. Show each partner card as it comes, and order the cards when `data-answer` comes.
3. Give `trade-finder.tsx` the same stream reader, in place of `postFind`. Its 60 s timeout can then reset on each part.

Measured, per partner, 4 partners with 1 to 4 offers each:

| Partner offers | Time to its result | Output tokens |
| --- | --- | --- |
| 2 | 10.6 s | 1,167 |
| 1 | 19.9 s, with an id retry (11.2 s + 8.5 s) | 1,327 + 881 |
| 3 | 18.0 s | 2,246 |
| 4 | 36.2 s, with an id retry (18.2 s + 17.5 s) | 2,271 + 2,099 |

With the id fix, the first partner shows at about 13 s from the press start, and the last at about 21 s.
Each call still writes 900 to 2,300 output tokens at medium effort, even for one offer. So more partners do not make the slowest call faster than about 10 s.
The cost of 4 calls with no retry is about $0.12, near the $0.07 to $0.14 of one call now. A press with 10 partners costs more. The Claude API rate limit of the account was not checked for 10 calls at a time.

## 6. Answer for the spec

- Make it fast first: the id fix brings a press from about 42 s to about 22 to 26 s, under the 35 s limit. The sheet and the wave cuts take off 2 to 3 s more.
- A stream per partner is optional on top. It shows the first result at about 10 to 13 s. It changes the pick of the top 3 from one Advisor judgment to a merge across partners, so the spec must decide who ranks the cards.
- Do not lower the effort of the pick.

## 7. Spend

| Run | Claude | Jev | In all |
| --- | --- | --- | --- |
| 2 timed presses | about $0.29 | under $0.001 | $0.290 |
| Low effort test and per-partner test | about $0.23 | under $0.001 | $0.235 |
| Total | | | **$0.53** of the $1.50 budget |

The meter of `cornerstone.advisor_eval` counted the cost, at the prices of `facts/writer.py:127`.
