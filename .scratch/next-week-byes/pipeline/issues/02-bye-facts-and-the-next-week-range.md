# 02: Bye facts for the writer and the Next Week range

Spec: `.scratch/next-week-byes/pipeline/PRD.md`, "Facts, for the writer", "Position rank", "Bye cover".
Glossary: **Bye cover**, **Position rank**, **Must Watch**.

**What to build:** The Next Week chapter gives the writer one fact per player on bye, one bye cover fact
per key starter on bye, and one fact per team with nobody on bye. Its range is 2 to 6 sentences and its
brief says the byes are part of the preview. A week 7 build passes the verifier with the byes in the blurb.

**Blocked by:** 01 (byes on the next-week games).

**Status:** done

- [x] The weekly build loads the analyzer's snapshot from the files of the week, with no chart and no slow sources, and reads position rank from it. The bye list sorts the non-key players by that rank.
- [x] A bye cover per key starter on bye: the bench player with the highest lineup value who can fill his slot, from the lineup slots the best-lineup code builds. One bench player covers one slot. No such player means no cover.
- [x] Facts `NX.bye.<roster>.<pid>` with the name, the position rank, the bye week, and the starts of the window, through the number holder. A K or a DEF reads without a rank.
- [x] Facts `NX.bye.<roster>.<pid>.cover` for each key starter on bye, with the cover's name, rank, and points a game, or "No bench player can fill his slot."
- [x] Facts `NX.bye.<roster>.none` for a team with nobody on bye.
- [x] The Next Week chapter lists the `NX.bye.` facts, its range is 2 to 6, its scope teams and players include the bye teams and players, and its brief gains one line: the byes next week are part of the preview. No required fact.
- [x] Tests on the week 6 fixture bundle read the fact texts and numbers, the chapter's fact ids, and the range. A test covers a key starter with no cover.
- [x] `make build WEEK=7` in the worktree passes the verifier, and the Next Week blurb cites at least one bye fact.
- [x] `uv run pytest -q` and `uv run ruff check src tests` pass.

## Comments

- 2026-11-02: `main` holds the merge 9d9ecc8. Status set to done by the state-file sweep of agent-habits 02.
