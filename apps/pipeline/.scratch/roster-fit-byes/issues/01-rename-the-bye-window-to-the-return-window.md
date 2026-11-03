# 01: Rename the bye window to the return window

**What to build:** The window that a hole reads ahead for a starter due back is the return window, not the
bye window. The tunable, its comment, every docstring and code comment, the test comments, and the rubric
prompt test say "return window". The rubric prompt test pins the two new paragraphs of the prompt, the
return paragraph and the bye exception paragraph, and the new tunable name. No grade changes. This is a
prefactor so that ticket 02 removes the bye read from a window that already has the right name.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] The hole read uses the injury read's return window tunable, trade week plus two, and the bye window tunable is gone.
- [x] No source, test, or prompt text says "bye window".
- [x] The rubric prompt test asserts the new return paragraph and the new bye exception paragraph.
- [x] The full suite passes and ruff is clean.
- [x] The hand-worked table passes with its letters unchanged.
