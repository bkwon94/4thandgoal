/**
 * The trade of the Stack: each side, its team, and the players it gets, each with the side it comes from.
 * It builds the body of POST /analyze from the picks, so the body keeps the shape of ADR 0008.
 */
import type { AnalyzeRequest, Team } from "./api";

/* A player that a side gets, and the id of the side that gives him. fromSide is the id of a side, not its roster,
   so the source holds when that side changes its team. */
export type Get = { playerId: string; fromSide: number };

/* One side of the trade: a stable id, the picked roster, and the players it gets. The id keys the side, so a remove
   keeps the state and the motion of the sides after it. */
export type Side = { id: number; rosterId: number | null; gets: Get[] };

/* The sides of a trade in order. The first side is the asker, "Your Team". */
export type Sides = Side[];

/* The heading of each side, by its place in the order. */
export const SIDE_TITLES = ["Your Team", "Team Two", "Team Three", "Team Four"];

/* The analyze route grades two to four sides. */
export const MAX_SIDES = 4;

export const EMPTY_SIDES: Sides = [
  { id: 0, rosterId: null, gets: [] },
  { id: 1, rosterId: null, gets: [] },
];

/* The team of a roster id, or undefined before a pick. */
export function teamOf(teams: Team[], rosterId: number | null): Team | undefined {
  return teams.find((t) => t.roster_id === rosterId);
}

/* Every side has a team, gets at least one player, and gives at least one player. The grade bar reads it. */
export function everySideTrades(sides: Sides): boolean {
  return sides.every(
    (side) =>
      side.rosterId !== null &&
      side.gets.length > 0 &&
      sides.some((other) => other !== side && other.gets.some((get) => get.fromSide === side.id)),
  );
}

/* The body of POST /analyze, or null until each side has a team. Each pick is a give of its source side, with to set
   to the roster of the side that gets it. The gives of a side keep the order of the cards, then the order of the picks. */
export function analyzeRequest(sides: Sides, season: number): AnalyzeRequest | null {
  if (sides.some((side) => side.rosterId === null)) return null;
  return {
    season,
    asker: sides[0].rosterId!,
    sides: sides.map((side) => ({
      roster_id: side.rosterId!,
      gives: sides.flatMap((card) =>
        card.gets.filter((get) => get.fromSide === side.id).map((get) => ({ player_id: get.playerId, to: card.rosterId! })),
      ),
    })),
  };
}

/* Drops each get whose player is not on the current roster of its source team. A fresh roster can lose a player
   after a trade. It returns the same array when nothing drops, so React skips the render. */
export function dropStaleGets(sides: Sides, teams: Team[]): Sides {
  const rosterOf = (sideId: number) => {
    const team = teamOf(teams, sides.find((side) => side.id === sideId)?.rosterId ?? null);
    return new Set(team?.players.map((p) => p.player_id) ?? []);
  };
  let changed = false;
  const next = sides.map((side) => {
    const known = side.rosterId === null || teamOf(teams, side.rosterId) !== undefined;
    const gets = side.gets.filter((get) => rosterOf(get.fromSide).has(get.playerId));
    if (known && gets.length === side.gets.length) return side;
    changed = true;
    return { ...side, rosterId: known ? side.rosterId : null, gets };
  });
  return changed ? next : sides;
}
