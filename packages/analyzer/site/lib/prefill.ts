/**
 * The prefill of the trade form from the query of the Trade page, such as /analyze/?team=3&with=6&give=5045&get=8151.
 * The front door links here when it is not sure of each player of a typed trade, and fills only the sure ones.
 */
import { EMPTY_SIDES, type Sides } from "./trade";

/* The trade of a link: Your team, the partner or null, the players that Your team gives, and the players it gets. */
export type Prefill = { team: number; partner: number | null; gives: string[]; gets: string[] };

const ids = (value: string | null) => (value ? value.split(",").filter(Boolean) : []);

/* The query of a prefill, with no key for a part that is empty. */
export function prefillQuery({ team, partner, gives, gets }: Prefill): string {
  const query = new URLSearchParams({ team: String(team) });
  if (partner !== null) query.set("with", String(partner));
  if (gives.length > 0) query.set("give", gives.join(","));
  if (gets.length > 0) query.set("get", gets.join(","));
  return `?${query.toString()}`;
}

/* The prefill of a query, or null when it names no team. A bad number reads as no team. */
export function readPrefill(search: string): Prefill | null {
  const query = new URLSearchParams(search);
  const team = Number(query.get("team"));
  if (!Number.isInteger(team) || team <= 0) return null;
  const partner = Number(query.get("with"));
  return {
    team,
    partner: Number.isInteger(partner) && partner > 0 && partner !== team ? partner : null,
    gives: ids(query.get("give")),
    gets: ids(query.get("get")),
  };
}

/* The sides of the form for a prefill. Your team gets each player of the partner side, and the partner side gets each
   player that Your team gives, so the cards show the trade as the question named it. */
export function prefillSides({ team, partner, gives, gets }: Prefill): Sides {
  const [mine, theirs] = EMPTY_SIDES;
  return [
    { id: mine.id, rosterId: team, gets: gets.map((playerId) => ({ playerId, fromSide: theirs.id })) },
    { id: theirs.id, rosterId: partner, gets: gives.map((playerId) => ({ playerId, fromSide: mine.id })) },
  ];
}
