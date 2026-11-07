# 10: No hold egg on a blurb

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance test AT-56.

**App:** both

**What to build:** Brian decided on 2026-11-07 that a hold egg never goes on a blurb. On Android a long press on text starts the selection of a word, so the blurb keeps its menu and a hold there never sends. A blurb may take a double-tap egg. The blurb is one target, so a double-tap anywhere in it counts. See the revision of decision ticket 01.

**Blocked by:** none

**Status:** in-review

- [x] The draft prompt states the rule.
- [x] The draft refuses a `hold` on a `blurb-*` target and writes nothing.
- [x] The drop answers 422 for a `hold` on a `blurb-*` target and stores no egg. A `tap2` on a blurb drops.
- [x] The listener sends `tap2` with the id of the blurb for a double-tap anywhere in the blurb.
- [x] Decision 01, the PRD, and the acceptance tests state the rule. AT-56 tests it.
