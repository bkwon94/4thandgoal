# 12: How wide is a free answer?

Map: `.scratch/front-door/MAP.md`.

**Kind:** grill

**Blocked by:** 03

**Status:** done

## Question

A free answer reads only the fact sheet of this week now (decision 03). It misses past weeks, past seasons, player game logs, the waiver pool, and news from today. Decide if Claude gets tools over all our data, such as any week of the season, nflverse game logs, and the league history. Decide also if a live news source comes in. Each tool widens the answers, and each one adds cost and wait. The spec needs this, because Brian leans toward a chat. Evidence from prototype 07: in his first minutes, Brian asked "week 1 results" and "highest scoring team this season". A free answer from the week 8 sheet misses the first one.

## Decision

Brian, 2026-11-09, in a grill.

1. A free answer gets tools over this season. Claude can read any week's matchups, scores, and transactions, the standings, any roster, and the nflverse game logs. The data sits in `clients/<slug>/data/<season>/history/` and the nflverse cache of `manager-brain` decision 06. This replaces "a question with no Topic gets the full fact sheet" of decision 03. Reason: Brian asked "week 1 results" and "highest scoring team this season" in his first minutes, and this data answers both.
2. Pydantic AI runs Claude and its tools on the Python API. `VercelAIAdapter` in `pydantic_ai.ui.vercel_ai` streams the answer, and the site reads it with `useChat` of the Vercel AI SDK. A Topic Answer streams its data block as a custom data part through `ctx.emit()`. Reason: the brain stays in one language with the facts, the Jev port, the verifier, and the Advisor. A TypeScript service with AI SDK Core would split it and add a service. The spec pins the versions of Pydantic AI and of the AI SDK, because the docs give no minimum version and the adapter targets AI SDK v5 by default.
3. Jev checks each claim of a tool answer against the tool results of that answer. Claude gets at most 4 tool calls for each answer. Past the cap, it answers with what it found and says what it could not find. Reason: the tool results are the only ground truth of a season answer, and the cap holds an answer to about 10 to 20 s and under about $0.15.
4. Past seasons of the league and a live news source are out of scope. See the map.

For the API work, load the skill `building-pydantic-ai-agents` from `pydantic/skills` (plugin `ai@pydantic-skills`).
