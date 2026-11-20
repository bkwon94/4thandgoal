# 18: Which acceptance tests change?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** spec

**Blocked by:** 14, 15, 16, 17

**Status:** done

## Question

AT-41 to AT-47 are the Finder tests. The fair-first Finder may change AT-42, AT-43, AT-46, and AT-47 again, and may need new tests for the shapes and the value screen. `4ag:to-acceptance` records the change. The Judge runs again on the changed tests after the new tickets merge (handoff ruling 8).

## Decision

Brian approved the tests on 2026-11-19. `ACCEPTANCE.md` records them under Revisions.

- Changed: AT-36, AT-38, AT-41, AT-43, AT-45, and AT-46. AT-41 lost its 30 s limit, because it is a time claim.
- Retired: AT-42. The Spares tree gates no partner, and the targets step is gone.
- New: AT-55 to AT-71, for the Value screen, the two Jev steps, the spread, the request split, the shared pacer, the Ledger card, five picks, the wait, and the long-context header.
- The Judge runs on the changed and new tests after the fair-first tickets merge, with the evidence recorded again.
