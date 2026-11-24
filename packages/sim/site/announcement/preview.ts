/**
 * The few numbers of the week sim file that the art of The Race Announcement needs: the League board for a playoff spot.
 * A server page builds them at build time, so the home page ships about 1 KB and not the whole file.
 */
import type { BoardTeam, WeekSim } from "../schema/sim-types";
import { nameOf } from "../page/format";
import { boardOdds, boardOrder } from "../page/goals";

/* One row of the board: the team, its record, its odds of a playoff spot, and its pill, or null for a team in the hunt. */
export type PreviewRow = {
  id: number;
  name: string;
  record: [number, number];
  odds: number;
  pill: string | null;
};

/* The data of the art. The rows hold every team, because the browser picks Your team after the build. */
export type PreviewData = { rows: PreviewRow[] };

/* The pill of a board team by the plain check on wins: the best Goal locked, in the order 1 seed, bye, spot, then Out. A
   team in the hunt shows no pill, as on the League board (decision 04). */
function pillOf(team: BoardTeam): string | null {
  const status = (goal: string) => team.goals[goal]?.status;
  if (status("seed-1") === "in") return "Clinched 1 seed";
  if (status("bye") === "in") return "Clinched bye";
  if (status("spot") === "in") return "Clinched spot";
  if (status("spot") === "out") return "Out";
  return null;
}

/* The rows are in the order of the League board for a playoff spot: the odds, then the standings. */
export function previewOf(sim: WeekSim): PreviewData {
  const rows = boardOrder(sim, "spot").map((team) => {
    const [wins, losses] = sim.records[team.roster_id] ?? [0, 0];
    return {
      id: team.roster_id,
      name: nameOf(sim, team.roster_id),
      record: [wins, losses] as [number, number],
      odds: boardOdds(team, "spot"),
      pill: pillOf(team),
    };
  });
  return { rows };
}
