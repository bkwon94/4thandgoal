# 06 — Shared API call hook

**Repo:** site. **Spec:** none. This is a cleanup found in the ticket 05 review.

**What to build:** The trade form and the trade finder each copy about thirty lines of fetch, timeout, abort, stale-run guard, and 401 handling. Move them into one hook. Both components use the hook. The behavior does not change.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] One hook holds the fetch, the timeout, the abort, the stale-run guard, and the 401 handling.
- [ ] The trade form and the trade finder both use the hook.
- [ ] The existing tests pass unchanged.

## Comments

2026-10-22: Found in the ticket 05 review.
