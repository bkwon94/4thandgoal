# 07: What does the Finder look like, and how does it show progress?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** prototype

**Blocked by:** 02, 04

**Status:** done

## Question

Brian says the UI of the Finder is not great. It should match the analyzer stage, or bring something new. Build several radically different variations with `ui-sdk`, scrolltide, and transitions.dev, and the design skills of design-bar. Each one shows the pick of a partner, the progress of a search of every team, the trades as they arrive, and the empty state. Each one also shows position chips, such as `Any · RB · WR · TE · QB`: one tap sets the `aim_position` of the Limit, the same field that a typed question such as "trade ideas for an RB" sets. Brian chose the chips on 2026-11-18, after decision 09, because a manager does not know that he can type a position. Brian chooses on the phone at 390x660.

## Decision

Brian chose on 2026-11-19, after four looks on the phone: A · Stage, B · Focus, C · Thread, and D · Deck. "Consistency is key." The prototype is on the branch `deadline-week-07-proto` at `2eaadb70`, in `apps/site/src/app/_routes/analyzer/finder-proto/`. It stays off `main` as the primary source.

1. **One hero, with a switch.** The analyzer hero has a switch at its top: "Grade a trade · Find a trade". Brian checked look `E · Switch` on the phone (round 2, `cd385837` on the same branch): "way better". The switch is the ui-sdk `SegmentedControl`, through a new wrapper `packages/design/site/ui/segmented-control.tsx` (ADR 0035, ADR 0037). It runs the full width of the hero, two equal halves, with the sliding pill of `transitions-dev`. During a wait it takes the eyebrow of the hero and is locked. Find mode has the title "Trade Ideas" and the line "Who has a trade for you?". The Finder and the grade share one stage, so the Finder never sits below the form or above it. About half a day of build more than a Finder below the form.
2. **The look of A · Stage.** The Finder takes the dark hero of the analyzer. The trades land as cards under the hero, all 3 in one list, so a manager can compare them.
3. **One wait for both modes.** `StageLines` gets one change: a list of one line holds until the caller sends the next line, then swaps with the same motion. The prototype proved it. The Finder wait uses the same `StageLines` part as the grade (`stage-lines.tsx`): one line under the title, the same swap and timing. The Finder lines are its real steps from the stream, such as "4 of 5 · Making a shortlist". The grade lines stay as they are, because a grade is one call with no real steps.
4. **The avatars.** The one extra part of the Finder wait: the avatars of the teams light up in turn as the teams are read.
5. **The rest from the ticket.** The partner choice (one team or every team), the position chips `Any · RB · WR · TE · QB` that set `aim_position`, the Lean, a Case of up to 3 lines, folded Bullets, no headline, the empty line, and the error with Try Again. A tap opens the trade in the analyzer, already graded.

Out: the dot path of B (a second wait pattern), the full-screen sheet of B, the thread of C (the front door is already a thread), and the deck of D (it hides 2 of 3 trades).

The step lines name no Jev and no Advisor (`no-internal-names`): "Read 11 teams", "Found 18 players who fit", "Built 42 offers", "Made a shortlist of 9", "Picked the best 3".
