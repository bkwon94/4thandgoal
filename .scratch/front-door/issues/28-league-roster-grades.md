# 28: "Who has the best roster" reads the grades of every team

Spec: `.scratch/front-door/PRD.md`. Source: H13 of `.scratch/front-door/HANDS-ON.md`.

**App:** API

**What to build:** "who has the best roster" routes to How you stack up, which grades only the asker's team, and the free answer says "I can't rank rosters directly". A league-wide roster question now goes to the free answer, and the free answer gets a tool that reads the roster grade of each team of the league, from the same grade the manager pages use.

**Blocked by:** none

**Status:** done

- [x] The router sends "who has the best roster" and close forms to the free answer, not to stack_up; the route eval holds them.
- [x] A free tool gives each team's roster grade and its parts, best first.
- [x] Live: "who has the best roster" names a team and its grade, and passes the check.
- [x] "how do i stack up" still routes to stack_up.

## Comments
- Closes with the squash merge of the spec PR.
