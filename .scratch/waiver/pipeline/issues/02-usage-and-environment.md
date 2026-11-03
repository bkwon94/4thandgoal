# 02: Usage and environment

Spec: `.scratch/waiver/pipeline/PRD.md`.

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

**Status:** done

- [x] The nflverse reader returns usage per player per week and environment per team per week from a small play by play fixture.
- [x] A player with a rising snap share and a flat projection outranks a player with a higher projection and flat usage.
- [x] A QB, WR, or TE environment score uses plays per game and neutral pass rate; an RB uses rush success and plays per game.
- [x] Every player in the file carries a usage fact and an environment fact, with every digit in the numbers.
- [x] A player with no usage rows, a rookie in week 1 or a player on a bye, gets a usage score of 0 and no usage fact, and the build does not stop.
- [x] The weights and `USAGE_WEEKS` are tunables.

## Comments

2026-10-23, decisions the ticket left open:
- The snap share is real: the nflverse snap counts file joins on the PFR ID from the ffverse id map.
- The FTN charting has no routes column, so the usage has no routes.
- The usage trend compares week N with week N - `USAGE_WEEKS` + 1. A player with no row or no snap share in either week has no window: usage 0 and no usage fact.
- Only a rise scores. A flat or a falling usage scores 0, and the risers rank inside the position from 1 to 0.
- The touches that count are targets for a WR or a TE and carries for an RB or a QB.
- The environment uses the season to date. An RB's environment fact names the rush success, not the neutral pass rate.
- The extract saves `USAGE_SAVED_WEEKS` (4) weeks of usage for the drops bucket. The score reads the last `USAGE_WEEKS`.
- `nflverse_snaps` joins the sources that gate the save of the extract, so a failed snap fetch tries again on the next build.
- A partial game in week N-1, such as an injury exit, inflates the rise. A later ticket may use the last full game as the base.
