# 06: Break the three cycles and cut the API's render import

**What to build:** The import graph becomes a tree. The odds result model moves into the model module. The live module imports nothing from the orchestrator. The two waiver modules get their shared piece in a third module. The headshot URL and the defense check move into a model-layer module beside the player models, so the API imports neither render nor the orchestrator.

**Blocked by:** 05

**Status:** done

- [ ] No module-level import cycle. The two indirect cycles behind `TYPE_CHECKING` stay and are named in a comment.
- [ ] The API package imports nothing from render, pipeline, or cli.
- [ ] The model module imports no logic module.
- [ ] The four golden tests and the API tests pass with no golden change.

## Comments

- 2026-11-01: merged into `modular` from branch `modular-06-cycles`, commits cfaf3ea and 89dba96. 1,505 tests collected. The one direct cycle was the waiver pair; `rank_scores` now sits in `rank_score.py`. The live module had already dropped the orchestrator in ticket 05. `OddsResult`, `TeamOdds`, `Swing`, and `OddsStatus` sit in `models.py`. `is_def` and `headshot_url` sit in `player_ids.py`. An independent graph script finds no cycle and no API edge into render, pipeline, or cli. Two reviewers passed it after one fix pass.
