# 04: What are the numbers of the caps?

Map: `.scratch/front-door/MAP.md`.

**Kind:** grill

**Blocked by:** 03

**Status:** done

## Question

Set the cap of Claude answers for each team each day, and the cap in dollars for the league each month. Decide what the manager sees past each cap. The spec needs the numbers for the API and for the acceptance tests.

## Decision

Brian, 2026-11-09, in a grill.

1. Each team gets 25 Claude Answers a day. A kept Answer and a Jev-only miss do not count. The head start of decision 11 does not count toward the team cap.
2. Each league gets $25 a month, as a separate cap. One league never uses the budget of the other. The head start counts toward this cap.
3. At 80% of the monthly cap, the API logs an alert and sends a notice to the commissioner.
4. At 100%, everything that costs nothing still works: the league Topics, the kept Answers, the Jev routes, and the honest misses. A new Claude Answer shows a calm line, such as "The league's question budget is used up for this month. It resets on Dec 1.", with the 3 closest Topics. The line names no manager.
5. At the team cap, the line reads "That's 25 questions today. Ask again tomorrow."
6. The model is Claude Sonnet 5.5 (`claude-sonnet-5-5`, $2 and $10 per million input and output tokens) for every Claude answer of the front door: the free answers at `low` effort and the personal Topics at `medium` effort. The Advisor of `manager-brain` sets its own model for sell high, trade ideas, and the trade check. Reason: half the cost of Opus 5.5 and a faster stream, and Brian chose it over a split with Haiku 5.5.
7. The route sets the model with a table in code: a league Topic needs none, a personal Topic and a free answer use Sonnet 5.5, a judgment Topic goes to the Advisor, and a miss needs none.

Reason for the caps: $25 a month covers the high-use estimate of one league with room, and it holds the worst month near $50 for both leagues. A hard stop with a calm line beats a surprise bill.
