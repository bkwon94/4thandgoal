# 21: The team name at most once per blurb

**What to build:** The writer, the tone, and the analysis prompts each get one rule: name a team at most once per blurb or per side analysis, as the punchline, and use "this side", "they", or the player names otherwise. The verifier counts team name mentions per blurb and fails a blurb that names one team twice. The analysis check does the same per side.

**Why:** The commissioner reads the prose and the team name is in every sentence. The week 7 build on 2026-10-27 is the first real check.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] One rule in `src/cornerstone/prompts/writer.md`, `tone.md`, and `analysis.md`, in the voice of the rules around it. Keep "roast by team name" in the tone; the roast lands once.
- [x] `code_check` in `src/cornerstone/verifier.py` counts whole-word mentions of each team name in the blurb text and fails on a second mention. The feedback line names the team and the count, with the same mask rule as the other lines.
- [x] `check_response` in `src/cornerstone/analysis.py` does the same per side analysis, for the two teams in the trade.
- [x] A team name that is also a common phrase, such as "behold the lamb", counts only as a whole phrase.
- [x] Tests with the call patched: a blurb with the team name twice fails with the right line; once passes; the analysis check the same.
- [x] A run of the writer on the saved week 6 facts for one chapter, with a real key, to read the result. Paste one blurb.
- [x] `uv run pytest -q` passes with no failed test.
- [ ] Deploy needs Brian's `fly deploy`. The weekly build reads the prompts from the repo, so the Tuesday job gets it from main.

## Result

Branch `team-name-rule`. The real run of `cornerstone rewrite --season 2026 --week 6 --chapter recap_4` passed on attempt 1, with 2 Claude calls. Each team appears once:

> behold the lamb sat 11th before this week and still beat Bo Girds, an upset by 5.34. Recent add Germie Bernard was the lucky pickup at 20.2 on a 8.13 projection, and without him, that is a loss. The losing starters dropped passes worth about 17.8, so the drops cost the game, and recent add Indianapolis Colts chipped in -0.85.

The saved blurb before this rule named Bo Girds twice. The check now fails that blurb.

Scope of the hard check: the prompt rule holds for every chapter. The verifier count runs only on the chapters about one or two teams: `motw`, `game_changer`, and each `recap_*` chapter. Chapters carry no "two-team" attribute, so `two_team_chapter(key)` and `TWO_TEAM_CHAPTERS` sit next to `SENTENCE_RANGES` in `src/cornerstone/sheet.py`. The 12-team chapters, such as awards and median, name many teams, and "they" is unclear there.

The match ignores case, so "Behold the lamb" at the start of a sentence counts. The bounds stay whole-phrase, so "the lamb" alone does not count. One helper, `repeat_failure`, gives the failure line for the blurb check and the analysis check.

`uv run pytest -q`: `564 passed, 8 deselected in 60.14s (0:01:00)`

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in ed455b93.
Proof: "Name a team at most once per blurb and per side analysis" is on `main`, and `repeat_failure` and `TWO_TEAM_CHAPTERS` still sit in `packages/facts`; the weekly build reads the prompts from `main`.
Read 1 file: .scratch/todoist-queue/audit.md.
