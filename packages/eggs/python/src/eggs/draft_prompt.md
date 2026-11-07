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

Answer with one JSON list and nothing else. Each item has these keys:

- "page": the path of the page, such as "/midseason/2026/".
- "target": the stable id of the element.
- "action": the action name, such as "tap3".
- "conditions": an object of condition names and values, or {{}}.
- "reason": the reason of the spot.
