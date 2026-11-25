/**
 * The few numbers of the week sim file that the art of The Race Announcement needs: the League board for a playoff spot.
 * A server page builds them at build time, so the home page ships about 1 KB and not the whole file.
 */
import type { WeekSim } from "../schema/sim-types";
import { nameOf } from "../page/format";
import { boardOdds, boardOrder, pillOf } from "../page/goals";

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

/* The rows are in the order of the League board for a playoff spot: the odds, then the standings. */
export function previewOf(sim: WeekSim): PreviewData {
  const rows = boardOrder(sim, "spot").map((team) => {
    const [wins, losses] = sim.records[team.roster_id] ?? [0, 0];
    return {
      id: team.roster_id,
      name: nameOf(sim, team.roster_id),
      record: [wins, losses] as [number, number],
      odds: boardOdds(team, "spot"),
      // The pill of the League board for a spot: the best Goal locked, or Out. A team in the hunt shows none (decision 04).
      pill: pillOf(team, "spot")?.label ?? null,
    };
  });
  return { rows };
}
