# 09: The analyzer form and the picker

Spec: `.scratch/site-redesign/PRD.md`. Acceptance tests AT-19, AT-20, AT-21, AT-22, and AT-23.

**App:** site

**What to build:** The analyzer is one scroll, the Stack: the teams row with up to 4 teams, one card for each team that says what it gets, and the picker "Gets" with a tab for each other team, a search field, and the position chips. Each pick names its source team, so the form has no send-to control. The "Grade the Trade" bar sits on the dock.

**Blocked by:** 04

**Status:** done

- [x] The empty analyzer shows two teams, "2 of 4", and the bar turned off.
- [x] The sheet closes with Done, the close button, and a tap on the dim page, and keeps the picks.
- [x] A third and a fourth team can join and leave.
- [x] The body of `POST /analyze` has the same shape as on `main` for the same trade.
- [x] The empty analyzer is on the full floor, and the floor passes.
- [x] The local dev server runs for Brian after the build.
- [x] The evidence of AT-19, AT-20, AT-21, AT-22, and AT-23 is recorded in `EVIDENCE.md`.

## Comments
- Closed by the merge of PR #11.
