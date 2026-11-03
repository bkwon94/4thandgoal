# 15 — The once-per-page rule for "lucky" is a check

Spec: `.scratch/nflverse/PRD.md`, "The Unlucky and Lucky awards". Found in the ticket 05 review on 2026-10-24.

**What to build:** The writer prompt says "lucky" at most once per page. The fact id gate in the verify step
checks that each "lucky" and "unlucky" sentence cites the right fact, but nothing counts them. The verify step
gains one check: the page says "lucky" in at most one sentence, "unlucky" in at most one sentence. A second
sentence fails the page as a word-gate failure does today.

**Why:** A prompt rule holds most weeks. A check holds every week.

**Blocked by:** None.

**Status:** done 2026-10-24

The rule follows the chapter order of the build. An early chapter, such as `motw`, can use up "lucky" before
the awards chapter, and then the awards chapter must write its Lucky award without the word.

- [x] A page with "lucky" in two sentences fails the verify step and the failure names both sentences.
- [x] A page with "lucky" once and "unlucky" once passes.
- [x] "Unlucky" does not count as "lucky".
- [x] Every existing verify test passes unchanged.
