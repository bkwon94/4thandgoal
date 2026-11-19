# 05: The analyzer switch and Find mode

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-26, AT-28, AT-31, AT-33, AT-34, AT-35, and AT-53.

**App:** site

**What to build:** The analyzer hero gets a switch, "Grade a trade · Find a trade": the ui-sdk SegmentedControl through a new wrapper of the design package, full width, two equal halves, with the sliding pill of transitions-dev. The analyzer reads its mode from the URL, so the links of the Trade Wire open the right mode. Find mode shows the title "Trade Ideas", the line "Who has a trade for you?", the partner choice of one team or every team, the chips "Any · RB · WR · TE · QB", and the find button, in the same dark hero as the grade. A chip sets `aim_position` of the Limit, the same field that a typed question sets. During Deadline week the hero eyebrow reads "Trade deadline" with the countdown, and "The trade deadline has passed" after the Lock. Find mode shows only when the `finder` flag is on. It offers no choice of three teams.

**Blocked by:** none

**Status:** ready-for-agent

- [x] The switch is the wrapper of the ui-sdk SegmentedControl, and its two halves differ in width by 1 px or less.
- [x] A link with the Find mode opens the analyzer in Find mode, and a link with the Grade mode opens Grade mode.
- [x] The chip "RB" sends `aim_position` "RB", the same value as the typed question "trade ideas for an RB".
- [x] The eyebrow reads the countdown during Deadline week and the passed line after the Lock.
