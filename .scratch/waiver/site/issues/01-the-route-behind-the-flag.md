# 01: The route behind the flag

Spec: `.scratch/waiver/pipeline/PRD.md` in the pipeline repo. Pipeline ticket 01 fixes the file shape.

**What to build:** A build with `NEXT_PUBLIC_WAIVER=on` has a waiver page per season and week with a
file, at a route beside the week page, and the masthead links the current week's page. A build without
the flag has no route and no link, as the finder flag works today. The page shows the masthead with the
week and the build time, the budget table as a plain list in budget order, and the best adds bucket as
a plain list: headshot, name, position, team, bye, week projection, rest of season projection. No
motion, no ring, no sheet yet. A week folder with no file has no route, and old weeks still build.

**Blocked by:** Pipeline 01 The week file, thin.

**Status:** done

- [x] `waiverOn` reads one env var in the config module, off by default, with a config test like the finder flag.
- [x] With the flag off, the export has no waiver route and the masthead has no link.
- [x] With the flag on, the export has a route for each week with a file and none for a week without.
- [x] The loader accepts a week with and without the file, and the types mirror the file.
- [x] The list renders from a fixture file with the fallback headshot on a missing image.
- [x] The page passes the export check.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in c80b0073.
Proof: "Merge waiver-01: the waiver route behind the flag" is on `main`, and every box is checked; clients later removed the flag.
Read 1 file: .scratch/todoist-queue/audit.md.
