/**
 * The text formats of the waiver page: the team name, the meta line, the price, the trending line, the stance, and the drop line.
 * The field, the sheet, and the list share them, so a player reads the same in all three.
 */
import { num, thousands } from "@/lib/format/format";
import type { ClaimStance, DropInfo, WaiverPlayer } from "@/lib/waiver-types";
import type { Team } from "@/lib/week-types";

/* The team name of a roster, or the roster number when the week page has no such team. */
export function teamName(teams: Record<string, Team>, rosterId: number): string {
  return teams[String(rosterId)]?.name ?? `Roster ${rosterId}`;
}

/* The position, the team, the bye, the injury status, and the return week, each only when the file has it. */
export function metaLine(player: WaiverPlayer): string {
  const parts = [player.position, player.team];
  if (player.bye != null) parts.push(`Bye ${player.bye}`);
  if (player.injury_status) parts.push(player.injury_status);
  if (player.return_week != null) parts.push(`Back week ${player.return_week}`);
  return parts.join(" · ");
}

/* The price of a pool player, or null for a drop, which has no price. */
export function priceText(player: WaiverPlayer): string | null {
  return player.price ? `$${player.price.bid}` : null;
}

/* The trending count with a thousands separator, or null when he is not in the trending file. */
export function trendingLine(player: WaiverPlayer): string | null {
  const count = player.trending_count ?? 0;
  return count > 0 ? `${thousands(count)} adds on Sleeper in the last day` : null;
}

/* The words for each stance. The record type makes the compiler ask for a label when the pipeline adds a stance. */
export const STANCE: Record<ClaimStance, string> = {
  backs: "Backs the board",
  disputes: "Disputes the board",
  news: "News",
};

/* The roster that holds a drop. */
export function holderLine(drop: DropInfo): string {
  return `On ${drop.holder}`;
}

/* The pool player who beats a drop, and by how much a week. */
export function beatenLine(drop: DropInfo): string {
  return `${drop.beaten_by_name} projects ${num(drop.margin)} a week higher`;
}
