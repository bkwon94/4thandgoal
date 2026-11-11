# 07: The catalog after the hands-on test

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests AT-1, AT-26, AT-27, AT-30, AT-47, AT-52, AT-53, AT-54, and AT-55.

**App:** both

**What to build:** Brian tested the hunt by hand on 2026-11-07 and changed the catalog. The taps are a double-tap only. The holds are one action `hold` of 2 seconds or more. A long press on Android Chrome sends its hold. A 404 egg matches on any missing URL. An analyzer egg names two teams, and any graded trade between them matches. See the revisions of decision tickets 01 and 10.

**Blocked by:** none

**Status:** done

- [x] The listener sends `tap2` only for exactly 2 fast taps. A burst of 3 or more fast taps sends nothing. The tap combo stays.
- [x] The listener sends `hold` on the release of a press of 2 seconds or more. A press of 1 to 2 seconds sends nothing, and a cancel sends nothing.
- [x] On a touch press of an egg target, the listener calls `preventDefault` on `contextmenu`, so Android Chrome sends no `pointercancel` and the hold sends. A link, an image, a blurb, and a mouse right-click keep the menu.
- [x] The drop refuses an action that is not `tap2`, `hold`, or `select`, and the draft refuses such a spot.
- [x] An egg with `not_found = true` stores the page `*404` and matches a 404 check of any path.
- [x] The listener sends `trade_teams`, the two roster ids of the analyzer trade. An egg with `trade_teams` matches any graded trade between exactly those two teams. The drop refuses the old `trade` condition.
- [x] The draft prompt, the package docs, the PRD, and the acceptance tests state the new rules.

## Comments
- Closed by the merge of PR #19.
