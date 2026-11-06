# 10: NorCal end to end

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-2.

**App:** pipeline

**What to build:** `make midseason CLIENT=norcal WEEK=8` builds the full report for NorCal. Each rule reads the league settings, so the report has no median game, no DEF list, and a fixed bracket.

**Blocked by:** 04 and 09.

**Status:** ready-for-agent

- [x] NorCal records count one game a week.
- [x] Position top 10 of NorCal has no DEF list.
- [x] The sim of NorCal has a fixed bracket with no reseed.
- [ ] The review file of NorCal has every blurb with a verifier pass.
