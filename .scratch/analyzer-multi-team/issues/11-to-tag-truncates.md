# 11: A long team name in the To picker trigger truncates

**Repo:** `cpcfantasyfootball`

**What to fix:** With three or more sides, the To picker in a picked row shows the destination team name with an ellipsis when the name is long, so the full destination is not visible with the picker closed. The popup shows the full name. Seen at 768 and 1280, and at 390 for the longest names. See `.scratch/analyzer-multi-team/screenshots/form-four-768-light.png`.

**Blocked by:** None (can start immediately)

**Status:** wontfix

- [ ] The destination reads in full with the picker closed, or wraps to a second line
- [ ] The rows in the two columns still line up at the tablet and desktop tiers

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12.
Proof: The site redesign 0a8b8868 removed the `Select` To picker and `defaultTo` from `trade-form.tsx`, so the truncated trigger no longer exists.
Read 1 file: .scratch/todoist-queue/audit.md.
