# 11: The behind-injury rule needs a starter ahead

**What to build:** On the fresh week 6 board of 2026-10-24, sneaky held Athan Kaliakmanis, the WAS third QB, because Marcus Mariota is out and Kaliakmanis sits one slot below him. Mariota is a backup, so no role opened. The behind-injury rule should fire only when the out player is the depth chart starter, slot 1, or when every player above the candidate is out. Add a test with an out backup and a healthy starter: no sneaky entry.

**Blocked by:** None (can start immediately). Found on the real week 6 board, 2026-10-24.

**Status:** done

- [ ] A player behind an out backup with a healthy starter above is not sneaky.
- [ ] A player behind an out starter is sneaky, as today.
- [ ] A player with two out players above him is sneaky.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in dc564361.
Proof: Front-door ticket 15 commit 071b6021 added `every_above_out` in `packages/waiver/python/src/waiver/buckets.py` with the out-backup test.
Read 1 file: .scratch/todoist-queue/audit.md.
