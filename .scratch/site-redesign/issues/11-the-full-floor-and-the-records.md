# 11: The full floor and the records

Spec: `.scratch/site-redesign/PRD.md`. Acceptance tests AT-34, AT-38, and AT-41.

**App:** site

**What to build:** The full floor covers the 7 pages and the 3 open states of both clients, and the fast sweep covers every other built page. The records match the redesign.

**Blocked by:** 05, 06, 07, 08, 09, 10

**Status:** in-review

- [ ] The floor passes in CI for both clients, with its time in the log.
- [x] `GLOSSARY.md` holds the term changes of the spec: Top band, Menu, Sheet, Chapter, Page, Hero, Shell, and Pill bar. Masthead, Menu button, Compact bar, and Black chapter are gone.
- [x] No client builds a waiver page, and its URL shows the 404 page. The floor test "no waiver page is built, and its URL shows the 404 page" proves it for each client.
- [x] The branch changes no path under `apps/pipeline/`, `apps/api/`, or `clients/<slug>/published/`. The one exception is `apps/pipeline/tests/test_client.py`, which Brian accepted in the comment on ticket 04.
- [ ] The evidence of AT-34, AT-38, and AT-41 is recorded in `EVIDENCE.md`.
