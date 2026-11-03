# 03: The game story data check

Spec: `.scratch/week-8-fixes/PRD.md`, part 3.

**What to build:** A report, not code. Find out what the saved week 8 data holds for a game story: each
player's injury status and when it changed, the timing of scores within the week (Thursday, Sunday early,
Sunday late, Monday night), and the Monday night result as a turn in a matchup. Say what is there, what is
not, and what one fetch would add. Write the report under `## Report` in this ticket.

**Blocked by:** none. Tickets 04 and 05 wait on this one.

**Status:** ready-for-agent

- [ ] List the saved files of week 8 under `data/2026/week-08/` and `data/2026/history/week-08/`, with one line each on what it holds.
- [ ] Injuries: which file holds a player's injury status, and does the data say when it changed?
- [ ] Timing: does any saved file give a game's day or kickoff, so a score can be placed on Thursday, Sunday, or Monday? Check the nflverse files too.
- [ ] Monday night: can the data say which matchups were open before Monday night and which flipped?
- [ ] For each gap, name the one fetch that would fill it, its source, and its cost. Prefer a source the provider already reaches.
- [ ] Recommend the smallest set of facts for ticket 04, as a list of fact names with their source file.
- [ ] Close with the files-read line.
