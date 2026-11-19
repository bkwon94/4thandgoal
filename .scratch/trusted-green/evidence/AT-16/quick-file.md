# Add

Kind: bug
Status: in-progress
Branch: `bug-add`.
Source: the session of 2026-11-18.
Boundary: holds.

## Items

### 1. add gives the sum

Done condition: add(2, 2) gives 4.
Method: tdd
Cause: `add` in `calc.py` adds 1.
Red: at `458a34a5`, `python3 -B loop.py`

```text
Traceback (most recent call last):
AssertionError: add(2, 2) gave 7 apples
```

Green: at `70fc8277`, `python3 -B loop.py`

```text
loop passed
```
Test verdict: pending

### 2. The README names the loop

Done condition: the README names the loop.
Method: text only.
Red: none, text only.
Green: at `70fc8277`, the diff of the text.
Test verdict: none

## Comments
