# Matchup impact: each matchup blurb says what the week did to its two teams

Status: ready-for-agent
Date: 2026-11-03
Apps: pipeline. The pipeline adds the impact fact and a writer rule. The site shows the blurb text as it is, so the site does not change.
Spec branch: `matchup-impact`.
Source: the grill session of 2026-11-03. No map and no decision tickets, because the grill left no fog.
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

A matchup blurb tells how a game was won: the lead by game time, the turn, the injuries, and the recent adds. It does not say what the result did to the two teams. A manager reads that Maye d'force B with U beat Lil Fridge, but not that Lil Fridge lost first place, or that the playoff odds of Maye rose this week.

Part of the cause is the facts. The matchup prose blocks get the standings place after the week, the new records, the upset, and the head-to-head streak. They do not get the standings place before the week, the playoff odds, the median result, or a clinch or an out. The writer cannot say a number that no fact holds, because the verifier rejects it.

The other part is the writer rules. In week 8, the `recap_1` blurb had both standings facts in scope and cited neither. No rule asks a matchup blurb to say the impact.

## Solution

Each matchup gets one impact fact, `M<n>.impact`. It gives what this week did to each of its two teams: the standings place before and after, the cut, the playoff odds before and after, the median result, the streak, and a clinch or an out. It lists only the parts that apply this week.

The Matchup of the Week prose block and the six recap prose blocks get the impact fact in scope. A new rule in the writer prompt asks each of these blurbs to say the impact. A manager reads each matchup blurb and knows what the game meant for both teams.

The odds change is for the whole week, not for the one game. The other games and the median game also move the odds. So the fact text says "this week", and the writer cannot put the whole change on the game.

## User Stories

1. As a manager, I want each recap to say what the week did to both teams, so that I know if the game mattered.
2. As a manager, I want the Matchup of the Week blurb to say the impact too, so that the biggest game is not the one with the least context.
3. As a manager, I want to read that my team rose from 5th to 3rd in the standings, so that I see the climb, not only the place.
4. As a manager, I want to read when my team fell in the standings, so that a loss shows its cost.
5. As a manager, I want to read when my team stayed in its standings place, so that a win that held a place still reads as a hold.
6. As a manager, I want to read when my team crossed into the playoff spots, so that I know I am in position.
7. As a manager, I want to read when my team fell out of the playoff spots, so that I know I must catch up.
8. As a manager, I want the playoff odds before and after this week, so that I see the size of the change.
9. As a manager, I want the odds change to say "this week", so that the blurb does not blame one game for a change that the whole week made.
10. As a manager, I want each odds number named as playoff odds, so that I do not read it as a win chance.
11. As a manager, I want my median result in the recap, so that I know if I went 2-0, 1-1, or 0-2 this week.
12. As a manager, I want to read when both teams beat the median, so that a loser who still went 1-1 gets credit.
13. As a manager, I want to read when a game started a streak of 3 or more, so that a run shows when it starts.
14. As a manager, I want to read when a game extended a streak, so that I know the length of a run.
15. As a manager, I want to read when a game ended a streak of 3 or more, so that a broken run gets its note.
16. As a manager, I want to read when my team clinched a playoff spot, so that I know the week it happened.
17. As a manager, I want to read when my team is out, so that I know to sell.
18. As a manager, I want a clinch or an out only when the plain check is sure, so that the word is never wrong.
19. As a manager, I want the impact for both teams, so that the loser's side of the story is there too.
20. As a manager, I want the writer to choose the parts of the impact that matter most, so that the blurb stays short.
21. As a manager, I want six recaps that do not say the impact the same way, so that the page does not read like a form.
22. As a manager, I want the impact to leave out a part that did not happen, so that the blurb does not say "no change" for every kind.
23. As a manager, I want an early week with no odds from last week to leave out the odds change, so that the blurb never shows a made-up number.
24. As a manager, I want the impact numbers to match the standings table on the page, so that the blurb and the table agree.
25. As a manager, I want the impact odds to match the `Playoff %` column, so that the blurb and the rankings page agree.
26. As the league owner, I want the impact in every matchup blurb, so that the outcome holds for all seven blurbs.
27. As the league owner, I want proof from a real week build, so that I know the writer uses the impact.
28. As the league owner, I want a code check only if the guideline misses, so that the writer keeps its room when it does not need a rule.
29. As the league owner, I want the weekly odds engine to run once, as now, so that the build does not get slower.

## Implementation Decisions

- **Scope.** The Matchup of the Week prose block and the recap prose blocks get the impact fact. The Next Week prose block does not, because the swing line covers a game that is not played yet.
- **One impact fact for each matchup.** The matchup fact group adds `M<n>.impact`. It covers both teams of the matchup. It sits under the `M<n>.` prefix, so the Matchup of the Week and recap prose blocks get it in scope with no change to their fact lists. The Game Changer prose block keeps its narrow list and does not get it.
- **The six parts.** The fact holds only the parts that apply this week:
  1. The standings place before and after. The place before comes from the ranks before the week, which the context already builds for the upset fact. Use the words "rose from 5th to 3rd in the standings", "fell from 1st to 2nd in the standings", or "stayed 4th in the standings".
  2. The cut. Name it only when a team crossed into the playoff spots or fell out of them this week.
  3. The playoff odds before and after. The odds before are last week's saved odds in last week's `facts.json`. The odds after are this week's. The weekly engine run does not change. The text reads "playoff odds went from 88% to 74% this week" and uses the whole-percent rules of the odds facts.
  4. The median result. Say if each team beat or missed the median, and its record for the week, such as 2-0, 1-1, or 0-2.
  5. The streak. Name a head-to-head streak of 3 or more that this game started, extended, or ended. It uses the head-to-head streak rule of the streak fact. The median game does not count, as for **Streak on the line**.
  6. A clinch or an out. Name it only in the week that the plain check first gives it.
- **The early weeks.** A week with no saved odds from the week before leaves out the odds part. That is each week before `ODDS_FROM_WEEK` + 1. The other parts still apply.
- **The writer rule.** A new rule in the writer prompt asks each Matchup of the Week and recap blurb to say the impact of the week for both teams. The writer chooses the parts. The rule asks for a different shape across the six recaps. The rule names the impact fact as the source of an odds number in a recap. Rule 23 still governs the odds of other prose blocks.
- **No code check now.** The verifier does not fail a blurb that leaves the impact fact uncited. A rebuild of week 8 counts the blurbs that say the impact. If a blurb misses, a later ticket adds a code check in the shape of the required why.
- **Terms.** `GLOSSARY.md` holds **Impact fact** and **Standings place**. A fact says "rose" or "fell" in the standings, never "moved", because **Movement** is the power rank and **Move** is a roster change.

## Testing Decisions

A good test reads the facts that a week build makes and checks their text. It does not reach into the helper functions that build the parts.

The test seams:

1. **The fact sheet of a fixture week.** A test builds the facts from the fixture raw data and reads `M<n>.impact`. It checks each part against the fixture: the places, the cut, the median result, the streak, and the absence of an odds part with no saved odds. Prior art: `tests/test_facts_matchup.py` and `tests/test_sheet.py`.
2. **The prose block scope.** A test checks that the Matchup of the Week and each recap prose block list `M<n>.impact`, and that Next Week and Game Changer do not. Prior art: `tests/test_sheet.py`.
3. **The golden file.** The golden file of the fixture week gains the impact facts. Prior art: `tests/test_golden.py`.
4. **A real build of week 8.** This is not a unit test. The build writes the seven matchup blurbs with the new rule. A reader counts the blurbs that say the impact. The result decides whether the code check is needed.

## Out of Scope

- The Next Week blurb. The swing line covers it.
- The share of the odds change that comes from one game. It needs extra engine runs for each matchup each week.
- The head-to-head season series and the points-for tiebreaker. They add facts with little gain.
- A code check that fails a blurb with no impact. A later ticket adds it only if the week 8 build shows a miss.
- Any change to the site.

## Further Notes

- The week 8 page is live. The rebuild of week 8 is for proof only. Do not publish it unless Brian asks.
- The impact fact for the Matchup of the Week overlaps the `PICK` fact and the upset fact. The writer rule must not make the blurb repeat the upset in two sentences.
