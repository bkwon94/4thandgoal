# 32: Each roster grade says when it is from

Spec: `.scratch/front-door/PRD.md`. Source: H19 of `.scratch/front-door/HANDS-ON.md`.

**App:** API and site

**What to build:** the manager page shows the grade of the weekly build (Bo Girds: B, through week 9). How you stack up and the roster grade tool read the live league (Bo Girds: C, Lamar Jackson on IR). The code is the same; the data differs. The live grade now says "as of today", and the grade of the manager page says "after week N".

**Blocked by:** none

**Status:** done

## Boxes

- [x] The manager page grade shows "after week N", from `through` of `managers.json`.
- [x] The data block of How you stack up shows "as of today" in a quiet label.
- [x] The stack_up slice carries `grade_as_of`, and `FACT_MEANINGS` says what it means.
- [x] The `roster_grades` tool result carries `as_of`, and `what_each_field_means` says what it means.
- [x] Each part has a test that failed first and now passes.

## Comments
- Closes with the squash merge of the spec PR.
