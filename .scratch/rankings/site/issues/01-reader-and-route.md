# 01: The reader and the route

**What to build:** A league member opens `/rankings` and sees one table of twelve rows for the latest week: power rank, movement as an arrow with the count, avatar and team name, record, and the four component ranks. A reader loads the season file for the latest season, checks the schema version, throws on a mismatch, and returns null on no file. A missing file renders a short empty state. On a phone at 390 the four component ranks fold under the row, and the page has no sideways scroll. The avatars come from the latest published week's page through the existing week reader. This ticket works from a fixture file in the exact shape the pipeline writes. No blurb row yet.

The file shape, which pipeline ticket 02 writes word for word:

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

Spec: pipeline repo `.scratch/rankings/pipeline/PRD.md`, section "The site". This repo's `.scratch/rankings/site/PRD.md` points there.

**Blocked by:** None (can start immediately).

**Status:** done

- [ ] The reader reads the fixture, throws on a schema version other than 1, and returns null when the file is missing. Tests like the week reader's.
- [ ] `/rankings` renders twelve rows in rank order with rank, movement arrow and count, avatar, team, record, and four component ranks, in a component test on the fixture.
- [ ] Week 1 style null movement renders as a dash, not an arrow.
- [ ] The movement arrow colors read in light and dark; the dataviz skill is read before the color choice.
- [ ] At 390 wide the component ranks fold under the row and there is no sideways scroll. Checked with agent-browser at viewport 390 by 844 with reduced motion.
- [ ] A missing file renders the empty state and the build still passes.
- [ ] Any new token is in the class helper's group list.
- [ ] Every test passes and the static export builds.

## Comments

- 2026-10-22: built on `rankings-route` at `db0fbf3`, two Opus reviews, one fix pass. Awaits Brian merge with `--no-ff`.

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in db0fbf3.
Proof: The commit sits on `main` through the merge c6f2db70, and `_routes/rankings/` exists now.
Read 1 file: .scratch/todoist-queue/audit.md.
