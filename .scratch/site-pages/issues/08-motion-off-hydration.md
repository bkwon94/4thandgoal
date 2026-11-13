# 08: The reduced-motion class differs between the server and the browser

**What to build:** With reduced motion on, the dev page warns of a hydration mismatch on the chevron class of a rankings row. `useMotionOff` in `src/lib/motion.ts` reads the media query only in the browser. So the server HTML carries the transition class and the browser does not. Find a fix that keeps the static export. For example, apply the motion-off branch after mount, or move the choice into CSS with a media query.

**Blocked by:** None

**Status:** wontfix

- [ ] Reproduce the warning in the dev page with reduced motion on.
- [ ] Choose a fix that keeps `pnpm build` and `pnpm check:export` passing.
- [ ] The dev page shows no hydration warning with reduced motion on or off.
- [ ] The chevron still skips its transition with reduced motion on.
- [ ] `pnpm typecheck` and `pnpm test` pass.

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12.
Proof: The rankings row chevron and `src/lib/motion.ts` are gone since the redesign 0a8b8868, and `useMotionOff` now wraps the Framer `useReducedMotion`; nobody checked the warning again on the current pages.
Read 1 file: .scratch/todoist-queue/audit.md.
