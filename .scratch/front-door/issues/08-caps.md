# 08: The caps

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-37, AT-38, AT-39, AT-40.

**App:** both

**What to build:** Each team gets 25 Claude Answers a day, and each league gets $25 a month, as a separate cap. A kept Answer, a route, an honest miss, and the head start do not count toward the team cap. At 80% of the monthly cap, the API logs one alert. It sends no email. Past a cap, a new Claude Answer shows its calm line with the 3 closest Topics, and everything that costs nothing still works.

**Blocked by:** 05

**Status:** in-review

- [x] At 25 Answers today, Lil Fridge sees "That's 25 questions today. Ask again tomorrow." with no Claude call (AT-37).
- [x] CPC at $25.00 sees the league line, and NorCal at $0 still gets a free answer (AT-38).
- [x] The pass of $20.00 logs one alert, and a later answer logs no second alert (AT-39).
- [x] Past the team cap, the power rankings Answer still shows in full (AT-40).
- [x] No cap line names a manager.
