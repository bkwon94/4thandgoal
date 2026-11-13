# 12: Move the finder and the waiver page to the Select picker

**Repo:** `cpcfantasyfootball`

**What to fix:** The trade form picks a team from a Select. The finder's "Trade Partner" list and the waiver page's team pick still use the old `TeamPicker` radio list, so the old component and its test stay. Move both to the Select, then delete `TeamPicker`, its test, and `team-pick.ts` if nothing else reads it.

**Blocked by:** None (can start immediately)

**Status:** wontfix

- [ ] The finder picks the partner from a Select with the avatar in each row
- [ ] The waiver page picks its team the same way
- [ ] `TeamPicker` and its test are gone

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12. Brian dropped it, because it fixes no real bug and changes nothing that a manager sees.
Proof: `TeamPicker` still serves `trade-finder.tsx` and the waiver page, but the target `Select` is gone since 0a8b8868, so the ticket must name a new target, such as the team sheet.
Read 1 file: .scratch/todoist-queue/audit.md.
