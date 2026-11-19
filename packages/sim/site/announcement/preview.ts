/**
 * The few numbers of the week sim file that the art of the sim Announcement needs. A server page builds them at build
 * time, so the home page ships about 1 KB and not the whole file.
 */
import type { WeekSim } from "../schema/sim-types";
import { nameOf } from "../page/format";

export type PreviewRow = { id: number; name: string; place: number; odds: number };

/* The data of the art. The table holds every team, because the browser picks Your team after the build. */
export type PreviewData = {
  // The standings at the start of the sim, first place first, each with the playoff odds of the team over all runs.
  table: PreviewRow[];
  spots: number;
  median: boolean;
  // The What-if odds of each team by roster id: it wins its game of the next week, and with the median game also beats
  // the median. Null with no regular week left, or when no run had that result.
  whatIf: Record<number, number | null>;
};

/* The table is in the order of the sim: the most wins, then the most points, then the lowest roster id. */
export function previewOf(sim: WeekSim): PreviewData {
  const table = Object.keys(sim.records)
    .map(Number)
    .sort((a, b) => {
      const [winsA, , pointsA] = sim.records[a];
      const [winsB, , pointsB] = sim.records[b];
      return winsB - winsA || pointsB - pointsA || a - b;
    })
    .map((id, index) => ({ id, name: nameOf(sim, id), place: index + 1, odds: sim.pages[id]?.playoff ?? sim.teams[id].playoff }));
  const whatIf = Object.fromEntries(
    Object.entries(sim.pages).map(([id, page]) => {
      const win = page.weeks[0]?.results.find((result) => result.game === "win" && result.median !== "below");
      return [Number(id), win?.playoff ?? null];
    }),
  );
  return { table, spots: sim.parameters.playoff_spots, median: sim.parameters.median_game, whatIf };
}
