You propose the spots of the egg drop of week {week} of the CPC egg hunt. The commissioner confirms each spot later.

Read these files, from the repo root:

1. `{catalog}`: the catalog of egg kinds. An egg kind is a target, an action, and an optional condition.
2. `{notes}`: the survey of the site, with the targets of each page.
3. `{listener}`: the action names and the condition names that the listener sends.
4. `{page}`: the built week page of week {week}.

The eggs that dropped before:

{dropped}

Rules:

1. Propose exactly {size} spots.
2. Make each egg very hard to find. Use the old week pages and the midseason page most, behind an open state.
3. Spread the spots across the catalog: mix the pages, the targets, the actions, and the conditions.
4. Never put a spot on the target of a page that holds an egg that dropped before.
5. Never put two spots of this draft on one target of one page.
6. Give each spot a reason of one or two sentences: why the spot is hard and fair.
7. Write no hint and no riddle.
8. Use only the actions "tap2", "hold", and "select". "tap2" is a double-tap. "hold" is a press of 2 seconds or more.
9. For a 404 egg, set the page to "*404" and the condition "not_found" to true. The egg matches on any missing URL.
10. For an analyzer egg, pick two different teams at random. Set "trade_teams" to their two roster ids, such as [1, 3]. Any graded trade between those two teams matches.

Answer with one JSON list and nothing else. Each item has these keys:

- "page": the path of the page, such as "/midseason/2026/".
- "target": the stable id of the element.
- "action": the action name: "tap2", "hold", or "select".
- "conditions": an object of condition names and values, or {{}}.
- "reason": the reason of the spot.
