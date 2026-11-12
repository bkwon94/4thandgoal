# 10: Name removal is case-sensitive and leaves a bare player last name

**What to build:** `remove_names` is case-sensitive. The sentence "Behold the lamb won." keeps the capital "Behold" and the bare "lamb" after the removal of the team "behold the lamb". The check then matches the last name of CeeDee Lamb and fails the sentence. Make the name removal ignore case, with a test.

**Blocked by:** None.

**Status:** ready-for-agent

- [ ] "Behold the lamb won." passes in a chapter whose scope has behold the lamb and no CeeDee Lamb. A test covers it.
- [ ] `make test` passes. Ruff (`make lint`) stays at 123 or lower.

## Comments

2026-10-22: found in the tone 08 review.

Stays open in the audit of `todoist-queue` on 2026-11-12, as ready-for-agent. Brian kept it, because it fixes a real bug or changes what a manager sees.
Proof: `remove_names` in `packages/facts/python/src/facts/verifier.py` still runs `re.sub` with no `re.IGNORECASE`. The scope-team-word skip of 28fd4d8e may already hide the "Behold the lamb" failure, so the fix may have a small effect.
Read 1 file: .scratch/todoist-queue/audit.md.
