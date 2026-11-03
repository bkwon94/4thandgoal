# 10: Name removal is case-sensitive and leaves a bare player last name

**What to build:** `remove_names` is case-sensitive. The sentence "Behold the lamb won." keeps the capital "Behold" and the bare "lamb" after the removal of the team "behold the lamb". The check then matches the last name of CeeDee Lamb and fails the sentence. Make the name removal ignore case, with a test.

**Blocked by:** None.

**Status:** ready-for-agent

- [ ] "Behold the lamb won." passes in a chapter whose scope has behold the lamb and no CeeDee Lamb. A test covers it.
- [ ] `make test` passes. Ruff (`make lint`) stays at 123 or lower.

## Comments

2026-10-22: found in the tone 08 review.
