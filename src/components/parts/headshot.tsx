/**
 * The player headshot image, with the default headshot for a player the map lacks.
 * It is decorative, because the player name always sits next to it.
 */
import { HEADSHOT_FALLBACK } from "@/lib/headshot";
import type { HeadshotMap } from "@/lib/week-types";
import { cn } from "@/lib/utils";

/* The player name sits next to the headshot, so the image is decorative. A className sets the size, the shape, and the layout.
   A player with no entry in the map gets the default headshot. A headshot below the fold passes lazy.
   The top story's cutout passes priority, so the browser fetches the biggest image of the first view first. */
export function Headshot({
  playerId,
  headshots,
  lazy,
  priority,
  className,
}: {
  playerId: string;
  headshots: HeadshotMap;
  lazy?: boolean;
  priority?: boolean;
  className?: string;
}) {
  return (
    <img
      src={headshots[playerId] ?? HEADSHOT_FALLBACK}
      alt=""
      loading={lazy ? "lazy" : undefined}
      fetchPriority={priority ? "high" : undefined}
      className={cn("flex-none object-cover", className)}
    />
  );
}
