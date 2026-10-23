# 02: Usage and environment

Spec: `.scratch/waiver/PRD.md`.

**What to build:** The best adds bucket is led by usage, not by projection. A player whose snap share
and target or carry share rose over the last two weeks ranks above a player with a higher projection
and flat usage. Each player carries a usage fact with numbers, "played 71% of snaps and took 5
targets last week, up from 48% and 2", and an environment fact, "runs the 3rd fastest offense and
passes on 61% of neutral downs". Every digit in a fact's text is in its numbers.

The nflverse module reads per-player per-week usage from the play by play and the FTN charting:
offensive snaps, snap share, targets, target share, carries, red zone touches, and routes where the
charting has them. It reads per-team per-week environment: plays per game, neutral pass rate, pass
rate, and rush success rate. Both use the existing cache and max age. The board engine takes the
usage and environment and gives each player the three scores with `BOARD_WEIGHTS`, usage 0.5,
environment 0.3, projection 0.2, scaled by position as the spec says.

**Blocked by:** 01 The week file, thin.

**Status:** ready-for-agent

- [ ] The nflverse reader returns usage per player per week and environment per team per week from a small play by play fixture.
- [ ] A player with a rising snap share and a flat projection outranks a player with a higher projection and flat usage.
- [ ] A QB, WR, or TE environment score uses plays per game and neutral pass rate; an RB uses rush success and plays per game.
- [ ] Every player in the file carries a usage fact and an environment fact, with every digit in the numbers.
- [ ] A player with no usage rows, a rookie in week 1 or a player on a bye, gets a usage score of 0 and no usage fact, and the build does not stop.
- [ ] The weights and `USAGE_WEEKS` are tunables.
