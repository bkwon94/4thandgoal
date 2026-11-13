# 09: The home page test reads a class name

**What to build:** `src/app/page.test.tsx` checks the red season number with `className` and `text-red`. The spec says a test never reads a class name. Find a check that a reader can see, or drop the assertion.

**Blocked by:** None

**Status:** ready-for-agent

- [ ] Decide whether a reader-visible check exists for the red season number.
- [ ] Replace the `className` assertion with that check, or remove it.
- [ ] No test in `src/app/page.test.tsx` reads a class name.
- [ ] `pnpm typecheck` and `pnpm test` pass.

## Comments

Stays open in the audit of `todoist-queue` on 2026-11-12, as ready-for-agent. Brian kept it, because it fixes a real bug or changes what a manager sees.
Proof: Commit 8159f80b removed the `text-red` `className` assertion; but `apps/site/src/app/page.test.tsx:322` from the front door (dc564361) now reads `className` again, so the last box still fails.
Read 1 file: .scratch/todoist-queue/audit.md.
