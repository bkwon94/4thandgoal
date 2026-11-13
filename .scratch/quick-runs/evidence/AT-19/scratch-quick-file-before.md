# Scratch: two Quick wins for the Judge step

Kind: quick-win
Status: in-progress
Branch: `win-scratch-judge`.
Source: the session of 2026-11-13. A scratch file for AT-19, never on a branch.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Rewrite the depth phrases so a manager reads each one in one pass

Done condition: each phrase of `DEPTH_MEANINGS` in `apps/api/src/cornerstone_api/personal_facts.py` reads as one plain clause, with no "meaning" and no "starter count past the starters".
Method: text only
Red: none, text only.
Green: at `1111111`, the diff of the text.
Test verdict: pending

### 2. A quick task title has no slug in front

Done condition: a push of `.scratch/bugs/pick-owner.md` plans the task title "Pick owner: week_moves names the first owner of a traded pick", with no word in front.
Method: tdd
Red: at `7b5a17f~1`, `python3 -m unittest scripts.test_queue.AQuickFile.test_a_quick_file_title_is_its_h1_alone`

```text
FAIL: test_a_quick_file_title_is_its_h1_alone (scripts.test_queue.AQuickFile)
AssertionError: 'pick Pick owner: week_moves names the first owner of a traded pick' != 'Pick owner: week_moves names the first owner of a traded pick'
Ran 1 test in 0.004s
FAILED (failures=1)
```

Green: at `7b5a17f`, `python3 -m unittest scripts.test_queue.AQuickFile.test_a_quick_file_title_is_its_h1_alone`

```text
.
Ran 1 test in 0.004s
OK
```

Test verdict: pending

## Comments
