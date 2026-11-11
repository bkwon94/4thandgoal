# 03 notes: the live cost of the Jev questions, the limits, and one Claude answer

Ticket: `decisions/03-research-jev-live-cost.md`. Written 2026-11-09. No TypeSafe call and no Claude call ran.
These notes give numbers and sources. Brian sets the caps in ticket 04.

## Sources

- TypeSafe models page, with price, context, and rate limits: https://docs.typesafe.ai/go/models.md, fetched 2026-11-09. The URL https://typesafe.ai/pricing redirects to it (HTTP 308 to `https://docs.typesafe.ai/models`).
- TypeSafe request rules and errors: https://docs.typesafe.ai/api/errors.md.
- TypeSafe parallel questions cookbook, with a timed run: https://docs.typesafe.ai/cookbooks/parallel_questions.md.
- Anthropic pricing: https://docs.claude.com/en/docs/about-claude/pricing.md, fetched 2026-11-09.
- Copies of all four pages: `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/372f785e-ac82-4c3f-913e-f68aef8f1946/scratchpad/docs/`.
- Repo, `main` at `47b1dc6d`: `packages/league/python/src/league/jev.py`, `packages/facts/python/src/facts/jev_check.py`, `packages/facts/python/src/facts/writer.py`, `apps/pipeline/src/cornerstone/pipeline.py:395-400`, `docs/adr/0029-typesafe-jev-is-the-second-model-vendor.md`.
- Prior research with live Jev timings: `.scratch/jev/decisions/01-research-jev-on-past-labels.notes.md` and `.scratch/jev/decisions/09-research-finder-fact-rank.notes.md` on `main`. Also `.scratch/manager-brain/decisions/03-research-search-cost.notes.md` in the `manager-brain` worktree.
- Real fact sheets: `clients/cpc/data/2026/week-08/facts.json` and `clients/norcal/data/2026/week-08/facts.json` in the main checkout.

Token counts are characters / 4 on compact JSON, the same method as the manager-brain notes. Treat them as estimates within about 20%.

## Answers in short

1. A Jev route costs about $0.00004 and takes about 0.1 s. The "facts can answer" Noul over the full week sheet costs about $0.0008 and takes about 0.25 to 0.4 s.
2. TypeSafe sets the rate limits per organization, in tokens per second and requests per second. The docs give no number. Brian must read them at https://console.typesafe.ai/rate-limits.
3. One short Claude answer on Opus 5.5 costs about $0.04 to $0.10, by the size of the facts it gets. The Jev check adds about $0.0002 to $0.0008. No repo run measured the time of a short Claude answer.
4. For 2 leagues of 12 managers, a month costs about $1 to $2 at low use, $4 to $11 at middle use, and $25 to $66 at high use. Claude is over 95% of each total.

## The facts each number depends on

### Jev price, context, and model

- Jev 1.14 (`jev-1.14.0`) costs $0.042 per million input tokens. "Output tokens are free." Source: https://docs.typesafe.ai/go/models.md, table "Current models" and the "Price" note. The earlier note's $0.042 is correct.
- A request fits 64k tokens. The state plus one question fits 32k tokens. Source: the same page, "Context length".
- No limit applies to the count of questions in a request. Source: the same page.
- The body of a request is at most 32 MiB. Source: https://docs.typesafe.ai/api/errors.md, "Request rules".
- The repo sends `model="jev-latest"`, which points to `jev-1.14.0` today (`packages/league/python/src/league/jev.py:9`; https://docs.typesafe.ai/go/models.md, "Aliases").

### Jev latency, measured before

| Request | Input tokens | Time | Source |
|---|---|---|---|
| One blurb check, `single_all_vocab` | about 4,900 | p50 0.088 s, p95 0.136 s | `.scratch/jev/decisions/01-research-jev-on-past-labels.notes.md`, "Cost and latency" |
| One article, 13 questions | about 11,800 | 0.24 s | https://docs.typesafe.ai/cookbooks/parallel_questions.md, the printed result |
| One request of 289 to 333 Score questions | 42,361 to 49,099 | 0.31 to 0.51 s, median 0.39 s | `.scratch/jev/decisions/09-research-finder-fact-rank.notes.md`, "Latency" |

All times are client wall time from Brian's laptop. A call from the Fly API adds its own network time. No run measured that.

### The real size of a week fact sheet

| League, week 8 of 2026 | Facts | Chapters | Compact JSON of `{id: text}` | Tokens, about |
|---|---|---|---|---|
| cpc | 622 | 13 | 70,787 characters | 17,700 |
| norcal | 622 | 12 | 67,959 characters | 17,000 |

Source: `clients/<slug>/data/2026/week-08/facts.json`, key `sheet.facts`. The full sheet fits the per-question limit of 32k, with about 14k tokens to spare.

The facts that name one team are 4,797 to 7,902 characters in cpc, median 5,956. That is about 1,500 tokens. Method: each fact whose text holds the team name, for each of the 12 team names of the matchup chapters. This slice misses player facts that do not name the team, so it is a lower bound.

The largest chapters are "Power rankings" (80 facts, 9,459 characters) and "Matchup of the Week" (95 facts, 9,336 characters).

The vocabulary prompt is 6,126 characters, about 1,500 tokens. The tone prompt is 6,097 characters, about 1,500 tokens (`packages/facts/python/src/facts/prompts/`).

## 1. The cost and the latency of the two Jev calls

### The route call

The state is the question of the manager. The questions are one Choice over the Topics, plus one companion Noul "Does any Topic fit?". The TypeSafe skill says that a companion Noul usually works better than a "none of the above" option on Jev 1.14.

| Part | Tokens, about |
|---|---|
| The question of the manager | 30 |
| 15 Topics, each with a name and a one-line description in the criteria | 15 × 40 = 600 |
| The Choice text and the companion Noul | 150 |
| The team of the asker and the week, as state | 50 |
| Total | about 850, so use 1,000 |

- Cost: 1,000 × $0.042 / 1,000,000 = **$0.000042** per question.
- Latency: the state is a quarter the size of a blurb check. Expect **under 0.1 s** from the laptop, on the 0.088 s p50 of a 4,900-token request. This is a projection, not a run.

### The "facts can answer" call

The state is the full week fact sheet plus the question. The question is one Noul.

- Tokens: about 17,700 + 100 = **about 17,800** for cpc.
- Cost: 17,800 × $0.042 / 1,000,000 = **$0.00075** per question.
- Latency: between the 11,800-token run (0.24 s) and the 42,000-token runs (0.31 s). Expect **about 0.25 to 0.4 s**. This is a projection, not a run.
- The call runs only when no Topic fits.

A choice for the spec: the skill says to "ask speculatively". One request could hold the route Choice, the companion Noul, and the "facts can answer" Noul, with the sheet in the state. That saves one round trip of about 0.1 s. It costs the sheet on every question, about $0.0008 instead of $0.00004. The skill also warns that a state field for one question can sway the answer to another. So the 17,000 tokens of facts can pull the route. Decision ticket 09 can test both forms.

## 2. The TypeSafe rate limits and quotas

What the docs say:

- "Rate limits are set per organization." The org reads its limits at https://console.typesafe.ai/rate-limits. Source: https://docs.typesafe.ai/go/models.md, "Rate limits".
- "Limits are measured in tokens per second and requests per second." A request over either limit gets `429 Too Many Requests`. Source: the same page.
- The SDKs retry a `429` and a `529 Overloaded` with backoff by default, and follow `retry-after`. Source: the same page and https://docs.typesafe.ai/api/errors.md, "Handling rate limits". The repo keeps the default retry (`packages/league/python/src/league/jev.py:16`).
- "Higher limits are available on custom and enterprise plans." The request form is https://support.typesafe.ai/forms/rate-limit-increase-request. Source: https://docs.typesafe.ai/go/models.md.
- The default Python client opens at most 100 connections. Source: https://docs.typesafe.ai/sdk/python/usage/advanced.md, line 102, as the manager-brain notes cite it.

What the docs do not say:

- No number for requests per second or tokens per second.
- No limit for concurrency apart from the client pool.
- No list of plan tiers with prices, no monthly quota, and no free tier.

The load of the ask box is small. A burst of 24 managers in the same second, each with a "facts can answer" call, is 24 requests and about 430,000 tokens. That is the worst case to check against the console numbers. A normal minute has 0 to 2 questions.

## 3. One short Claude answer plus one Jev check

### The model and the call shape in this repo

- The Writer model is `claude-opus-5-5` (`packages/facts/python/src/facts/writer.py:19`). Every Claude call goes through `ClaudeWriter.parse`, with `max_tokens=16000` and an `effort` of `"high"` by default (`writer.py:73-99`).
- The analyzer uses `effort="medium"`, "because it answers a waiting browser", with a cache TTL of `1h` (`writer.py:51-57`). An ask box also has a waiting reader, so the same choice fits.
- Opus 5.5 costs $4 per MTok of input and $20 per MTok of output. A 5-minute cache write costs $5, a 1-hour cache write costs $8, and a cache hit costs $0.20. Source: https://docs.claude.com/en/docs/about-claude/pricing.md, "Model pricing".

### The tokens of one answer

| Part | Full sheet | Team slice |
|---|---|---|
| System: the vocabulary, the tone, and a short answer rule | about 3,500 | about 3,500 |
| Facts | about 17,700 | about 1,500 to 2,000 |
| The question and the team of the asker | about 100 | about 100 |
| Input total | about 21,300 | about 5,500 |
| Output, an assumption: 2 to 4 sentences of JSON with fact IDs, plus the effort overhead | about 1,000 | about 1,000 |

The output number is an assumption. The repo logs the input and cache tokens of each Claude call, but not the output tokens (`writer.py:101-110`). So no saved run gives the output of a short call.

### The cost of one answer

| Case | Input cost | Output cost | Total |
|---|---|---|---|
| Full sheet, no cache | 21,300 × $4 / M = $0.085 | 1,000 × $20 / M = $0.020 | **about $0.105** |
| Full sheet, cache hit on the system and the sheet | 21,200 × $0.20 / M + 100 × $4 / M = $0.0046 | $0.020 | **about $0.025** |
| Full sheet, a 1-hour cache write | 21,200 × $8 / M = $0.170 | $0.020 | about $0.19 |
| Team slice, no cache | 5,500 × $4 / M = $0.022 | $0.020 | **about $0.042** |

The cache needs care. A 1-hour write costs twice the base price, and it pays back only after two hits (pricing page, "Prompt caching"). A league with one question an hour pays a write on most questions, which costs more than no cache. Only the high-use case gets enough hits in an hour. The spec must pick the TTL with the use rate in mind.

### The Jev check of the answer

The check reuses `jev_check.py`: one Noul per sentence, with the facts, the vocabulary, and the answer in the state.

- With the cited facts or the team slice: about 3,500 to 5,300 tokens, so **about $0.0002**. The week 8 build gives `Jev: 14 checks, 0 errors, 74573 input tokens`, which is 5,327 tokens per check (log line from `apps/pipeline/src/cornerstone/pipeline.py:400`).
- With the full sheet: about 19,500 tokens, so **about $0.0008**.
- Latency: about 0.09 s for 5,000 tokens and about 0.3 s for 19,500 tokens, from the timings above.

### The latency of one answer

No repo run measured a short Claude answer. The nearest number is `write_reasons`, one Opus 5.5 call at `effort="medium"` for 8 to 10 trade sentences. It took **21.3 s to 26.6 s** (`.scratch/jev/decisions/09-research-finder-fact-rank.notes.md`, "Latency"). A 2 to 4 sentence answer writes fewer tokens, so it is faster, but by how much is not known.

Two ways to make it faster exist. Each changes the cost.

- Fast mode on Opus 5.5 costs $8 per MTok of input and $40 of output, twice the base (pricing page, "Fast mode").
- Sonnet 5.5 costs $2 and $10. Haiku 5.5 costs $0.10 and $0.50 up to 100,000 tokens (pricing page, "Model pricing"). The repo uses neither, so the voice of their answers is not tested.

Decision ticket 09, the prototype of the Jev route, is the natural place to time one real short answer.

## 4. A monthly cost for 2 leagues of 12 managers

### Assumptions

- 24 managers, and 4.3 weeks a month during the season.
- Low: 1 question per manager per week. Middle: 5. High: 20.
- The share of questions with no Topic, which then get the "facts can answer" call: 35% at low and middle, 45% at high. The miss share is higher at high use, because a keen manager asks odder questions.
- The share that gets a Claude answer: 20% at low and middle, 30% at high.
- Each Claude answer gets one Jev check.
- The cache gives no saving at low and middle use. See section 3.
- These shares are guesses. The log of misses gives the real ones after the first weeks.
- The caps of ticket 04 are not applied. A cap lowers the high case.
- The weekly build of the Answers for each team is a separate cost and is not here.

### Counts per month

| Use | Questions | "Facts can answer" calls | Claude answers |
|---|---|---|---|
| Low | 103 | 36 | 21 |
| Middle | 516 | 181 | 103 |
| High | 2,064 | 929 | 619 |

### Cost per month, full sheet to Claude

| Use | Jev route | Jev "facts can answer" | Jev check | Claude | Total |
|---|---|---|---|---|---|
| Low | $0.004 | $0.03 | $0.02 | $2.21 | **about $2.25** |
| Middle | $0.02 | $0.14 | $0.08 | $10.82 | **about $11.05** |
| High | $0.09 | $0.70 | $0.50 | $65.00 | **about $66.30** |

Jev at $0.0008 for the check. Claude at $0.105 per answer. With a warm cache at high use, Claude falls to about $0.025 per answer plus about one write per active hour. Then the high case is about $20 to $30.

### Cost per month, team slice to Claude

| Use | Jev, all three calls | Claude | Total |
|---|---|---|---|
| Low | $0.04 | $0.88 | **about $0.92** |
| Middle | $0.18 | $4.33 | **about $4.50** |
| High | $0.91 | $26.00 | **about $26.90** |

Jev at $0.0002 for the check. Claude at $0.042 per answer.

### What the numbers mean for the caps

- Jev is under $1 a month at every level. A cap on Jev alone is not needed for cost. Only the rate limit can bound it.
- Claude sets the cost. A cap of 300 Claude answers a month for one league holds that league to about $32 with the full sheet, or about $13 with the team slice.
- The team slice cuts the Claude cost by about 60%. It may also miss a fact that the answer needs, such as a league leader. The "facts can answer" Noul should see the same facts that Claude gets, so the two calls agree.

## Open for Brian

1. Read the requests per second and the tokens per second of the TypeSafe org at https://console.typesafe.ai/rate-limits. Check that a burst of 24 requests and 430,000 tokens fits. The docs give no number.
2. Ask TypeSafe whether the account has a plan tier, a monthly quota, or a spend limit. The docs name only "custom and enterprise plans".
3. Decide whether Claude gets the full sheet or the team slice. The cost differs by about 60%.
4. Decide whether a 25 s answer is acceptable in the Thread. If not, ticket 09 must time a short call and may test fast mode or Sonnet 5.5.
5. Note that the ask box sends the questions of managers to TypeSafe and to Anthropic. ADR 0029 covers fact sheets and blurbs, not free text from managers. A question can hold a name, so the ADR may need a line.

## Rate limits from Brian

Brian read https://console.typesafe.ai/rate-limits on 2026-11-09. The limits of the organization are 80 requests per second and 100,000 tokens per second. A "facts can answer" call of about 17,700 tokens lets about 5 such calls run each second. A route call of about 1,000 tokens hits the request limit first, at 80 each second. Both are far above the use of 24 managers.
