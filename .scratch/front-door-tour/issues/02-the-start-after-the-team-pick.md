# 02: The start after the team pick

Spec: `.scratch/front-door-tour/PRD.md`. Acceptance tests AT-1, AT-5, AT-6, AT-32, and AT-38.

**App:** site

**What to build:** A league mate on a new browser picks a team in the team sheet. The Tour starts only after the team sheet finishes its exit, so Stop 1 points at the real Suggestions of that team. The Tour starts only when no `[aria-modal="true"]` element is open, such as the team sheet, the passphrase modal, or an Announcement. If one is open, the Tour waits and starts after the last one finishes its exit. If a text field has focus when the Tour starts, the Tour blurs it first and waits for the keyboard lift to end. The norcal front door shows the same Tour.

**Blocked by:** 01

**Status:** done

- [x] On a new browser, Stop 1 shows on the Suggestions of Bo Girds after the team sheet closes (AT-1).
- [x] No dim and no Stop card show while the team sheet is open (AT-5).
- [x] With a modal layer open, no Stop card shows, and Stop 1 shows after the layer closes (AT-38).
- [x] The norcal front door shows the same four Stops and copy (AT-6).
- [x] With the ask box focused before a start, no text field has focus at Stop 1 (AT-32).

## Comments

- Closes with the squash merge of the spec PR.
- The branch front-door-tour-02 merged into front-door-tour on 2026-11-18 as c70c0c47.
- 17 Vitest tests and 3 Playwright tests cover the start rules, on cpc and norcal.
- No Announcement is on main yet, so AT-38 uses a test modal layer with an exit fade, as Brian approved on 2026-11-19.
- Read 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/front-door-tour/PRD.md, .scratch/front-door-tour/ACCEPTANCE.md, .scratch/front-door-tour/issues/02-the-start-after-the-team-pick.md.
