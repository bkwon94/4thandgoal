/**
 * Pure helpers over the rankings types, safe to call from a server component.
 * They do no file reads, and the module is not a client module, so the static home page can call them at build time.
 */
import type { RankingsRow, RankingsWeek } from "@/lib/rankings-types";

/* The team with the largest movement up or down, for the home chapter. On a tie the higher ranked team wins,
   because the rows are in rank order and the scan keeps the first. A week with no movement has no mover. */
export function biggestMover(week: RankingsWeek): RankingsRow | null {
  let mover: RankingsRow | null = null;
  for (const row of week.rows) {
    const size = Math.abs(row.movement ?? 0);
    if (size > 0 && size > Math.abs(mover?.movement ?? 0)) mover = row;
  }
  return mover;
}
