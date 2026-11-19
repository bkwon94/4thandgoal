/**
 * The small parts of the sim page: the bar of a percent, and the read of the tablet tier.
 * The bar takes a value and returns markup.
 */
import { useSyncExternalStore } from "react";
import { cn } from "@cpc/design/lib/utils";

/* The tablet tier, the same breakpoint as the tablet variant, --breakpoint-tablet in globals.css. */
const TABLET = "(min-width: 40rem)";

function onTierChange(change: () => void): () => void {
  const query = window.matchMedia(TABLET);
  query.addEventListener("change", change);
  return () => query.removeEventListener("change", change);
}

/* True from the tablet tier up. The static page and the first paint take the phone, and the CSS of each part shows the
   right tier before this reads the window. */
export function useTabletUp(): boolean {
  return useSyncExternalStore(onTierChange, () => window.matchMedia(TABLET).matches, () => false);
}

/* A thin bar that fills to its percent. The fill scales, so the bar keeps its width. */
export function Bar({ value, className }: { value: number | null; className?: string }) {
  return (
    <span aria-hidden className={cn("block h-sp-1 overflow-hidden rounded-pill bg-bar-off", className)}>
      <span
        className="block h-full origin-left rounded-pill bg-accent"
        style={{ transform: `scaleX(${Math.min(100, Math.max(0, value ?? 0)) / 100})` }}
      />
    </span>
  );
}
