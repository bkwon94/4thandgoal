# 05: What does Jev read, what happens when Jev fails, and what does the log show?

Map: `.scratch/evidence-flags/MAP.md`.

**Kind:** spec

**Blocked by:** 01, 02

**Status:** done

## Question

Three small choices that the spec records. The first is the state that Jev reads: the text of the test, its section of `EVIDENCE.md`, the list of files in `evidence/AT-<n>/`, and the screenshots if ticket 01 allows them. The second is the behavior on a `JevError` or a missing `TYPESAFE_API_KEY`: the evidence goes on with no flags, and the log says so. The third is the one log line of each run, with the count of flags, the errors, and the input tokens, in the shape of the weekly build line. The fourth is the cut of each full-page shot into parts of 280 to 1568 px per side, because the API never resizes an image. Ticket 01 found this limit. Ticket 06 found that most false flags come from a state with missing parts, so the state sends every shot of the test and each text file in full, within the request limit of 32 MiB.

## Decision

`cpc:to-spec` recorded the four choices in `PRD.md`, under Implementation Decisions: "The state that Jev reads", "The image type and the cut of a shot", and "The failure and the log". Claude wrote them on 2026-11-10 from tickets 01, 02, and 06, for Brian to approve with the spec.
