# Easter eggs: a hunt for letters across the CPC site, six eggs each Tuesday

Status: ready-for-agent
Date: 2026-11-06
Apps: both. The site holds the listener, the find and claim flow, the egg board, the egg banner, and the egg button. The API holds the eggs, the claims, the egg check, and the letter rule. The pipeline drafts and drops the eggs of each week with the Tuesday publish.
Spec branch: `easter-eggs`.
Source: the map `.scratch/easter-eggs/MAP.md` and decision tickets 01 to 10. The canvas of ticket 08 is https://claude.ai/artifact/2pe6Z3X2vAiTVAfEwbHSJF. ADRs 0022, 0023, and 0024.
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

The CPC league reads the site each week, but most managers read only the newest week page and leave. The old week pages, the midseason report, the sim, and the analyzer hold a lot of work that few managers open twice. The commissioner wants a reason for each manager to come back each week and to read every page with care. The league also wants some fun between the games, with a real prize.

## Solution

A CPC-only `eggs` package hides very hard eggs across the site. Each Tuesday from week 9 to week 17, an egg drop of six eggs goes live with the weekly publish, 54 eggs in all. Each egg holds one letter. A manager finds an egg by a tap, a long press, or another action on one exact spot, sometimes under a condition such as light mode. The egg cracks open and shows its letter.

The first manager to claim the egg puts its letter toward one egg word: CORNERSTONE, LANSDALE, or EAGLES. The first manager to fill an egg word wins its gift card: $50, $30, or $20. The egg board shows the race of each egg word, the count of eggs left, and the latest claims. It never shows where an egg hides. The site gives no hints.

The commissioner places every egg, so the commissioner cannot hunt. An agent proposes six spots each Tuesday, and the commissioner confirms each one before it can drop.

## User Stories

### Find an egg

1. As a manager, I want to tap an exact spot on a page to find an egg, so that the hunt rewards a close read of the site.
2. As a manager, I want an egg kind to use 2 to 5 fast taps, a long press, a long hold, a tap combo, or a selected word, so that each egg is a new puzzle.
3. As a manager, I want some eggs to need a condition, such as light mode, an open "Show all", or an old week, so that the hard eggs stay hard.
4. As a manager, I want eggs on the sim, so that a replay where one roster wins the title can hide a letter.
5. As a manager, I want eggs on the analyzer, so that a grade of one exact trade can hide a letter.
6. As a manager, I want an egg that works only in a clock window, after a scroll to the end of a page, or on the 404 page, so that the catalog has many kinds.
7. As a manager, I want a normal tap to do what it always does, so that the hunt never breaks a link, a toggle, or a chip.
8. As a manager on an iPhone, I want a long press on a target to show no callout, so that the long-press eggs work on a phone.
9. As a manager, I want a multi-tap on a sim row to count across the frames of the replay, so that a moving target can still hold an egg.
10. As a manager, I want the page to blur and a red ring to ripple from the spot when I find an egg, so that the find feels big.
11. As a manager, I want a black egg with the grid and the CPC house that bobs and wobbles, so that I know a tap opens it.
12. As a manager, I want a tap to crack the egg and a big red letter tile to spring up, so that the letter is the reward of the find.
13. As a manager, I want to see "another manager claimed first" if the egg is gone, so that I know the spot was right but too late.
14. As a manager, I want to see "The eggs need a rest. Try again in N minutes." at the limit of the egg check, so that a real spot never looks empty.

### Claim an egg

15. As a manager, I want "Claim N" to open a sheet, so that I claim the letter at once after the find.
16. As a manager, I want to pick my team from pills, so that the claim needs no login.
17. As the commissioner, I want my team left out of the pills, so that I cannot hunt the eggs I placed.
18. As a manager, I want a card for each egg word with its gift card value, my count, my tiles, and its leader, so that I choose the egg word with care.
19. As a manager, I want a ghost tile to pulse where the letter lands, so that I see what the claim does before I confirm it.
20. As a manager, I want an egg word with no open slot for the letter to be faded and disabled, so that I cannot waste a claim.
21. As a manager, I want a dashed notice that offers a block when the letter fits none of my egg words, so that I can still take the egg from the other managers.
22. As a manager, I want the passphrase field to show only if my browser has no passphrase, so that I type it once per browser at most.
23. As a manager, I want the claim button to name what is still missing, so that I know the next step.
24. As a manager, I want a hero card after the claim where the count rises and the red tile drops into its slot, so that the claim feels final.
25. As a manager, I want the hero card to say the gift card is mine when I fill an egg word, so that I know I won.
26. As a manager, I want a hero card for a block, so that I know the egg is gone and the letter counts for no egg word.
27. As a manager, I want the first claim to win when two managers claim one egg at once, so that a tie has one clear answer.

### Follow the hunt

28. As a manager, I want an egg button with a red badge in the top band of every page, so that I see the count of eggs left from anywhere.
29. As a manager, I want the egg button to open the egg board, so that the race is one tap away.
30. As a manager, I want the egg banner under the top band of the home page after each egg drop, so that I know new eggs are out.
31. As a manager, I want the egg banner to read "6 new eggs · 7 left" and link to the egg board, so that I get the two counts and the way in.
32. As a manager, I want to hide the egg banner, so that it does not take space after I read it.
33. As a manager, I want the hero of the egg board to show the counts left to find, found, and to drop, so that I see the size of the hunt.
34. As a manager, I want a grid of all 54 eggs, one column per week from 9 to 17, so that I see which drops still hold eggs.
35. As a manager, I want a found egg white, an egg still out to glow red, and a future egg dashed, so that I read the grid at a glance.
36. As a manager, I want one card per egg word with its gift card value, its leader, and the top 5 managers with their tiles, so that I see who is close.
37. As a manager, I want "Show all 11" on each egg word card, so that I can see every manager in the race.
38. As a manager, I want a won egg word to turn into a hero card with a WON stamp, so that the win is clear to the league.
39. As a manager, I want a "Latest claims" feed with the manager, the letter, and the egg word, so that I see the hunt move.
40. As a manager, I want the feed to never name the page or the spot, so that a claim gives no hint.
41. As a manager, I want a short "How the hunt works" card at the end of the egg board, so that the rules are on the site.
42. As a manager, I want the egg board to show no block, so that a block reads as a letter that went nowhere.
43. As a manager, I want the found count to still count each block, so that the counts add up.

### Place and drop the eggs

44. As the commissioner, I want `make egg-draft CLIENT=cpc WEEK=N` to propose six spots, each with a reason, so that I start each Tuesday from a draft.
45. As the commissioner, I want the draft to read the catalog, the survey notes, the new week page, and the eggs that dropped before, so that no spot repeats.
46. As the commissioner, I want to keep, change, or reject each spot in `~/cpc-eggs/2026.toml`, so that no egg drops without my confirmation.
47. As the commissioner, I want `make publish CLIENT=cpc WEEK=N` to send the confirmed eggs to the API as its last step, so that the eggs go live with the week.
48. As the commissioner, I want the publish to warn when the API is down, and `make egg-drop CLIENT=cpc WEEK=N` to retry, so that a failed drop is easy to fix.
49. As the commissioner, I want the publish to say so when a week has no confirmed eggs, so that I see that it dropped none.
50. As the commissioner, I want the API to give each egg its letter at the drop, so that the letters follow one public rule.
51. As a manager, I want each letter of a drop to be one that the most managers still need, so that the race stays open.
52. As a manager, I want no egg to hold the last letter that the leader of an egg word needs, so that one drop cannot end a race.
53. As the commissioner, I want to undo a claim, so that I can fix a claim for the wrong team.
54. As the commissioner, I want the spots to live only in my file and in the API, so that the public repo and the bundle never name a spot.
55. As the commissioner, I want an AI that reads the whole source to learn only that multi-taps go to the API, so that nobody can read the answers.

### Stay CPC only

56. As the commissioner of NorCal, I want no eggs on the NorCal site, so that the hunt stays a CPC game.
57. As a manager, I want the claim to need the passphrase of the league, so that an outsider can find a spot but cannot claim it.

## Implementation Decisions

### The package

- A new package `eggs` holds the domain in both languages (ADR 0023). Its Python holds the store, the egg check, the claim, the letter rule, the drop, the undo, and the board. Its site part holds the listener, the find and claim flow, the egg board, the egg banner, and the egg button.
- Only `clients/cpc/client.toml` adds `eggs` to its package list (ADR 0022). A client without the package gets no listener, no egg button, no egg banner, and no egg board route.
- The package values of `eggs` hold the egg words, the gift card value of each, the weeks of the hunt, the count of each egg drop, and the roster of the commissioner. The roster of the commissioner is a roster id, not a name.
- The API app imports the routes of the package as it imports the routes of `analyzer`. The site app takes the parts of the package through the shell, as other packages do.

### The store

- One SQLite file per client on the Fly volume at `/data`, beside the files of the analyzer.
- Two tables, decided in ticket 01:

```text
eggs:   id, week, page, target, action, conditions, letter, dropped_at
claims: egg_id UNIQUE, roster_id, word | NULL (a block), claimed_at, browser, undone_at | NULL
```

- Each other number derives from the two tables: the counts, the letters of each manager, the leader, and the winner. The unique `egg_id` of `claims` settles a tie: the first write wins. An undo sets `undone_at`, so the egg goes live again and the log keeps the claim.

### The routes

Each route sits under the slug of the client. The egg check and the egg board are open. The claim needs the passphrase. The drop and the undo need the commissioner key.

- `POST /{slug}/eggs/check`: the body holds the page, the element id, the action, the trail of a tap combo, and the state of the conditions. The answer is no match, a match with the letter and a one-time claim token, or a match on an egg that another manager claimed. The token is good for 15 minutes and for one claim.
- `POST /{slug}/eggs/claim`: the body holds the token, the roster id, and the egg word or a block. The API refuses the roster of the commissioner, a word with no open slot for the letter, a block when the letter fits an egg word, and an egg word that has a winner. The answer holds the new state of the manager in each egg word, and the winner if the claim fills a word.
- `GET /{slug}/eggs/board`: the counts left to find, found, and to drop, the state of each of the 54 slots by week, each manager in each egg word, the winner of each egg word, and the latest claims. It holds no page and no spot. The egg banner and the badge of the egg button read the same route.
- `POST /{slug}/eggs/drop`: the body holds the week and its confirmed eggs. The API gives each egg its letter and makes the eggs live. A second drop of one week replaces nothing and answers with the eggs that already dropped.
- `POST /{slug}/eggs/undo`: the body holds an egg id.

### The keys and the limits

- The egg check and the egg board sit outside the passphrase guard. The egg check has its own limit of 60 per hour for each address, apart from the limit of 10 per minute of the other routes (ticket 10). The egg board takes the limit of the other routes.
- The claim needs the passphrase of the client, through the guard that the analyzer already uses. The claim form keeps the passphrase in the same browser key as the analyzer.
- The drop and the undo need a commissioner key, a Fly secret apart from the passphrase. This changes ticket 02, which sent `eggs.toml` with the passphrase. Every manager knows the passphrase, so with it alone a manager could drop a fake egg or undo a claim of another manager.

### The listener

The rules of ticket 10, with the shape of each action:

1. A multi-tap counts when each tap lands within 400 ms of the one before, on the same element. The listener sends one check when the taps stop.
2. A long press sends one check on release, with the hold rounded down to 1, 3, or 5 seconds.
3. A tap combo is tap A, tap B, then a double-tap on C. The double-tap check carries the ids of the two taps before it, within 5 seconds. So only multi-taps and long presses send a check, and a normal tap sends none.
4. A selected word sends one check when the selection settles on one whole word in a blurb.
5. The listener counts by the stable id of the element, not by the node, so a frame change of the sim does not reset the count.
6. The listener never calls `preventDefault` on a tap. It turns off the iOS callout on every class of target in the catalog, never on a link or an image. Text selection stays on.

- The stable id of an element derives from the data that it renders, such as the chapter, the roster, and the row. Every element of each class of target in the catalog gets a stable id on every page, with an egg or not. So the bundle holds thousands of candidates, and no id marks an egg.
- The state of the conditions is the theme, the open states, the sim outcome, the trade key of the analyzer result, the scroll to the end, and the 404 page. The API checks the clock window in the timezone of the client.
- The sim result and the analyzer result put their outcome and their trade key on the root of the result, so the listener can read them.

### The letter rule

- The API gives each egg its letter at the drop, by a public rule that the "How the hunt works" card states.
- A letter fits an egg word for a manager when the manager holds fewer of that letter than the egg word has. An egg word with a winner takes no more letters.
- For each egg of a drop, the API picks the letter that the most managers still need, over the open egg words. A tie goes to the earlier letter of the alphabet. No letter repeats within one egg drop, so the first egg drop holds A, C, D, E, G, and L.
- The guard: the API never picks the last letter that the leader of an egg word needs. If the guard rules out every letter, the API picks the next letter by need.
- The claim form offers a block only when the letter fits no open egg word of the manager. A block takes the egg and counts toward the found count, but the egg board shows no block.

### The drop each Tuesday

The order of ticket 09:

1. `make build CLIENT=cpc WEEK=N` builds the week, as now.
2. `make egg-draft CLIENT=cpc WEEK=N` runs an agent with a prompt of the package. It writes six proposed spots, each with a reason, to `~/cpc-eggs/2026.toml`, each marked not confirmed.
3. The commissioner keeps, changes, or rejects each spot in the file. Only a spot marked confirmed can drop.
4. `make publish CLIENT=cpc WEEK=N` publishes and pushes the week, then sends the confirmed eggs of the week to the API as its last step. A failed drop warns and does not fail the publish. `make egg-drop CLIENT=cpc WEEK=N` retries.

- The file sits outside the repo. Each egg in it holds the week, the page, the target, the action, the conditions, the reason, and the confirmed mark.
- The undo runs as `make egg-undo CLIENT=cpc EGG=<id>`.
- The publish of a client without the package skips the drop.

### The look, from ticket 08

- The claim flow, the egg banner, and the egg board use the look of the site (ADR 0024): the 24px grid, the red glow, the four corner brackets, and one scan line on each big moment. The labels are red uppercase at 10px with 0.16em spacing. The numbers use JetBrains Mono. The motion uses the rise curve and the 0.98 tap scale of the design package.
- A claimed letter tile is a white square, and the new letter is the red square, in the colors of the logo.
- Each motion respects reduced motion, as the rest of the site does.
- Copy says "manager" or "another manager", never "rival", and "the commissioner", never a name.

### The egg board: route, way in, and layout (ticket 07)

This records the choice of the `spec` ticket 07.

- The route is `/eggs/`. It is a page of the site that renders in the client, because the claims change at any time. It reads the egg board route of the API at each visit.
- The way in is the egg button in the top band, beside the theme button, on every page. Its red badge is the count of eggs left to find. The egg board is not a menu item, so the dock keeps its five items. This replaces "the egg board is in the menu" of ticket 06.
- The egg banner is a strip 52px tall, edge to edge under the top band of the home page. It shows after an egg drop, until the next drop or until the manager hides it. The hidden state of each drop stays in local storage of the browser, as a convenience of one viewer.
- The order of the egg board, from the top:
  1. The hero: the counts left to find, found, and to drop, over the grid of the 54 eggs, one column per week from 9 to 17. A found egg is white, an egg still out glows red, and a future egg is dashed.
  2. One card per egg word, CORNERSTONE first: its gift card value, its leader, the top 5 managers with their tiles, and "Show all 11". A won egg word turns into a hero card with a WON stamp and the name of its winner.
  3. "Latest claims": the manager, the letter, and the egg word of each claim, newest first, with no page and no spot. A block is not in the feed.
  4. "How the hunt works": the egg drop each Tuesday, the claim, the letter rule, the gift cards, and that the commissioner cannot hunt.
- Before the first egg drop, the egg board shows the three egg words with no letters and the count to drop.

## Testing Decisions

A good test checks what a manager or the commissioner sees, through the highest seam. It does not check the inner steps of the code. The seams below are the ones that Brian checks with this spec.

### Seam 1: the API routes of `eggs` (the main seam)

- The tests call the routes through the FastAPI test client, as `apps/api/tests/test_api.py` does. They use a real SQLite file in a temp folder.
- They cover the egg check of each action and condition, the claim, a tie of two claims, the refusal of the commissioner, a block, the winner of an egg word, the limit of 60 per hour, the passphrase on the claim, the commissioner key on the drop and the undo, the letter rule with its guard, and the egg board shape.
- The board shape is the published seam between the API and the site, so a fixture of it from these tests feeds the site tests.

### Seam 2: the site part of `eggs`

- The listener: tests fire real pointer events on a rendered page and read the checks that it sends through its send port. They cover each action, the 400 ms rule, the count by stable id across a re-render, no check for a normal tap, and no blocked link or toggle.
- The egg board, the egg banner, the egg button, and the claim flow: tests render each from the board fixture of seam 1 with Testing Library, as the tests of `packages/sim/site` and `packages/analyzer/site/form` do.

### Seam 3: the drop of the pipeline

- The tests run the drop command on a temp copy of the file and send it to the API app in process. They cover a drop of the confirmed eggs only, a week with none, a warning when the API is down, and the skip for a client without the package.

### The evidence

- A Playwright run in `apps/site/e2e/` drives the real built site against a local API with one dropped egg. It finds the egg, claims it, and sees the claim on the egg board, at a phone width and at a desktop width.
- The readability floor of ADR 0025 holds on the egg board, the claim sheet, and the egg banner.

## Out of Scope

- A hint of any kind: a page, a spot, or a riddle. Brian wants the eggs found with no help.
- Eggs for `norcal` or any other client. Only `clients/cpc/client.toml` takes the package.
- A login, a PIN, or Google sign-in. Brian trusts the league, and an account is a barrier to the fun.
- A riddle, an answer box, or any typed answer. An egg is found and tapped, never answered.
- An egg that only a live NFL game window shows. It needs a game clock in the API.
- Automatic payout of a gift card. The commissioner gives each prize by hand.
- A page of the site for the commissioner. The drop and the undo run from make targets.
- A swipe, a hover, a key code, time on a page, and a device check as actions or conditions. Ticket 01 cut them.

## Further Notes

- Three choices in this spec go past the decision tickets. Brian checks each one with the spec:
  1. The drop and the undo use a commissioner key, not the passphrase, because every manager knows the passphrase.
  2. An egg word with a winner takes no more letters.
  3. A tap combo ends with a double-tap, so a normal tap never sends a check.
- If the eggs prove too hard, the commissioner raises the count of each egg drop in the package values.
- An egg that nobody finds keeps its letter, so an egg word can stall. Brian accepts the risk.
- For a few minutes after a drop, an egg can point to a page that the site deploy has not put online yet. That does no harm.
- Fly snapshots the volume each day. A lost laptop loses only the draft of one week.
