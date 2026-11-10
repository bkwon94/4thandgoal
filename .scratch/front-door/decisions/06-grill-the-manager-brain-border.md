# 06: Where is the border with manager-brain?

Map: `.scratch/front-door/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Decide if trade questions and trade ideas go to the Advisor of `manager-brain`, and which Topics wait for its merge. Decide also how the live Finder of `your-league` fits here. The spec needs the border, so two specs do not build the same thing.

## Decision

Brian, 2026-11-09, in a grill.

1. "Check a trade" calls `POST /analyze` and "trade ideas" calls `POST /find` of the `manager-brain` API, both as they are. The Answer shows the Lean, the Case, and the top Bullets, and links to the Trade page. Reason: one Advisor, one prompt, and one eval, so two specs never build the same judge.
2. The front-door spec adds a third Advisor route, `/sell-high`, in the `analyzer` package beside `/analyze` and `/find`. It uses Sonnet 5.5, like the Finder pick, and reuses the Playbook, the fact helpers, the verifier, and the Jev checks of the Advisor. `manager-brain` stays as it is. Reason: a player call is a judgment, so it belongs to the one judge with the Playbook. A front-door writer gives the league two voices on player value, and a new `manager-brain` ticket delays a spec that is ready.
3. The planning of front-door goes on now. `cpc:implement front-door` waits for the merge of `manager-brain` to `main`, and then the `front-door` branch merges `main` before the first ticket. If `manager-brain` is still open when the tickets are ready, only the three judgment Topics wait, each with "Blocked by: the merge of `manager-brain`".
4. The Advisor does not stream. The front-door route sends each Advisor stage as a data part on the `useChat` stream, such as "Jev picked the targets on each side", then sends the whole Answer. The front-door spec adds one optional stage callback to the Advisor. Reason: the Advisor returns one object from `messages.parse`, and a Lean must never show before the verifier passes it. A Find press takes about 20 s, so a bare spinner is too long.
5. The live Finder of `your-league` is the "trade ideas" Topic. It calls `/find` with Your team. No other Finder gets built.

Facts checked on the `manager-brain` branch at `26dbed1b`: the routes are in `packages/analyzer/python/src/analyzer/routes.py`, the Advisor calls the `anthropic` SDK in `packages/facts/python/src/facts/writer.py`, and no route serves sell high or buy low.
