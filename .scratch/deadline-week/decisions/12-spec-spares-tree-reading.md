# 12: Which reading of the code list of the Spares tree does the Finder use?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

The research of decision 10 found two readings of the code list that the Spares tree asks about. The surplus reading of decision 09 lists a player for 29 of 132 ordered pairs of teams. The literal reading of decision 05, "a backup above the line", lists a player for 117 of 132. The reading sets how many partners the two-team Finder sees. `4ag:to-spec` settles it with Brian. Facts: `10-research-three-team-finder.notes.md`.

## Decision

The spec takes the literal reading of decision 05, "a backup above the line behind him", with the can-play-now rule of decision 09. It lists a player for 117 of 132 ordered pairs. The surplus reading lists one for 29 of 132 and would starve the Finder again, the fault of decision 01. Code keeps only the count rule, and Jev judges each player (`no-math-filters`). Recorded in `PRD.md`, under The Finder steps.
