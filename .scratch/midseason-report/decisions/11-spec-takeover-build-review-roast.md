# 11: How long does the takeover last, and how do the build, the review, and the roast setting work?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

These choices are small, so the spec records them. The spec needs: how long the home takeover lasts, the build command and its week input, how the writer's draft reaches Brian for review before the publish, the scale of the `roast` setting in `client.toml`, and the package boundary of the sim. The sim must plug in anywhere: its engine and its replay part do not depend on the `midseason` package (map, Brian on 2026-11-05).

The ticket 09 data run on 2026-11-05 added these items for the spec:

- The MVP, Jahmyr Gibbs, is also the RB #1 of Position top 10. Ticket 10 says no award repeats the #1 of another chapter. Decide if the MVP is an exception.
- The boards cut long lists to their first rows, with "Show all", and showed 3 steals, busts, hits, and misses where tickets 02 and 03 say 5. Set the counts.
- Points for must be the sum of the weekly scores, as the standings use. The season total from Sleeper differs by up to 1 point after stat corrections.
- Ticket 04 sets the trade lines "from the spread". Set an exact rule. The prototype used the top 2 gaps for Robbery and the next 2 for Clear win.
- nflverse had no injury row for A.J. Brown in weeks 2 to 5, so the injury source misses some absences. Decide the fallback.
- The first press of the replay plays a fixed run in the prototype. Decide fixed or random (ticket 13).

## Decision

Brian approved the spec on 2026-11-05. `PRD.md` records each choice under Implementation Decisions: the packages `sim` and `midseason` with the app as the wire, the build and publish commands, the review file, the takeover through the report week plus 1, the `roast` steps `off`, `warm`, and `hot`, the trade lines 90, 60, and 10, the MVP exception, the list counts, a random first run, and the fallback for a missing injury row.
