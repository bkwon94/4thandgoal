# 07: What role the trade value chart plays

Map: `.scratch/manager-brain/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The rubric anchored the grade on the chart ratio. With the Advisor, does the chart stay, and what happens on a week with no chart? On cpc week 8 the saved PNG is 0.6 ms newer than its JSON, so the cache rule at `packages/league/python/src/league/chart.py:245` drops the read. With no chart, the unlisted rule empties every Finder pool, and the Finder finds nothing.

## Decision

Brian decided on 2026-11-09: "making it just another part of the context that Claude and Jev can use makes sense", and the fetch must be dependable, with a manual way to give the chart before a build.

1. **The chart is one fact with no gates.** Its value is the market price that the Advisor weighs. An unlisted player stays in the Finder pool, and his fact says he is not on the chart. A week with no chart still grades and still finds trades, and the case says the chart is missing. Where the chart and the playbook disagree, the playbook wins.
2. **The cache trusts content, not file times.** The fetch writes the PNG and then the JSON (`chart.py:301` to `:313`), so a normal run keeps the read. The week 8 files came from a hand placement, and a copy can flip the order of the two times. The saved read stores a hash of its PNG, and a read runs again only when the hash differs.
3. **One manual step.** Put the PNG at `data/nfl/cache/charts/<chart>/week-NN.png` before the build. Run `cornerstone chart --client <slug> --week NN` to read and check it. The build log says plainly when a week has no chart.

The cache fix also helps `main` now. The spec may ship it as its first ticket.
