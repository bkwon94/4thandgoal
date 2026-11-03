# 02: The season file, the rankings command, and the publish copy

**What to build:** One file per season, `rankings.json`, beside the week folders in the site output, written in full on every build after the page, from the formula over every week from 1 to the current one. Blurbs are empty in this ticket. A new `rankings` command writes the file for a saved week with no writer call. The build writes it too, or logs a warning and skips it when the history is not complete, so a missing past week never blocks the page. The publish command copies the file beside the week folder in the same commit. The schema version is 1. Running the command on week 6 is the demo: the file holds weeks 1 to 6.

The file shape, which site ticket 01 reads word for word:

```
{
  "schema_version": 1,
  "season": 2026,
  "weeks": [
    {
      "week": 6,
      "rows": [
        {
          "roster_id": 3,
          "name": "Lil Fridge",
          "wins": 10,
          "losses": 2,
          "rank": 1,
          "movement": 2,
          "components": { "standing": 1, "form": 3, "schedule_played": 6, "scoring": 2 },
          "blurb": [ { "text": "...", "fact_ids": ["PR.3"] } ]
        }
      ]
    }
  ]
}
```
Rows are in rank order, 1 to 12. `movement` is last week's rank minus this week's, or `null` in week 1. Each component is a rank of 1 to 12. `blurb` is a list of sentences, empty when no blurb exists for that week.

Spec: `.scratch/rankings/PRD.md`, section "The season file".

**Blocked by:** 01 The formula.

**Status:** ready-for-agent

- [ ] The `rankings` command on a saved week writes the file with one entry per week from 1 to that week, rows in rank order, blurbs empty.
- [ ] The build writes the same file after the page.
- [ ] An incomplete history logs a warning, skips the file, and the page still builds, in a test.
- [ ] The publish copies the file beside the week folder, in the existing publish test.
- [ ] The file render test checks the schema version, twelve rows per week, the row keys, and null movement in week 1.
- [ ] The command runs on the real week 6 and the file holds weeks 1 to 6. Note the top three of week 6 in a comment at the bottom of this file.
- [ ] `make test` passes. Lint count on the branch is no higher than on main.

## Comments

- 2026-10-22: `make rankings WEEK=6` on the real history wrote weeks 1 to 6. Week 6 top three: 1 Lil Fridge 10-2, 2 London Cooking 9-3, 3 Bo Girds 8-4. All three show movement 0. London Cooking has schedule played rank 12.

- 2026-10-22: fixes amended into `601be8e`. The file never shrinks: it covers weeks 1 to the latest saved week.
