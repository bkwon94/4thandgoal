/**
 * The src of a headshot for the round photo frame, or null when the week has no headshot of the player.
 * The frame then shows the initials, so a missing headshot leaves no hole.
 */
import type { HeadshotMap } from "../schema/week-types";

/* The paths of the map are relative to the week folder. A defense has its team code as the id and no entry. */
export function photoOf(headshots: HeadshotMap, playerId: string): string | null {
  return headshots[playerId] ?? null;
}
