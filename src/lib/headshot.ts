/**
 * The default headshot, the image error handler that swaps to it, the Sleeper CDN headshot URL, and headshotSrc, the lookup of a headshot by player id.
 * The player picker, the analyzer result, and the waiver list share them, so a missing CDN image looks the same in all.
 */
import type { SyntheticEvent } from "react";
import { basePath } from "@/lib/config";
import type { HeadshotMap } from "@/lib/week-types";

export const HEADSHOT_FALLBACK = `${basePath}/images/headshot-default.svg`;

/* A headshot the CDN does not have swaps to the default once. The guard stops a loop if that file fails too. */
export function swapToDefault(event: SyntheticEvent<HTMLImageElement>) {
  const img = event.currentTarget;
  if (img.dataset.fallback) return;
  img.dataset.fallback = "1";
  img.src = HEADSHOT_FALLBACK;
}

/* The Sleeper CDN headshot of a player, by player id. It is the same URL the pipeline downloads from. */
export function sleeperHeadshot(playerId: string): string {
  return `https://sleepercdn.com/content/nfl/players/${playerId}.jpg`;
}

/* The week chapters read a headshot from the map of the week. A player with no entry in the map gets the default headshot. */
export function headshotSrc(headshots: HeadshotMap, playerId: string): string {
  return headshots[playerId] ?? HEADSHOT_FALLBACK;
}
