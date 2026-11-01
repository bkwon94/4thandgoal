/**
 * The default team avatar and the image error handler that swaps to it.
 * The team pickers share them, so a missing avatar looks the same in each.
 */
import type { SyntheticEvent } from "react";
import { basePath } from "@/lib/config";
import type { AvatarMap } from "@/lib/week-types";

export const AVATAR_FALLBACK = `${basePath}/images/avatar-default.svg`;

/* An avatar that fails to load swaps to the default once. The guard stops a loop if that file fails too. */
export function swapAvatarToDefault(event: SyntheticEvent<HTMLImageElement>) {
  const img = event.currentTarget;
  if (img.dataset.fallback) return;
  img.dataset.fallback = "1";
  img.src = AVATAR_FALLBACK;
}

/* The JSON paths are relative to the week folder. The route ends in a slash, so the browser resolves them as given. */
export function avatarSrc(avatars: AvatarMap, rosterId: number): string {
  return avatars[String(rosterId)] ?? AVATAR_FALLBACK;
}
