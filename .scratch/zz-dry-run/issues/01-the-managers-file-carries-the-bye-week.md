# 01: The managers file carries the bye week

Spec: `.scratch/zz-dry-run/PRD.md`. Acceptance test AT-1.

**App:** pipeline

**What to build:** each top performer and each best add of each manager in `managers.json` carries the bye week of the player's NFL team, from the schedule that the bye line already reads. (dry run)

**Blocked by:** none.

**Status:** ready-for-agent

- [ ] A run of the page build for `2026` week 8 writes a `bye_week` on each top performer and each best add.
- [ ] A player who changed NFL teams carries the bye of his team now.
- [ ] A team with no bye in the schedule gets a null `bye_week`.
