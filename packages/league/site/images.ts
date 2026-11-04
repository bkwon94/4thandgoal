/**
 * The default avatar and headshot, the image error handlers that swap to them, the Sleeper CDN headshot URL, and the lookups by roster id and player id.
 * The module is no client module, so a server component calls the lookups. The pages share them, so a missing image looks the same in each.
 */
import type { SyntheticEvent } from "react";

// Each client serves at the root of its own domain, so the default image path has no base path.
export const AVATAR_FALLBACK = "/images/avatar-default.svg";

/* An avatar that fails to load swaps to the default once. The guard stops a loop if that file fails too. */
export function swapAvatarToDefault(event: SyntheticEvent<HTMLImageElement>) {
  const img = event.currentTarget;
  if (img.dataset.fallback) return;
  img.dataset.fallback = "1";
  img.src = AVATAR_FALLBACK;
}

/* The JSON paths are relative to the week folder. The route ends in a slash, so the browser resolves them as given. */
export function avatarSrc(avatars: Readonly<Record<string, string>>, rosterId: number): string {
  return avatars[String(rosterId)] ?? AVATAR_FALLBACK;
}

// Each client serves at the root of its own domain, so the default image path has no base path.
export const HEADSHOT_FALLBACK = "/images/headshot-default.svg";

/* A headshot the CDN does not have swaps to the default once. The guard stops a loop if that file fails too. */
export function swapToDefault(event: SyntheticEvent<HTMLImageElement>) {
  const img = event.currentTarget;
  if (img.dataset.fallback) return;
  img.dataset.fallback = "1";
  img.src = HEADSHOT_FALLBACK;
}

/* The Sleeper CDN headshot of a player, by player id. It is the same URL the pipeline downloads from.
   The Sleeper player ID is the canonical player ID of every package. */
export function sleeperHeadshot(playerId: string): string {
  return `https://sleepercdn.com/content/nfl/players/${playerId}.jpg`;
}

/* The week chapters read a headshot from the map of the week. A player with no entry in the map gets the default headshot. */
export function headshotSrc(headshots: Readonly<Record<string, string>>, playerId: string): string {
  return headshots[playerId] ?? HEADSHOT_FALLBACK;
}
