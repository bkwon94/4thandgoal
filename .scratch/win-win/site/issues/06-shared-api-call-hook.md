# 06 — Shared API call hook

**Repo:** site. **Spec:** none. This is a cleanup found in the ticket 05 review.

**What to build:** The trade form and the trade finder each copy about thirty lines of fetch, timeout, abort, stale-run guard, and 401 handling. Move them into one hook. Both components use the hook. The behavior does not change.

**Blocked by:** none

**Status:** done

- [ ] One hook holds the fetch, the timeout, the abort, the stale-run guard, and the 401 handling.
- [ ] The trade form and the trade finder both use the hook.
- [ ] The existing tests pass unchanged.

## Comments

2026-10-22: Found in the ticket 05 review.

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 15e288c6.
Proof: "Move the hooks into src/hooks and add useRequest" moved the abort and stale-run guard into one hook for both forms, but the timeout and the 401 handling stay in each caller by choice.
Read 1 file: .scratch/todoist-queue/audit.md.
