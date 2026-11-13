# 03: The rankings table per tier

**What to build:** A league member on a tablet or a laptop opens the power rankings and sees the ten columns of the table spaced with wide tokens and a wider gap, as the standings of the report are, so the numbers sit apart. The tablet values sit between the phone and the desktop values. The team column holds the avatar, its gap, and the longest word of any team name at each tier, so no row grows taller than the others. The headers stay "Stand", "Form", "Sched", and "Pts". The method note and the odds note cap at the measure. The label reads "Power Rankings" as a level-two heading, in the table and in the empty state. The week chips, the open row, and the hash link work as today. On a phone the table is unchanged, with the 480px tier that unfolds the columns.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Wide tokens for the rankings columns from the tablet tier sit next to the standings wide tokens, with a comment that gives the width the team track needs for the longest word beside the avatar at each tier.
- [x] The column gap widens from the tablet tier. The phone grid and the 480px page tier are unchanged.
- [x] No row grows taller than the others at 640px or 720px with the longest team name in the file.
- [x] The headers stay short at every tier.
- [x] The method note and the odds note take the measure.
- [x] The label is a level-two heading that reads "Power Rankings", in the table and in the empty state.
- [x] The rankings page test checks the "Power Rankings" heading with weeks and in the empty state, and the week line that follows the chips. Tests that read "Power rankings" change with the casing.
- [x] A browser check at 768 and 1280 shows the spaced columns and the longest name on one row height. At 390 the table is unchanged.
- [x] `pnpm test`, `pnpm typecheck`, and `pnpm build` pass.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 442e8d58.
Proof: The commits 442e8d58 and 4bae5201 merged in ba2fb98a; the site redesign 0a8b8868 replaced the table with the Ladder later.
Read 1 file: .scratch/todoist-queue/audit.md.
