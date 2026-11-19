# 04: What does the sim page look like?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

The page opens on Your team, with its odds and the 3 games left that move its odds the most. A manager picks winners, the odds animate to the new values, and the replay plays a run that follows the picks.

Build 2 or 3 different layouts of the page for Brian to choose from. Use ui-sdk, transitions-dev, and scrolltide, and meet the design bar of every UI ticket. Check each one on a phone. Record the choice, then delete the prototype code.

## Decision

Brian chose it on 2026-11-18, after five rounds of the prototype. A copy of the final prototype, its screenshots, and the data script is in `~/plans/season-sim-prototype/final/`. Round 1 is in `~/plans/season-sim-prototype/round1/`.

**The job of the page.** The page answers, for Your team, in this order:

1. **How many more wins do I need?** One sentence, such as "Win 6 of the 8 left and you're in." A win of the head-to-head game and a win over the median each count. The sentence names the smallest count of more wins with playoff odds of 90% or more. A tap opens the full ladder: each count of more wins, its playoff odds, and how likely it is.
2. **What happens this week?** "Week 11 vs <team>", with four tiles in a 2x2 grid: win and beat the median, win and miss it, lose and beat it, lose and miss it. Each tile shows the playoff odds after that result, how likely the result is, and the wins it adds. In a league with no median game, two tiles show.
3. **If you lose, root for these.** The header states the odds after a loss: "If you lose, you drop to 40%. These results lift you back up." Each of up to 3 rows shows "<winner> beats <loser>", a short reason ("2 wins ahead of you", "1 win ahead of you", "Level with you", "1 win behind you", "In the race for the last spot"), and one number: the odds after a loss and that result, such as "→ 45%". The base number is the odds over all runs where Your team loses its game that week. The two-number form "37% → 45%" confused Brian, because both numbers assumed a loss and the page did not say so.
4. **Sim it.** Two buttons: "Sim week 11" and "Sim the season".

**Layout D, "Cards".** The header shows Your team: avatar, name, record, the weeks left, and the playoff odds. Under it sits the sentence of part 1. A week switch follows (Wk 11 to Wk 14, then Playoffs). Each week page holds the week card of part 2 and the root-for card of part 3, then the two sim buttons in the flow, never fixed over content. On a phone, the root-for card opens from one row. From tablet width up, it always shows, and the week card sits beside it at desktop width. Content is capped and centered on a tablet. Brian chose D over E, "Steps", a guided flow under a meter of more wins.

**A result is a What-if.** A tap on a tile sets that result for the week. The odds, the sentence, and the root-for list update, and the next week opens. A line at the top lists what is set, with a Reset. The page has no grid of every game.

**The replay is three screens on one stage that never scrolls.** It opens as a fixed layer under the site header, with a header row (the screen tabs and close), a body, and a control bar in its own row (play or pause, Skip, Sim again, and Done at the end). It uses `100dvh` and the safe-area inset.

- **Season:** the week, its median score, and the standings in the **Race** style: only the rows from the first spot after the byes to three below the playoff line are in full, plus Your team. The byes fold into one line at the top, and the teams out of it fold into one line at the bottom. Only Your team's row has an avatar. A W or L flashes when a row moves. The bye line and the playoff line are plain rules. Rows reorder with FLIP after each week. Brian looked at three styles (plain, movers, race), asked which one I liked, and accepted Race as the default on round 5 ("This is good").
- **Playoffs:** one round at a time with large rows. The teams with a bye wait in their own card, and the winners move on to the next round. The seeds lift from the table into round 1.
- **Champion:** a 120px avatar, the name, the seed and record, the playoff wins, and one line on where Your team finished.
- **Sim the week:** two parts in turn, with the tabs "Games" and "Standings". The games show one row each, with Your game first, then one line for the median: "Median 98.1 · you were below". Then the standings after the week in the Race style. Each tab of a part that has played goes back to it. The tab of a part not yet played is disabled.
- Reduced motion: fades only.

**The test rule.** A UI ticket of this spec checks each screen in WebKit at 390x660 (an iPhone in Safari with its bars), on an iPad at 810x980 and 1080x740, and at 1280x800, with a check that no text overlaps other text and no bar covers content. Round 2 passed at 390x844 in Chromium and failed on Brian's iPhone.

**For the spec:** a long team name cuts the name of the loser in a root-for row. The real page wraps that line or uses a short name.

## Comments

**Round 1, 2026-11-18.** Three variants on `/sim-prototype/`: A "Broadcast" (a scroll story with big game cards), B "Board" (a grid of every game and a live table), C "Path" (a timeline with "Pick my best path"). A copy is in `~/plans/season-sim-prototype/round1/`. Brian chose none. His feedback:

1. The page does not say what it is for. Its job is to show Your team, its playoff odds, and what you need to happen each week: your own game, and what to root for if you lose.
2. It must show how many weeks you need to beat the median, and how that moves your odds.
3. It must also be a fun way to sim the season or one week, to see what can happen.
4. The replay is the one of the midseason report, and it does not fit the screen. The bracket shows below the fold, and the champion shows after you scroll back up. Think of it as three screens: the regular season with live standings and the median, the playoff bracket, and the champion, with a transition between each.
5. No endless scroll. A long page keeps a manager from its use.

Brian agreed to the frame of round 2 (grill Q1 to Q5): the page answers, in order, "how many more wins do I need" (a ladder of results, the median counts), "what happens this week" (four results: win or lose, above or below the median), and "if I lose, what do I root for". This week comes first, and the later weeks fold. A pick is a result that you tap in place, not a grid of games. Round 2 builds two layouts of this frame, each with a three-screen replay.

**Round 2 and 3, 2026-11-18.** Two layouts of the new frame: D "Cards" (one page per week, a week switch, the ladder behind the headline) and E "Steps" (a guided flow under a meter of more wins), each with a new three-screen replay. Round 2 failed on the iPhone: it was tested at 390x844 in Chromium, but Safari's bars leave about 390x660, so the buttons covered the tiles and the replay overlapped. Round 3 tested in WebKit at 390x660, on iPad, and at 1280, with an overlap check. Brian chose **D**. His feedback on round 3:

1. Sim the week is fine but still cluttered. The standings after it are very cluttered.
2. After the standings show in the week replay, the "Games" tab does nothing.
3. Sim the season is good, except the clutter of the standings.
4. "If you lose, root for" is good, but it is not clear what the numbers mean or why to root for each result.

Round 4 builds three row styles of the standings on a toggle (plain, movers, race), one row per game in the week replay, the tab fix, and a reason on each root-for row.
