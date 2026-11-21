/**
 * The words of the Sim tile of the week page, from one week sim file: one tile for each team, and the league fact.
 * The build runs it, so the week page passes the browser only these few lines and not the whole file.
 */
import { nameOf, oddsText, roundName, winText } from "../page/format";
import type { SimPage, WeekSim } from "../schema/sim-types";

/* The tile of one team: the label of its number, the number, and one line under it. */
export type TeamTile = { label: string; odds: string; line: string };

/* The tiles of a week. A null tile means the tile shows the league fact: a team out of the playoffs, or any team after
   the final, because the fact then names the champion (decision 06). */
export type SimTileData = { fact: string | null; teams: Record<number, TeamTile | null> };

/* The line under the title odds of a team still in: its game of the round, its bye, or its seed. */
function playoffLine(sim: WeekSim, page: SimPage): string {
  const playoffs = page.playoffs!;
  if (playoffs.game !== null) {
    const index = playoffs.rounds.findIndex((round) => round.week === playoffs.game!.week);
    const vs = `Week ${playoffs.game.week} vs ${nameOf(sim, playoffs.game.opponent)}.`;
    return `${vs} ${winText(index, playoffs.rounds.length)}`;
  }
  if (playoffs.bye && playoffs.week !== null)
    return `Seed ${playoffs.seed}, a bye in week ${playoffs.week}.`;
  return `Seed ${playoffs.seed}, in the ${roundName(0, playoffs.rounds.length).toLowerCase()}.`;
}

/* The tile of one team. In the regular season it is the playoff odds and the sentence of more wins of the build. */
function teamTile(sim: WeekSim, page: SimPage): TeamTile | null {
  const playoffs = page.playoffs;
  if (playoffs === null)
    return { label: "Playoff odds", odds: oddsText(page.playoff), line: page.sentence };
  if (playoffs.champion !== null || !playoffs.alive) return null;
  return { label: "Title odds", odds: oddsText(playoffs.title), line: playoffLine(sim, page) };
}

export function simTileOf(sim: WeekSim): SimTileData {
  const teams = Object.fromEntries(
    Object.values(sim.pages).map((page) => [page.you, teamTile(sim, page)]),
  );
  return { fact: sim.fact, teams };
}
