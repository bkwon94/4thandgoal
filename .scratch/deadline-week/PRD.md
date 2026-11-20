# Deadline week: the Trade Wire, a better Finder, and the trade deadline on the CPC site

Status: ready-for-agent
Date: 2026-11-19
Apps: both. The site shows the Deadline banner, the Trade Wire sheet, the analyzer switch, and the Finder look. The API on Fly serves the Trade Wire route and the Finder stream. The `analyzer` and `league` packages, which the API imports, hold the Finder steps, the Spares tree, and the trade parser.
Spec branch: `deadline-week`.
Source: the map `.scratch/deadline-week/MAP.md` and decision tickets 01 to 18. ADR 0035 and ADR 0037 (ui-sdk through one wrapper). ADR 0038 (the Value screen is the one math cut of the Finder). Prototypes on the branches `deadline-week-07-proto` (`cd385837`), `deadline-week-08-proto` (`48f18de1`), and `deadline-week-17-proto` (`c403b55f`). The handoff `.handoff/deadline-week-fair-finder.md` holds Brian's rulings of 2026-11-19.
Tickets: 01 to 15, in `issues/`. Tickets 01 to 10 are built. Tickets 11 to 15 build the fair-first Finder.

## Problem Statement

The CPC managers meet for dinner on the weekend of the week 11 trade deadline. Sleeper locks trades after the Monday night games of week 11. The site treats that week like any other week, so a manager does not see how long is left, or which trades other managers made.

The trade tools are not in their best shape for the event:

1. The Finder gives few offers. With one partner it often gives one plain offer, and the Advisor rejects it about half the time (decision 01).
2. A press of the Finder takes about 42 s, and 17 to 21 s of that is a retry of a bad offer id (decision 02).
3. The Finder gives bad trade ideas. Brian saw "Kenneth Walker for Mahomes" and "Zay Flowers for Goff". No step asks what the asker gives up, so an offer can drop the lineup of the asker (decisions 06 and 09). The front door already runs the Finder for every CPC manager, whatever the `finder` flag says.
4. The Finder looks different from the analyzer, and it sits apart from the grade (decision 07).
5. A trade Topic sometimes fails on the first call, then a retry answers fast. Nothing logs the cause (decision 06).
6. A drag of the top of a sheet upward lifts the bottom edge of the sheet off the screen (decision 08).
7. The Finder is need-first, so it gives few ideas and most of them fill one slot. Brian tried it with his team, Bo Girds: "no offers for a lot. only couple offers for qb… these are ideas that should be fair! not really always perfect adds that fill a need." Bo Girds has one weak slot, QB. The Spares tree stops 7 of 11 partners at once, and the 4 left give only QB offers (handoff).

## Solution

During Deadline week, every page of the CPC site shows a slim Deadline banner under the top band. It counts down to the trade deadline. A tap anywhere on it opens the Trade Wire in a sheet. The sheet lists each trade that Sleeper accepts in week 11, newest first, about 5 to 15 s after Sleeper accepts it. At the top of the sheet, "Grade a trade" and "Find a trade" open the analyzer in that mode.

In the last 3 hours the Deadline banner turns to the accent fill and shows seconds. After the Lock it says "The trade deadline has passed. Good luck in the playoffs." One day after the Lock, the Deadline banner goes away by itself.

The analyzer hero gets a switch, "Grade a trade · Find a trade". The Finder takes the Stage look of the analyzer and the same wait, `StageLines`, fed by its real steps. Each Finder trade shows the Lean, a short Case, and folded Bullets, and a tap opens it in the analyzer, already graded.

The Finder is fair-first. It sparks ideas: it looks for every fair trade, and it shows varied ideas, not only the trades that fill a need. Code builds every trade of four shapes, 1-for-1, 2-for-1, 3-for-1, and 3-for-2, in both directions, and keeps the trades whose trade value sums sit close together. Jev then judges if each trade is fair, and if each lineup gets better. Five picks land as Ledger cards: "You get" and "You give" columns, a trade value total for each side, and one plain line for the gap. A need, or a player the other team can spare, becomes a reason in the Case, not a gate. A gain question still drops an offer that clearly makes a lineup worse. Each bad trade that Brian marks goes into a backtest set, and a change must pass it.

The `finder` flag in CPC stays off until Brian checks the Finder on the phone and says go.

## User Stories

### The Deadline banner

1. As a CPC manager, I want a slim Deadline banner under the top band of each page during Deadline week, so that I know the trade deadline is near.
2. As a manager, I want the Deadline banner to show a small "TRADE DEADLINE" label over a countdown such as "~2d 14h 05m", so that I see the time left at a glance.
3. As a manager, I want a tilde before the countdown, so that I know the time is an estimate for the end of the Monday night games.
4. As a manager, I want the countdown to tick each minute, so that it stays right while the page is open.
5. As a manager, I want the countdown to show seconds in the last 3 hours, so that I feel the time run out.
6. As a manager, I want the Deadline banner to take the accent fill and a shimmer in the last 3 hours, so that the last hours stand out.
7. As a manager who prefers reduced motion, I want no shimmer and no slide, so that the page stays still.
8. As a manager, I want the whole Deadline banner to be one tap target, so that I do not have to hit a small link.
9. As a manager, I want a "Trade Wire" label and a badge such as "2 new" on the right of the Deadline banner, so that I know new trades wait.
10. As a manager, I want the badge to hide when week 11 has no trade, so that the Deadline banner never says "0 new".
11. As a manager, I want the Deadline banner to sink a little when I press it, so that I know the tap took.
12. As a manager with a screen reader, I want the Deadline banner to read as one button, "Open the Trade Wire, 2 new trades", so that I know what it does.
13. As a manager, I want the Deadline banner to look right in light mode and in dark mode, so that it fits the theme I chose.
14. As a manager, I want even padding above and below the two lines of the Deadline banner, and one left edge for both lines, so that it looks tidy.
15. As a manager, I want the Deadline banner to read "The trade deadline has passed. Good luck in the playoffs." after the Lock, so that I know trades are closed.
16. As a manager, I want the badge to read "Final" after the Lock, so that I know the Trade Wire no longer changes.
17. As a manager, I want the Deadline banner to go away one day after the Lock, so that the site returns to normal by itself.
18. As a manager, I want no Deadline banner on the Norcal site, so that the event stays a CPC event.
19. As a manager, I want the Deadline banner never to say "Rosters are locked", so that I am not told something false. Waivers and free agents still run.
20. As a manager on a phone at 390 by 660, I want the Deadline banner to fit with no horizontal scroll, so that the page reads well.
21. As a manager on a tablet or a desktop, I want the Deadline banner to fit at 810 by 980, 1080 by 740, and 1280 by 800, so that the page reads well on each device.

### The Trade Wire

22. As a manager, I want the Trade Wire to open in a sheet from any page, so that I can check trades without a page change.
23. As a manager, I want the Trade Wire to list only the trades of week 11, newest first, so that it is about Deadline week.
24. As a manager, I want each trade to show the time, each team with its avatar, the players each team gets with their positions, and any FAAB, so that I see the whole trade.
25. As a manager, I want no draft picks in a trade, because CPC is a redraft league.
26. As a manager, I want each trade as one even block, with the same gap between its rows and one larger gap between trades, so that the list reads well.
27. As a manager, I want a new trade to show about 5 to 15 s after Sleeper accepts it, so that the Trade Wire feels live.
28. As a manager, I want a new trade to slide in at the top and the badge to change in place, so that I see what changed.
29. As a manager, I want a live dot and "Updated 4s ago" that ticks, so that I know the Trade Wire is current.
30. As a manager, I want the Trade Wire to poll at once when I come back to the tab, so that I see the newest trades without a wait.
31. As a manager, I want the Trade Wire to stop its poll when the tab hides, so that my phone does no extra work.
32. As a manager, I want "No trades yet this week." when week 11 has no trade, so that an empty list makes sense.
33. As a manager, I want "No trades this week." after the Lock when week 11 had no trade, so that the closed state makes sense.
34. As a manager, I want a short note when a read of the Trade Wire fails, with the last good list still shown, so that one bad read does not empty the sheet.
35. As a manager, I want a pending or vetoed trade to stay off the Trade Wire, so that it lists only accepted trades.
36. As a manager, I want "Grade a trade" and "Find a trade" at the top of the sheet, so that I can act on what I see.
37. As a manager, I want "Grade a trade" to open the analyzer in Grade mode, and "Find a trade" to open it in Find mode, so that one tap takes me to the right tool.
38. As a manager, I want "Find a trade" to show only when the `finder` flag is on, so that I never see a tool that is not ready.
39. As a manager, I want the two trade links to hide after the Lock, so that I am not sent to make a trade that Sleeper blocks.
40. As a manager, I want the sheet to show the eyebrow "TRADE DEADLINE ~2d 14h 05m" over the title "Trade Wire", so that the time left stays in view.
41. As a manager, I want to drag the sheet up and down without the bottom edge of the sheet lifting off the screen, so that the sheet feels solid.
42. As a manager at the dinner, I want the Trade Wire to work when many phones share one IP, so that the rate limit does not block us.
43. As a manager, I want the Trade Wire to need the league passphrase, as the analyzer does, so that only the league reads it.

### The analyzer switch and the Finder look

44. As a manager, I want a switch "Grade a trade · Find a trade" at the top of the analyzer hero, so that both tools share one page.
45. As a manager, I want the switch to run the full width of the hero in two equal halves, with a sliding pill, so that it is easy to hit.
46. As a manager, I want the switch locked during a wait, so that I do not start a second job by mistake.
47. As a manager, I want Find mode to read "Trade Ideas" with the line "Who has a trade for you?", so that I know what it does.
48. As a manager, I want the analyzer to open in Find mode from a link with the mode in it, so that "Find a trade" lands in the right place.
49. As a manager, I want the hero eyebrow to read "Trade deadline ~2d 14h 05m" during Deadline week, and "The trade deadline has passed" after the Lock, so that the analyzer shows the event in a small way.
50. As a manager, I want to pick one partner or every team, so that I can ask about one manager or the whole league.
51. As a manager, I want position chips "Any · RB · WR · TE · QB", so that one tap says which position I want.
52. As a manager, I want a chip to set the same limit as a typed question such as "trade ideas for an RB", so that both ways give the same result.
53. As a manager, I want the Finder wait to use the same `StageLines` as the grade, one line at a time, so that both waits feel the same.
54. As a manager, I want the wait lines to be the real steps, such as "4 of 5 · Making a shortlist", so that I know what the Finder does.
55. As a manager, I want each wait line to hold until the next step ends, then swap with the same motion as the grade, so that the wait looks calm.
56. As a manager, I want the avatars of the teams to light up in turn as the Finder reads them, so that I see the search move.
57. As a manager, I want the wait lines to name no internal tool, such as "Read 11 teams", "Found 18 players who fit", "Built 42 offers", "Made a shortlist of 9", and "Picked the best 3", so that the copy is plain.
58. As a manager, I want the 3 trades to land as cards in one list under the hero, so that I can compare them.
59. As a manager, I want each trade card to lead with the Lean, so that I see the verdict first.
60. As a manager, I want only trades with Send it, Lean yes, or Gut call, never Lean no or Pass, so that the Finder shows only trades worth a try.
61. As a manager, I want a Case of at most 3 lines with its condition first, so that I get the reason fast.
62. As a manager, I want the Bullets folded under the Case, one tap to open, so that the card stays short.
63. As a manager, I want no headline on a card, so that one voice speaks.
64. As a manager, I want a tap on a trade to open it in the analyzer already graded, with no second grade, so that I can edit it and grade it again.
65. As a manager, I want a plain empty line when no trade fits, so that I know the search ran.
66. As a manager, I want an error line with Try Again when the search fails, so that I can retry.

### A faster Finder

67. As a manager, I want a press of the Finder to take about 25 s, not about 42 s, so that I do not give up.
68. As a manager, I want no retry of a bad offer id, so that 17 to 21 s of wait goes away.
69. As a manager, I want the Finder to pick the best 3 trades across all partners in one call, so that the 3 trades speak in one voice.

### Better trade ideas

70. As a manager with one picked partner, I want the Finder to skip the Partner filter, so that I get real offers, not one plain offer.
71. As a manager, I want the Shortlist to hold the best offer for each player I could give and for each partner, before more forms of one trade, so that the 3 trades differ.
72. As a manager, I want the Finder to offer a player of the other team only if he would start over my weak starter, so that a trade fills a real hole.
73. As a manager, I want the Finder to check my side too, so that it never offers my starter when I have no one who can play to replace him.
74. As a manager, I want a player who is Out not to count as cover, so that the Finder does not think I have depth that I do not have.
75. As a manager, I want the Finder to drop an offer that clearly makes my lineup worse, so that I never see "Zay Flowers for Goff" again.
76. As a manager, I want the Finder to drop an offer that clearly makes the other lineup worse, so that the other manager has a reason to say yes.
77. As a manager, I want an unsure answer to pass, and only a clear no to stop an offer, so that the Finder does not starve itself of offers.
78. As a manager, I want a failed check to count as an error, never as a no, so that a network blip does not hide a good trade.

### Fair-first trade ideas (decisions 13 to 17)

Stories 89 to 112 replace stories 57, 58, 67, 69, 70, 71, 72, and 73. Stories 75 to 78 and 81 to 85 stay.

89. As a manager, I want the Finder to show fair trades, not only trades that fill a need, so that it sparks ideas I had not thought of.
90. As a manager, I want 1-for-1, 2-for-1, 3-for-1, and 3-for-2 trades, so that I see ways to consolidate and ways to add depth.
91. As a manager, I want each shape in both directions, so that a trade where I give more players and one where I get more players both show.
92. As a manager, I want the side that gets more players to get more trade value, so that the one better player is paid for.
93. As a manager, I want a 1-for-1 trade within 10% of trade value either way, so that a swap is close to even.
94. As a manager, I want no filler player under 5 trade value on a side of two or three players, so that a trade is not padded to look even.
95. As a manager, I want a fair check of each trade that reads the trade value of each player and each side, so that "fair" means what the numbers say.
96. As a manager, I want the fair check to give the same answer whichever team is named first, so that a trade is not called fair only because it favors me.
97. As a manager, I want a trade dropped only on a clear no to fairness, so that an unsure trade still has a chance.
98. As a manager, I want the Finder to still drop a trade that clearly makes either lineup worse, so that "Kenneth Walker for Mahomes" and "Zay Flowers for Goff" never come back.
99. As a manager, I want a need to show as a reason in the Case, not as a gate, so that a fair trade that adds depth can still show.
100. As a manager, I want a card to say when the other team can spare the player I get, such as "fills your weak QB slot, and they can spare him", so that I see why the other manager might say yes.
101. As a manager, I want the five picks to spread across shapes and partners, so that I do not get five forms of one trade.
102. As a manager, I want the best trade for each shape and each partner to come first on the Shortlist, so that variety does not cost quality.
103. As a manager, I want five picks, with up to three near ideas folded under them as "Close, but not sent", so that I have more ideas to weigh.
104. As a manager, I want each trade card in the Ledger form, with "You get · N" and "You give · N" columns, so that a 3-for-2 reads as clearly as a 1-for-1.
105. As a manager, I want each player row to show the position, the NFL team, and the rank, such as "RB · DAL · RB8", so that I know each player at a glance.
106. As a manager, I want a trade value total under each column, so that I can compare the two sides.
107. As a manager, I want one plain line for the gap, such as "You get 9% more trade value", so that I see if the trade is even without math.
108. As a manager, I want no trade value on each player row, so that the card stays calm. The full result shows each value.
109. As a manager, I want the wait lines "Reading 11 teams", "Matching trade value", "Checking 4,667 trades for fairness", "Checking 77 against both lineups", and "Picking the best 5", with the real counts of my press, so that I see what the search does.
110. As a manager, I want the wait to make no promise of how long it takes, so that the site never states a time it cannot keep.
111. As a manager, I want a search around one player, and my keep and aim choices, to hold on every fair trade, so that those tools still work.
112. As a manager, I want two managers who press at the same time both to get full answers, so that deadline night does not break the Finder.

### The commissioner

79. As the commissioner, I want the Lock as one value in the client config, so that I change it in one place.
80. As the commissioner, I want the `finder` flag in CPC to stay off until I check the Finder on the phone, so that no manager sees it early.
81. As the commissioner, I want one run of the Spares tree on every CPC pair of week 11 to give me a list of about 30 lines, so that I can mark the wrong ones in about 10 minutes.
82. As the commissioner, I want each wrong line and each bad trade I find later to become a Backtest mark, so that the tree learns from what I marked wrong.
83. As the commissioner, I want "Kenneth Walker for Mahomes" and "Zay Flowers for Goff" as the first two Backtest marks, so that those ideas never come back.
84. As the commissioner, I want a change to the tree to merge only if it breaks no mark it got right, keeps or raises the count of right marks, and does not touch `YES_AT` or `NO_AT` or name a player of a mark, so that the tree only gets better.
85. As the commissioner, I want the backtest to run as one command, with its result in `EVIDENCE.md` for the Judge, so that the merge has proof.
86. As the commissioner, I want each failed stream of a trade Topic to log one line with its cause and its time, so that the next failure shows why.
87. As the commissioner, I want the cause of the failed first call of a trade Topic found and fixed, so that a manager does not see a failure before a fast retry.
88. As the commissioner, I want the site copy never to name Jev, the Advisor, the Finder, or me, so that the site speaks plain words.

## Implementation Decisions

### The Lock and Deadline week (decision 04)

- The Lock is one value in the client config of CPC: 00:00 Eastern on Tue 2026-11-24. Norcal has no Lock, so it has no Deadline week.
- Deadline week runs from the deploy until one day after the Lock, then the Deadline banner and the analyzer eyebrow go away by themselves. No deploy turns them off.
- The site has three states from the clock and the Lock: `open`, `last-hours` (under 3 h to the Lock), and `closed`. One pure function of the time and the Lock gives the state and the countdown text. The countdown has a tilde, shows days, hours, and minutes, and adds seconds in `last-hours`.
- Code and config say Lock. Site copy says "trade deadline". Copy never says "Rosters are locked".

### The Deadline banner (decision 08)

- A slot under the top band of the shell holds the Deadline banner during Deadline week. The top band grows to fit it, so the band height token must take the Deadline banner into account on each page, the front door too.
- The whole Deadline banner is the trigger of the shared sheet, through the sheet wrapper of the design package (ADR 0035, ADR 0037). Its accessible name is "Open the Trade Wire, N new trades", or "Open the Trade Wire, final. The trade deadline has passed." after the Lock.
- The layout is one grid: a gutter for the red dot, then one left edge for the eyebrow "TRADE DEADLINE" and the countdown. "Trade Wire" and the badge sit on the right, centred on the two lines. The top padding equals the bottom padding.
- The fills come from the theme tokens only: `bg-card` when open, `bg-accent` in the last hours, `bg-raised` when closed. Both themes work.
- The press state follows transitions-dev: scale 0.98 in 150 ms with the ease-out. The shimmer of the last hours stops under reduced motion.
- The badge reads "N new", where N is the count of week 11 trades. It hides at 0. After the Lock it reads "Final".

### The Trade Wire (decisions 03 and 08)

- A new read route on the Fly API, per client, reads the Sleeper transactions of the current week with a query string, so the Sleeper CDN cache does not delay it. It keeps its answer for 5 s, so all phones share one Sleeper read in each 5 s. That is at most 12 Sleeper calls per minute, under the limit of 1000.
- The route checks the passphrase through the read guard and does not count against the limit of 30 requests per minute per IP, because the phones at the dinner may share one IP.
- The route returns only accepted trades of week 11, newest first by the time Sleeper accepted them. Each trade has its time, and for each team: the roster id, the team name, the avatar, the players it gets with their positions, and the FAAB it gets. No draft picks. A pending or vetoed trade is not in the list.
- The trade parser of the `league` package keeps the FAAB of a trade, which it drops now. The route reads which team got a player from the `adds` of the transaction, never from the cached rosters.
- The site polls the route every 10 s while the tab shows, polls at once when the tab shows again, and stops while the tab hides. The poll stops at the Lock. After the Lock the Trade Wire keeps the last list and reads "Final".
- A failed read keeps the last good list and shows a short note. It never empties the list.
- A new trade slides in at the top (400 ms, the smooth-out ease, 8 px, 2 px blur), the rows under it move down, and the badge changes in place. Reduced motion shows it with no slide.
- The sheet holds, in order: the links "Grade a trade" and "Find a trade", the eyebrow with the countdown, the title "Trade Wire", the live dot with "Updated Ns ago", and the list. "Find a trade" shows only when the `finder` flag is on. Both links hide after the Lock.
- Spacing: inside a trade, 8 px (`sp-2`) between the time line and each side row. Between trades, a 16 px pad, a 1 px rule, and a 16 px pad.
- The empty line is "No trades yet this week.", or "No trades this week." after the Lock.

### The sheet drag (decision 08)

- The shared sheet wrapper of the design package stops an upward drag past the open height from lifting the bottom edge off the screen. The fix lives in the wrapper, so every sheet of the site gets it.

### The analyzer switch and the Finder look (decision 07)

- A new wrapper in the design package wraps the ui-sdk `SegmentedControl` (ADR 0035, ADR 0037). The analyzer hero uses it for "Grade a trade · Find a trade": full width, two equal halves, the sliding pill of transitions-dev, locked during a wait.
- The analyzer reads its mode from the URL, so a link can open Find mode.
- Find mode: the title "Trade Ideas", the line "Who has a trade for you?", the partner choice (one team or every team), the position chips `Any · RB · WR · TE · QB`, and the find button, all in the same dark hero as the grade.
- A chip sets `aim_position` of the Limit, the same field that a typed question sets.
- `StageLines` gets one change: a list of one line holds until the caller sends the next line, then swaps with the same motion. The Finder wait feeds it the real steps from the stream. The grade lines stay as they are.
- The avatars of the teams light up in turn as the stream reports each team read.
- The 3 trades land as cards in one list under the hero. Each card: the Lean, a Case of at most 3 lines with its condition first, the Bullets folded under it, no headline. Only Send it, Lean yes, and Gut call show.
- A tap on a card opens the trade in the analyzer in Grade mode, already graded with the read that the find route sent. No second grade runs.
- The empty line and the error line with Try Again stay as the ticket of 07 set them.
- The hero eyebrow reads "Trade deadline ~2d 14h 05m" during Deadline week, and "The trade deadline has passed" after the Lock, until Deadline week ends.

### The Finder speed (decision 02)

- Each offer on the Shortlist gets a short label, `A` to `J`, in the pick prompt. Code maps the label back to its offer id, so the id retry goes away.
- The offer sheets build at the same time.
- The Jev waves pace by a count per second, not by a fixed 1 s wait.
- The log-only Jev checks run after the answer goes out.
- One pick call stays. It picks the best 3 across all partners and writes the Lean and the Case for each.
- The progress streams, one step line as each step ends. The analyzer page reads the same stream as the front door.
- No prewarm of the result cache.

### The Finder steps (decisions 01, 05, 09, and 12)

- With one picked partner, the Finder skips the Partner filter. The Jev targets build the offers.
- The Spares tree replaces the four big questions of the Partner filter. For a pair of teams, code lists each player of one team at the position of a weak starting slot of the other team, when the giving team has a backup above the line behind him who can play now. A player who is Out is never cover.
- **Decision 12, the reading of that list:** the literal reading of decision 05, "a backup above the line behind him", with the can-play-now rule of decision 09. The research of decision 10 measured 117 of 132 ordered pairs with a listed player under this reading, and 29 of 132 under a surplus reading. The surplus reading would starve the Finder again, the fault of decision 01. Code keeps only the count rule. Jev judges each listed player (`no-math-filters`).
- Jev asks one Noul per listed player: "Would {player} start over {weak starter} of {team} for the rest of the season?" Code puts the trade chart value of both players in the state as a fact. Jev compares no numbers.
- The Spares tree runs on both sides of a pair: what the partner can give, and what the asker can give.
- Code decides. A side stops only if it lists no player, or if each listed player gets a clear no, below `NO_AT` 0.3. A yes or an unsure answer passes. A failed Jev call is an error, never a stop.
- The Shortlist holds the best offer for each player that the asker gives and for each partner, before more forms of the same trade. It cuts no trade by a score.
- The Shortlist asks one gain Noul per side: "Does {team} start a better lineup after this trade?" Code puts the lineup points of each side before and after the trade in the state as facts. A clear no, below `NO_AT` 0.3, drops the offer. An unsure answer stays. A failed call is an error, never a no.
- The weak-slot rule, `YES_AT` 0.7, and `NO_AT` 0.3 stay as they are.

### The fair-first Finder (decisions 13 to 17)

These decisions replace the gate of "The Finder steps" above. The Spares tree list and its Noul stay, as a source of reasons. Each number is from the live CPC rosters of 2026-11-19 and the week 11 chart.

**The Value screen (decision 14, ADR 0038).** It is the one cut of the Finder by math, and the one source of offers.

- Code builds each trade of the shapes 1-for-1, 2-for-1, 3-for-1, and 3-for-2, in both directions, from the players that pass `in_pool`.
- The side that gets more players gets 100% to 125% of the trade value sum of the other side. A 1-for-1 stays within 10% either way.
- Each player on a side of two or three players has at least 5 trade value.
- A player with no week 11 chart value never enters a Value offer. 29 of 148 pool players have none, Justin Herbert among them.
- No cap ranks the trades after the screen. With no screen, a press of Bo Girds has 95,092 trades. The band with its direction leaves 9,777 before the floor of 5 (decision 13, the 20% column with the direction rule), and the floor cuts more. Decision 13 did not count the band and the floor together.
- The targets step and the wider pass go. An anchor player, and the keep and aim choices of a Limit, become hard rules on Value offers.

**The Jev questions (decision 15).** Two steps.

- Step 1 asks one fair Noul of each Value offer. The state gets each player's `chart_value`, and each side under `offers.<n>.sides` lists its players and its `chart_sum`, next to the facts of today.
- The fair wording won a live probe against the old `FAIR` text:
  - Text: ``Is the trade in `offers.{n}` close to fair by chart value: {gives}?``
  - Yes: ``Each team gives about as much chart value as it gets, by the sums in `offers.{n}.sides`.``
  - No: ``One team gives a clearly larger chart sum in `offers.{n}.sides` than it gets back.``
- Step 1 asks the fair Noul once in each side order. Code takes the mean. A clear no on the mean, below `NO_AT` 0.3, drops the offer. The probe found an offer reads more fair when the team named first gets the larger sum.
- No Jev question asks about the consolidation premium. The Value screen holds it in code.
- Step 2 asks the need Noul and the gain Noul of each side. A clear no on the gain of either side drops the offer (decision 09). No need answer drops an offer.
- The Spares tree still runs once per pair and builds no offer. A "yes" for a player that the asker gets becomes a pick sheet fact, such as "fills the weak slot QB, and the partner can spare him."

**The spread (decision 16).**

- The offers that pass step 1 group by partner and by shape direction, up to 77 groups. The best of each group, by the fair answer, goes to step 2.
- The score is the fair answer alone, the mean of the two side orders.
- `varied()` puts first the best offer for each shape direction, then for each partner, then for each player the asker gives. The rest follow by score. The Shortlist stays at 10, labelled `A` to `J`.

**The requests (decisions 14 and 16).**

- The Jev requests of one partner split into chunks under the 64k context of one request. Today one request per partner fails above about 590 offers, and its offers pass as unsure. No long-context header.
- One pacer for the whole API process replaces one pacer per press. The Fly app runs one machine with one process. Two presses at once share the budget of 100,000 tokens per second.

**The pick and the cards (decision 17).**

- The pick call picks up to 5 trades and up to 3 near ideas.
- Each card is the Ledger of prototype 17: "You get · N" and "You give · N" columns, a row per player with the position, the NFL team, and the rank, a trade value total per side, and one plain gap line, such as "You get 9% more trade value". No row shows a trade value. The Lean, the Case, the folded Bullets, and "See the Full Result" stay.
- The near ideas fold under the picks as "Close, but not sent · N".
- The live wait lines, each with the "n of 5 ·" prefix, carry the real counts of the press: "Reading 11 teams", "Matching trade value", "Checking 4,667 trades for fairness", "Checking 77 against both lineups", "Picking the best 5".
- The meta line "This can take about 25 seconds." goes. No copy states a time (memory `no-time-claims`).

**The glossary.** `GLOSSARY.md` has Shape, Value screen, and Value offer. When the build lands, the entries Target, Offer, and Spares tree change: no targets step, an Offer comes from the Value screen only, and the Spares tree gives reasons, not a gate.

### The backtest (decision 05)

- One command runs the Spares tree on every CPC pair of week 11 and writes a list of about 30 lines for Brian. Each line is one stop or pass with the answer that decided it.
- Brian marks the wrong lines during `4ag:implement`. Each wrong line with his fix is a Backtest mark. "Kenneth Walker for Mahomes" and "Zay Flowers for Goff" are the first two.
- The backtest calls the live Jev, so `make check-fast` does not run it. Its result goes into `EVIDENCE.md`.
- A change to the tree merges only if no right mark breaks, the count of right marks stays or rises, and the change does not touch `YES_AT` or `NO_AT` or name a player of a mark.

### The failed first call (decision 06)

- Each failed stream of a trade Topic logs one line with its cause, its stage, and its time since the start.
- The ticket finds the cause from those lines and fixes it. A Fly machine always runs, so the cause is not a cold start. The likely cause is a long stream that drops.

### The flags

- The `finder` flag of CPC stays off. Brian turns it on after his phone check. The front door runs the Finder whatever the flag says, so the Finder fixes reach managers at once.
- The Deadline banner and the Trade Wire need no flag. The Lock in the client config turns them on and off.

## Testing Decisions

A good test checks what a manager sees or what a route returns, not how the code gets there. Brian checks these seams with the spec.

The seams, highest first:

1. **The site in a real browser.** Playwright WebKit, `devices["iPhone 15"]` at 390 by 660, iPad at 810 by 980 and 1080 by 740, and desktop at 1280 by 800, from the LAN URL, both themes, with a fixed clock and a stub of the Trade Wire route. It checks the three states of the Deadline banner, the countdown text, the tap that opens the sheet, the sheet content and links, the empty line, a new trade that slides in, no horizontal scroll, no overlap, the even padding of the Deadline banner, the even gaps of the Trade Wire, the analyzer switch, and the Finder wait and cards. Prior art: `analyzer-stage.spec.ts`, `front-door-*.spec.ts`, and the checks of prototypes 07 and 08.
2. **The site parts in Vitest.** The state and countdown function at the edges (3 h, the Lock, one day after), the badge count, the poll that stops when the tab hides and at the Lock, the failed read that keeps the list, `StageLines` with a held line, the switch through its wrapper, and the drag limit of the sheet wrapper. Prior art: `stage-lines.test.tsx`, `trade-finder.test.tsx`, `sheet.test.tsx`, `top-band.test.tsx`.
3. **The API routes in pytest.** The Trade Wire route with a recorded Sleeper answer: only accepted week 11 trades, newest first, FAAB kept, sides from `adds`, the 5 s cache, the passphrase, and no count against the rate limit. The find route stream: the step lines, the labels `A` to `J` with no id retry, and the read sent with each trade. Prior art: `test_api.py`, `test_trade_topics.py`, and the fixtures of `cpc-week-10`.
4. **The Finder steps in pytest.** The Spares tree list on fixed rosters (the can-play-now rule, both sides), the decision rules (a clear no stops, unsure passes, a failed call is an error), the Shortlist variety, and the gain Noul drop, with Jev answers fixed in the test. Prior art: `test_finder_search.py`, `test_advisor_eval.py`.
5. **The backtest.** One command against the live Jev on the week 11 snapshot. It runs by hand, not in `make check-fast`, and its output goes into `EVIDENCE.md`. Backtest marks 1 and 2 stay right under the fair-first Finder.
6. **The fair-first Finder steps in pytest.** These go through the same seam as item 4, the search function of the Finder, with fixed rosters and fixed Jev answers:
   - the Value screen on fixed rosters: the shapes and directions, the band with its direction, the 1-for-1 band, the floor of 5, and no player without a chart value;
   - step 1: the mean of the two side orders, and the clear-no drop;
   - step 2: the best offer per group, the gain drop, and need that drops nothing;
   - the Spares tree "yes" as a pick sheet fact;
   - the spread of `varied()`: the best per shape direction first, then per partner, then per player;
   - the split of a large request under 64k;
   - one shared pacer under two presses.
   Prior art: `test_finder_search.py`, `test_jev_waves.py`.
7. **The Ledger cards and the wait in Vitest and Playwright.** These go through the seams of items 1 and 2: 5 picks, the near fold, the Ledger columns for a 1-for-1, a 2-for-1, and a 3-for-2, the gap line, the new wait lines, and no time claim. Prior art: `trade-finder.test.tsx`, prototype 17.

No test calls a paid API in `make check-fast`. The Jev answers in seams 3 and 4 are fixed inputs of the test, not a mock mode of the app.

## Out of Scope

- The Deadline Board. The Finder answers the same question for one manager, and real needs and spares need the Spares tree on each team (decision 08).
- The Trade Wire on the front door, and a grid of needs against spares (looks B and C of prototype 08).
- A Finder for three-team trades. Brian scrapped it (decisions 10 and 11).
- A push alert. Brian said it is not necessary.
- Norcal. The dinner is a CPC event.
- A theme for the whole site. The deadline look stays in the Deadline banner, the sheet, and the analyzer eyebrow.
- A stream of Finder results per partner, and a prewarm of the Finder cache (decision 02).
- The Accept tree, the split of the target question, and a Jev tree for fair (decision 05). The Value screen is the one math cut, by ADR 0038.
- A cap on the count of trades after the Value screen (decision 14). A later cap needs a new decision under ADR 0038.
- The long-context header of TypeSafe (decision 14). The split of a request covers the 64k limit.
- A trade value on each player row of a card (decision 17).
- A second Fly machine for the API. One shared pacer assumes one process (decision 16).
- The cause of the 29 pool players with no week 11 chart value. A follow-up (decision 14).
- A change to the weak-slot rule, `YES_AT`, or `NO_AT`.
- A season history in the Trade Wire. The transaction history of the weekly build already holds it.
- The upgrade of Next.js. It is an open decision of Brian.

## Further Notes

- The event must be live by Fri 2026-11-20 night. The Lock is 00:00 Eastern Tue 2026-11-24. The tickets should put the Deadline banner and the Trade Wire first, so the event can ship even if a Finder ticket runs late.
- Risk of the tight Lock: a trade between the end of the last game and the real lock of Sleeper shows after the Deadline banner says closed. Brian chose this over 03:00 Eastern.
- The front door runs the Finder now, so the bad ideas are live for every CPC manager until the Finder tickets merge.
- The Backtest marks list needs about 10 minutes of Brian's time during `4ag:implement`, after the Spares tree is built.
- The sheet drag fix touches every sheet of the site. Check each sheet on the phone.
- Prototype 08 found that the switcher bar of a prototype covers the grade bar of the analyzer at phone size. The switcher is not in the real build, so this needs no work.
- The fair-first tickets go on the same Spec branch and into the same PR. The PR is on hold by Brian's ruling. It opens only after the fair-first tickets merge, the evidence is recorded again, and the Judge passes. Brian gets preview links before the PR (handoff, ruling 8).
- The front door runs the Finder for every CPC manager, so a merge ships the fair-first Finder at once.
- The research of decision 13 and the probes of decision 15 cost $0.006 of TypeSafe in total. One fair Noul per Value offer, in two orders, costs a few cents per press.
