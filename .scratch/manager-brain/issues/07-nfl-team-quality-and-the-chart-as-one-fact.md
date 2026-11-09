# 07: NFL team quality, and the chart as one fact

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-8, AT-10, and AT-11.

**App:** pipeline

**What to build:** The sheet states the quality of each player's NFL team, from the nflverse team stats, so a player on a bad offense is not read as a safe start. The chart value is one fact with no gates. An unlisted player gets a fact that says he is not on the chart, and he stays in the Finder pool. A week with no chart still grades, and the Case says the chart is missing. The Playbook wins over the chart.

**Blocked by:** 01 and 02

**Status:** in-review

- [x] The sheet of Omarion Hampton has a fact on the quality of his NFL team.
- [x] With no chart for the week, `/analyze` returns a read, and the Case says the chart is missing.
- [x] A rostered player with no chart row has a fact that says so.
- [x] `make check-fast` passes.
