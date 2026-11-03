# 02: The manager page shows the bye week

Spec: `.scratch/zz-dry-run/PRD.md`. Acceptance tests AT-2, AT-3, and AT-4.

**App:** site

**What to build:** each top performer row and each best add row of the manager page reads "Bye <week>" for a coming bye and "Bye done" for a passed bye. A null bye shows no text. (dry run)

**Blocked by:** 01.

**Status:** ready-for-agent

- [ ] The site schema of `managers.json` accepts the optional `bye_week`.
- [ ] The rows show the bye text at 375, 768, and 1280 px, in the light theme and the dark theme.
- [ ] The page shows no roster list.
