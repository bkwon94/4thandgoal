# 09: The week package and the chapter port

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-1, AT-11, AT-13, and AT-23.

**App:** both

**What to build:** The week moves into the `week` package, in both languages. Another package gives its chapter through the chapter port. A week with no median game has no Median Game chapter.

**Blocked by:** 06, 07

**Status:** done

- [x] The `week` package holds the modules of decision 01 and the median text.
- [x] The chapter port takes a chapter from another package. The registry of the site build lists only the chapters of the client.
- [x] A fixture test with the median off shows no Median Game chapter in `page.json` (AT-11).
- [x] A fixture test with no DEF slot shows no DEF in the pool and the leaders (AT-13).
- [x] A test client with only `week` builds a week with no rankings chapter and no rankings route (AT-23).
- [x] The CPC golden diff is empty (AT-1).

## Comments
- Closed by the merge of PR #3.
