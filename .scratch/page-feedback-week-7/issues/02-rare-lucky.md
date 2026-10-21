# 02: Make "lucky" rare

**What to build:** The writer says "lucky" at most once per page, and only for a recent add that scored at least twice its projection. The verifier gate for the word does not change.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] The tone rule reads: "lucky" at most once per page, only for a recent add that scored at least twice its projection.
- [ ] Writer rule 8 and the vocabulary entry for recent add carry the same limit, in the same words.
- [ ] No code counts the word. The verifier and its tests do not change.
- [ ] `uv run pytest -q` passes.
