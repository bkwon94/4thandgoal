# 03: The Thread across the week

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-3, AT-30, AT-31, AT-32, AT-33, AT-36.

**App:** site

**What to build:** The Thread reads top to bottom, newest at the bottom, with one row of Suggestion chips above the ask box. Each older Answer folds to one line with its question and one fact, and a tap opens it in place. The browser keeps one Thread per team for the fantasy week, and a later latest week starts an empty Thread. Clear in the Thread header empties the Thread with no confirm.

**Blocked by:** 02

**Status:** in-review

- [x] A change of Your team shows the Thread of that team, and a change back shows the first Thread (AT-3).
- [x] A new Answer lands open at the bottom, and the older one folds to one line (AT-30).
- [x] A tap opens a fold at its top under the header, and a second tap folds it (AT-31).
- [x] The Thread survives a closed tab on the same day (AT-32), and a rebuild with a later week empties it (AT-33).
- [x] Clear empties the Thread at once, and the opened Topics stay off the Suggestions (AT-36).
