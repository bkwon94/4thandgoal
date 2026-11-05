/**
 * The share bar of a game: the share of the points of the lead side, as a pill bar with a meter role.
 * The hero tone sits in the hero, and the page tone sits on a card.
 */
import { cn } from "@cpc/design/lib/utils";

/* The share of the first score in the total, in percent with one decimal: 100.31 and 98.88 give 50.4.
   A game with no points gives an even split, so the bar never divides by zero. */
export function shareOf(lead: number, other: number): number {
  const total = lead + other;
  return total > 0 ? Math.round((lead / total) * 1000) / 10 : 50;
}

/* The track of each tone. The fill is the accent in both, as a graphic, so it carries no text. */
const TRACKS = { hero: "bg-rule-dark", page: "bg-raised" } as const;

export function ShareBar({ share, tone }: { share: number; tone: keyof typeof TRACKS }) {
  return (
    <div
      role="meter"
      aria-label="Share of the points"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={share}
      className={cn("h-sp-1 overflow-hidden rounded-pill", TRACKS[tone])}
    >
      <div className="h-full rounded-pill bg-accent" style={{ width: `${share}%` }} />
    </div>
  );
}
