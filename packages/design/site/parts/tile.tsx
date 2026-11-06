/**
 * The tile: a small card with one number, its label above it, and an optional note under it.
 * The page tone sits on a card or the page. The hero tone sits in the hero, on the raised surface of the hero.
 */
import type { ReactNode } from "react";
import { cn } from "../lib/utils";

type TileProps = {
  label: string;
  // The one number of the tile, such as "151.32" or "+18.4". The page formats it.
  value: ReactNode;
  // A short line under the number, such as the team that scored it.
  note?: ReactNode;
  tone?: "page" | "hero";
  className?: string;
};

/* The colors of each tone. Each text role is a pair that brand-contrast.test.mjs holds at 4.5 to 1 on its surface. */
const TONES = {
  page: { box: "bg-raised text-ink", label: "text-mute", note: "text-ink-2" },
  hero: { box: "bg-chip-dark text-on-dark", label: "text-on-dark-muted", note: "text-on-dark-2" },
} as const;

export function Tile({ label, value, note, tone = "page", className }: TileProps) {
  const colors = TONES[tone];
  return (
    <div className={cn("rounded-tile p-sp-4", colors.box, className)}>
      {/* The label and the number are mono, so the numbers of a row of tiles line up. */}
      <div className={cn("font-mono text-meta leading-tight font-bold tracking-caps uppercase", colors.label)}>{label}</div>
      <div className="mt-sp-1 font-mono text-stat leading-stat font-bold tabular-nums">{value}</div>
      {note !== undefined && <div className={cn("mt-sp-1 text-meta leading-tight", colors.note)}>{note}</div>}
    </div>
  );
}
