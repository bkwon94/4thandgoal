# 10: NorCal end to end

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-2.

**App:** pipeline

**What to build:** `make midseason CLIENT=norcal WEEK=8` builds the full report for NorCal. Each rule reads the league settings, so the report has no median game, no DEF list, and a fixed bracket.

**Blocked by:** 04 and 09.

**Status:** done

- [x] NorCal records count one game a week.
- [x] Position top 10 of NorCal has no DEF list.
- [x] The sim of NorCal has a fixed bracket with no reseed.
- [x] The review file of NorCal has every blurb with a verifier pass.

## Comments

- 2026-11-05, orchestrator: box 4 stays open. In two real NorCal runs, 2 and 4 of 26 prose blocks failed the verifier (arcs, luck, opener, roasts). The cause is friction between the writer and the code check, not a NorCal rule. Stage 2 of cpc:implement tunes the prompt and the check for every client.
- Closed by the merge of PR #13.
