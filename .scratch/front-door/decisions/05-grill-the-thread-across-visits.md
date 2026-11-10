# 05: Does the Thread stay across visits?

Map: `.scratch/front-door/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Decide if the Thread stays in the browser after a visit, if it resets each week, and if the manager can clear it. The spec needs this for the state model of the site.

## Decision

Brian, 2026-11-09, in a grill.

1. The Thread stays in the browser for the fantasy week. The Tuesday build starts an empty Thread. Reason: the week is the unit a manager thinks in, and its facts mostly hold until the build. A Thread with no end grows a long list of stale weeks on a phone. A Thread that empties each visit throws away a trade read that the manager wants to come back to.
2. The site asks the API whether the fact key of each Answer in the Thread is still current. The check costs nothing. A stale Answer shows dimmed, with the line "Your roster changed since <day>. [Refresh]". A tap on Refresh gets a fresh Answer, which counts toward the cap of 25 only if Claude writes it. Reason: a snapshot shows a wrong read with no warning, and a re-ask on each visit spends the cap on Answers the manager may not reread.
3. The browser keeps one Thread per team for the week. A change of Your team shows the Thread of that team, and a change back shows the first Thread again. Reason: a quick look at another team must not erase the work of the manager.
4. A Clear action in the Thread header empties the Thread of this week for Your team, with no confirm. The record of opened Topics stays, so a cleared Topic does not come back to the Suggestions until its fact changes (decision 02).
