# 19: The swap as best and worst, and the words of luck

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-8, AT-59, and AT-60.

**App:** both

**What to build:** The schedule luck chapter matches the S3 v2 board of the Design canvas, row "Ticket 16 · the schedule swap", with text rows. The pipeline adds to `midseason.json` the best and the worst schedule of each team, with ties, and the facts of the worked example of the luck card. The site shows a short card above the luck table that explains the idea with one real team, the columns "Real wins", "Wins if you played everyone", and "Luck (gap)", and a word under each luck number: "lucky", "unlucky", or "even" under 0.5, in the accent color at 1.5 or more either way. The swap is one text row per team, sorted by the spread between best and worst, with no grid and no bar. Each table says its count in plain words. The page never says "All-play".

**Blocked by:** 18.

**Status:** ready-for-agent

- [ ] `midseason.json` of CPC week 8 gives Bo Girds a best of 14-2 on the schedule of Maye d'force B with U.
- [ ] The luck card shows the worked example of All You Need Is Love: 9 of 11 teams outscored in week 3, and 4.27 wins in all.
- [ ] All You Need Is Love reads "+2.73" with "lucky" in the accent color, and The Blue Tent at −0.09 reads "even".
- [ ] The swap renders as text rows with no grid and no bar, and the word "All-play" shows nowhere on the page.
- [ ] A rule test covers the best and worst schedule with a tie.
