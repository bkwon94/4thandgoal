# Week 8 fixes: the odds, a shared award, and recaps with the game story

Status: ready-for-agent
Date: 2026-11-03
Repo: the pipeline. The site renders what the pipeline writes, so no site ticket is expected.
Source: Brian's read of the week 8 build on 2026-11-03. The page is unpublished until these land.

## Problem Statement

Brian read the week 8 page and found five things. The odds punish an injured starter twice: the projection
is zero, and no replacement steps in. Joe Burrow earned both Top Scorer and Game Changer, and a rule gave him
one. The matchup recaps read as box scores, not as game stories: no injury, no score timing, no Monday night
turn. The blurbs are flat.

## Solution

1. **The odds replace an injured starter** (ticket 01). A starter with a zero projection because of an injury
   is replaced by the better of the best bench player and the best waiver player at that position. Any
   position.
2. **A player can win two awards** (ticket 02). Find the one-award-per-player rule and remove it. Joe Burrow
   wins Top Scorer and Game Changer in week 8.
3. **The game story data check** (ticket 03). Find out what the saved week 8 data holds: injuries and their
   status, the timing of scores within the week, and the Monday night result. Report what is there, what is
   not, and what one fetch would add. No code change.
4. **The matchup recap rework** (ticket 04). Each recap tells how the game was won, with the injury and the
   timing facts that ticket 03 found. Blocked by 03.
5. **Blurbs with more fun and more detail** (ticket 05). The chapter blurbs use the same facts and a looser
   voice, inside the tone rules. Blocked by 03.

## Decisions

- **This is a test of the One vision.** Each builder starts cold from `CLAUDE.md`, `docs/agents/state.md`,
  and the folder READMEs. Each close comment ends with the files-read line. A folder every ticket had to open
  is the next README or the next split.
- **Golden changes show in review.** Tickets 01 and 02 change the week 6 golden odds and awards. The close
  comment names the diff.
- **The week 8 page rebuilds from the saved data** with `page-json` where the change is in the sheet or the
  render, and with `make build WEEK=8` where the change needs the writer. Brian publishes.
- **No mock mode.** Tests use `FakeWriter`, `FixtureProvider`, and `httpx.MockTransport`.

## Out of Scope

- A new data source beyond what ticket 03 finds in one fetch.
- A site change.
