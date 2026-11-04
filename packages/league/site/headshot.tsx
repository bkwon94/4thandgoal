/**
 * The player headshot image, with the swap to the default headshot on an image error. It ports the .headshot rule of the source stylesheet.
 * It is decorative, because the player name always sits next to it. It is a client part, because a server component cannot pass the error handler to the image.
 * The module holds the default headshot, the error handler that swaps to it, the Sleeper CDN headshot URL, and headshotSrc, the lookup by player id.
 * The player picker, the analyzer result, and the waiver list share them, so a missing CDN image looks the same in all.
 */
"use client";

import type { SyntheticEvent } from "react";

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

/* A named size maps to a size class of the theme. A number sets the width and the height in pixels, for a size that comes from a layout table.
   With no size, the className carries the size. */
const SIZES = { avatar: "size-avatar" } as const;

/* The player name sits next to the headshot, so the image is decorative. A className sets the shape and the layout.
   A headshot below the fold passes lazy. The top story's cutout passes priority, so the browser fetches the biggest image of the first view first.
   A defense id has no CDN image, so the error swaps it to the default headshot.
   The size class comes first and the className follows. A plain join keeps each class list as the page had it, because cn can merge or drop a name it does not know. */
export function Headshot({
  src,
  size,
  lazy,
  priority,
  className,
}: {
  src: string;
  size?: keyof typeof SIZES | number;
  lazy?: boolean;
  priority?: boolean;
  className?: string;
}) {
  const named = typeof size === "string";
  const sized = typeof size === "number";
  return (
    <img
      src={src}
      alt=""
      loading={lazy ? "lazy" : undefined}
      fetchPriority={priority ? "high" : undefined}
      onError={swapToDefault}
      style={sized ? { width: size, height: size } : undefined}
      className={named ? [SIZES[size], className].filter(Boolean).join(" ") : className}
    />
  );
}
