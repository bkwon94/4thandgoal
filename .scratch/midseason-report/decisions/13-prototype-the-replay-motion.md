# 13: How does the replay of the sim move?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** prototype

**Blocked by:** 08

**Status:** done

## Question

Ticket 08 chose a replay. Brian wants the redesign look to feel clean and futuristic, with strong motion. The spec needs the motion of four beats:

1. The transition from the regular season to the playoffs.
2. The bracket builds from the final standings.
3. Each winner of a playoff game gets an animation.
4. The champion gets a big champion animation.

The prototype also sets the speed of a full run, a way to skip to the end, and the reduced-motion version. It starts from variant A of ticket 08, in the throwaway worktree `.claude/worktrees/sim-prototype`. Delete that worktree when this ticket is done.

## Decision

Brian decided it on 2026-11-05, after three motion variants on real CPC week 8 data: Broadcast, Table to bracket, and Futuristic display. He chose Broadcast. Futuristic display was strong, but it differs too much from the rest of the redesign. Nothing from the other two variants carries over.

The motion of Broadcast, beat by beat:

1. **Regular season, weeks 9 to 14.** Each week a lower third wipes in, for example "WEEK 11 FINAL" with the median, over a crawl of the scores. The standings rows reorder on a spring. An up or down arrow shows each change of place. Only the red plate of the lower third scales; its text fades in, so the text never stretches.
2. **The split.** A red PLAYOFFS band wipes across the full width, holds, and wipes off. Behind it, the cut line draws under seed 6, BYE plates slide in for seeds 1 and 2, and seeds 7 to 12 dim.
3. **The bracket builds.** The game cards slide in from the left, one round at a time, and the bracket lines draw. The rounds are Round 1, the semifinal, and the final, with the week number small beside each.
4. **Each winner.** The scores count up. A red bar sweeps under the winner. The bracket line lights red, and the winner chip slides along it into its next slot.
5. **The champion.** The card shows above the complete bracket, inside the stage. The avatar scales up on a spring, the trophy drops in, and rays and a ring burst once. The card says "Champion of this run", the team name, and "Wins the title in N% of all 10,000 runs". The card first filled the stage and hid the bracket. Brian changed this on 2026-11-05 for AT-34, so the final state shows the bracket and the card together.

Rules for all beats:

- A full run takes about 20 seconds. A "Skip to the end" control jumps to the final state at once. A press of the main button during a run starts a fresh run cleanly.
- The odds of all 10,000 runs sit below the stage at every width, with a column for the seed of this run. Brian changed this on 2026-11-05: beside the stage, the bracket had only about 356 px on a desktop, and the team names did not fit.
- The week strip has two labeled groups, the regular season and the playoffs, with a gap and a different style.
- The motion reuses the redesign's `framer-motion`, its ease tokens, and its brand red. It adds no dependency. The trophy is from `lucide-react`.
- Spring bounce stays at 0.3 or less. A step of a beat may run 0.4 to 0.8 seconds, past the 300 ms limit for controls, because the replay explains and the reader watches it.
- With reduced motion, each beat keeps its timeline and shows as a fade or an instant change, with no movement, crawl, burst, or count-up.
- The stage keeps a fixed minimum height, so the page does not jump when the table becomes the bracket.

The prototype also showed: the order of the stored runs depends only on the count of presses, so the first press always plays the same run. The spec decides if the first run is fixed or random.
