# 10: Archive the old pipeline repo

Spec: `.scratch/one/PRD.md`. Solution part 1.

**What to build:** The old pipeline repo is read-only, so no agent commits to it by mistake.

**Blocked by:** 03.

**Status:** done

- [x] The README of the old repo names the merged repo and the new path.
- [x] The old repo is archived on GitHub.
- [x] No LaunchAgent, script, or workflow on this machine points at the old path.

## Comments

- The merge: no branch. The old repo got the README notice `966f420` with `[skip ci]`, and `gh repo archive` ran on 2026-11-03.
- The proof: `gh repo view` reports `isArchived` true. No workflow ran for `966f420`, so no deploy of old code happened. A grep of the LaunchAgents, `~/repos/scripts`, the shell files, and the crontab finds no old path.
- The notes: the archive also stops the old Fly deploy job and the old cron of the daily refresh. Only one old path remains, in a historical ledger under `.scratch/`, by design.
- Read 2 files: .scratch/one/issues/10-archive-the-old-pipeline-repo.md, the README of the old repo.
