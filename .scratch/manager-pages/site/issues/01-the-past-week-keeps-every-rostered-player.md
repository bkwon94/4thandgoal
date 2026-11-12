# 01: The past week keeps every rostered player

**What to build:** the past week model keeps each roster's players and their points per week, read from the saved matchups that already hold them. Bench points, best adds, and top performers all read this. No new fetch and no change to the saved files. Pipeline repo.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] The past week model gives, per roster, every player on it that week with his points, bench included.
- [ ] The saved history tests cover a roster with bench players and a roster with an empty slot.
- [ ] Every existing test passes. No saved file changes.
- [ ] Each new or changed code file keeps its two-line docstring. Comments and the commit in STE.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 62b61cca.
Proof: The ticket copies pipeline ticket 01, done in "Merge manager-pages-01: the past week keeps every rostered player".
Read 1 file: .scratch/todoist-queue/audit.md.
