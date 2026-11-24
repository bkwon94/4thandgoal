# 04: What does the redesigned sim page look like?

Map: `.scratch/playoff-paths/MAP.md`.

**Kind:** prototype

**Blocked by:** 01

**Status:** done

## Question

Build 3 or 4 layouts of the sim page for Brian to run on a phone, with the real week 11 data of cpc and of NorCal. Each layout holds the Goal switch, the Finish list, the Path row, the Week plan, the Score to beat, the root-for list, and the League board beside Your team. Name each part, and say if it is a ui-sdk part from `@ui-sdk/react` or a new part from `@ui-sdk/core`, such as a bar chart of the odds of each team. Write a detailed brief of each part: how it looks, how it feels, and what it does. Follow the design bar: transitions-dev, scrolltide, apple-design, animate, critique, and polish. Test at 390x660 iPhone WebKit, iPad 810x980 and 1080x740, and 1280x800. Brian chooses the layout and which parts to build or rebuild.

## Decision

Brian chose variant D, "Board + your race", on 2026-11-24, after 2 rounds. The prototype is on the branch `playoff-paths-prototype` (commit `be131972` and the round 2b commit). A copy with the screenshots and the data script `make_race_prototype.py` is in `~/plans/playoff-paths-prototype/`.

**The layout, from the top.**

1. The title "The Race" and one line: the league, the week, and the weeks left.
2. The Goal switch: Spot, Bye, Seed, with a seed picker for 1 to 6. It is a `SegmentedControl` from `@ui-sdk/react`.
3. The Your team card: avatar, name, record, the odds of the Goal, and a status pill. It opens in place, in a `Collapsible`, not in a sheet. Open, it shows:
   - The Finish list, as a bar chart labeled "Rest of season". Each row shows the Finish, its chance, the final record such as "ends 19-9", and the odds of the Goal. A tap on a row opens its Paths in place. A tap on a Path opens the Week plan in a `Sheet`, with "Try it", which sets the results of Your team as a What-if.
   - The week card: the Score to beat for the opponent and the median, in two columns, "Coin flip" and "80% sure". Then the four result tiles (two for NorCal) as a `ToggleGroup`. Then the root-for list of every other game for the chosen result, with "Doesn't matter" for a game under 1 point, and median rooting for the 1 or 2 teams that matter most.
4. The League board: one row per team in odds order, with the name on line 1 and the pill and the record on line 2, a bar of the odds, and the number or "Out". Your team has a "You" tag. A Clinch line shows under a row in lighter text, and never on a Seed Goal. A tap on another team opens its Finish list and Week plan in a `Sheet`.

**The bar chart** is a new part from `@ui-sdk/core`: one tab stop, arrow keys between bars. It serves the Finish list and the League board.

**The colors.** Each bar is ink at 80% strength. Only Your team's bars take the client accent, so red on a chart means "you". Light mode keeps the gray `page` behind white `card`. The status pill is a quiet tint with text: green for Clinched, red for Out. The label names the best Goal locked: "Clinched 1 seed", then "Clinched bye", then "Clinched spot". A team In the hunt shows no pill, because with 2 weeks left 10 of 12 cpc teams are in the hunt and the pill would tell nothing. The state follows the Goal switch and uses the plain check on wins. The site has no green or yellow token, so the spec adds the tint tokens to `packages/design`. Out keeps red because the pill has text and Your team's row has the "You" tag. Brian, rounds 1 and 2.

**Live team names.** The prototype showed "Puka Deez..." for a team that Sleeper now calls "Teez Nuts", because the Tuesday build fetched `users.json` before the rename. Brian wants live names as part of this spec. Decision 07 settles how.

**The test rule.** Each screen is checked in WebKit at 390x660, on iPad at 810x980 and 1080x740, and at 1280x800, in light and dark mode, with an overlap check. D passed 60 states. The lowest contrast of a pill is 5.73:1.

**Rejected.** A "Season first" put this week under the fold. B "This week first" grew long when "The rest of the season" opened. C "Board first" hid Your team's own answer in a sheet. D takes the board of C and the Finish list of A.

## Comments

**Round 1, 2026-11-24.** Variants A, B, C on `/sim/2026/?variant=`. Brian leaned C or A. He asked for "The Race" with a capital R, and asked why the page had so much white: the variants used only the site tokens, and his phone is in light mode. All bars were the CPC red, which reads as "bad" on a chart. Brian set the status colors: Clinched quiet green, In the hunt quiet yellow, Out quiet red, with one green for every Clinched label.

**Round 2, 2026-11-24.** Variant D. Critique score 27/40 after the fixes. Brian agreed to hide the "In the hunt" pill and to keep Out red.
