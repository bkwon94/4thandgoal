# 06: Two chapters fell to templates in the week 7 rebuild

Seen on 2026-10-28 in the local `make build WEEK=7` for this feature. Not caused by the bye facts.

**What happened:** The recap of game 6 failed both writer attempts. Attempt 1 claimed Pukancun on 3 is in
last place, and no fact says the league has 12 teams. Attempt 2 said the losing side's recent adds "went
nowhere" while the move facts show three of them beat their projections. The rankings chapter failed
attempt 1 with a code check, "[7] player Brenton Strange is not on a team in this chapter", and attempt 2
on one unsupported claim about schedule played. Both chapters shipped as templates in the local build.

**What to look at:** Whether a fact should state the count of teams, so "last place" is citable. Whether
the writer brief for the rankings chapter should list the players in scope, so a name outside it never
appears. Whether two attempts is enough for the rankings chapter, which writes 12 to 36 sentences.

**Blocked by:** None.

**Status:** wontfix

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12. Brian dropped it, because it fixes no real bug and changes nothing that a manager sees.
Proof: No team-count fact and no players-in-scope brief exist, and `facts/writer.py` still allows two attempts; no later spec names the issue, so it may no longer matter.
Read 1 file: .scratch/todoist-queue/audit.md.
