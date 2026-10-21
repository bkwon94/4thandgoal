# Cornerstone Weekly

The weekly report page for the Cornerstone fantasy football league. It turns Sleeper and nflverse
data into facts, the facts into chapters of prose, and the chapters into a static site.

## Language

### The sheet

**Fact**:
One sentence of true data with an ID, the numbers it holds, and the teams and players it names.
_Avoid_: stat, data point

**Fact sheet**:
Every fact of one week plus the chapters that cite them.

**Chapter**:
One unit of prose on the page, with the fact IDs it may cite and the sentence range it must fit.
_Avoid_: section, blurb (a blurb is the written output, a chapter is the brief)

**Blurb**:
The sentences the writer wrote for one chapter, each with the fact IDs it cites.

**Writer**:
The Claude call that turns one chapter and its facts into a blurb.

**Verifier**:
The code check and the Claude check that reject a blurb with an uncited number or claim.

### Trades

**Trade**:
A Sleeper transaction that moves players or picks between two or more rosters.

**Trade window**:
The span of time whose trades belong to one week's page: from the prior build to this build, or
from the Tuesday cutoff when no prior fetch time is saved.

**Tuesday cutoff**:
08:00 Eastern on the Tuesday after a week's games. It opens the next week's trade window.

**Late trade**:
A trade made after the lineups locked, so the lineup shows the roster from before it.

**Grade**:
The writer's letter, A to F, for one side of a trade, formed from the trade chapter's facts.
_Avoid_: score, rating

**Before the trade**:
Weeks 1 to N-1, for a trade on the page of week N. Every grade input ends there.

**Trade value**:
A player's worth on the half-PPR redraft trade value chart for the week of the trade. It shapes
the grade and never appears on the page.
_Avoid_: value (alone), chart value, price

**Chart week**:
The chart whose date falls in a week's trade window. A trade in week N uses the week N chart.

**Unlisted**:
A traded player with no row on the chart week's chart. He gets no trade value.

**Position order**:
The tie rule the writer uses at equal rank and points: RB over WR, WR over TE, TE over QB, DEF low.
