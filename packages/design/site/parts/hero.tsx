/**
 * The hero: the one loud surface of a page, with the grid texture, the brand glow, the four corner brackets, and one scan line.
 * It sits on the band color in both themes, so the hero stays dark in light. The page passes its content.
 */
import type { ReactNode } from "react";
import { cn } from "../lib/utils";

type HeroProps = {
  // The name of the region, for a screen reader, such as "Page not found" or "Matchup of the Week".
  label: string;
  children: ReactNode;
  className?: string;
};

/* The four corner brackets. Each sits one step in from its corner, so no text sits on a bracket. */
const BRACKETS = [
  "top-sp-3 left-sp-3 border-t-2 border-l-2",
  "top-sp-3 right-sp-3 border-t-2 border-r-2",
  "bottom-sp-3 left-sp-3 border-b-2 border-l-2",
  "bottom-sp-3 right-sp-3 border-b-2 border-r-2",
];

/* The text of a hero sits on a plate of the band color (the plate utility of globals.css). The plate keeps the grid and
   the glow from under each letter, so the contrast of the text is the contrast of its role pair, and axe can read it.
   The art layer comes first in the markup and the content box is relative, so the content paints over the art. */
export function Hero({ label, children, className }: HeroProps) {
  return (
    <section
      aria-label={label}
      className={cn(
        "relative overflow-hidden rounded-hero border border-rule-dark bg-band px-hero-x py-hero-y text-on-dark",
        className,
      )}
    >
      <div aria-hidden="true">
        <div data-hero-art="texture" className="hero-texture pointer-events-none absolute inset-0" />
        <div data-hero-art="scan" className="hero-scan" />
        {BRACKETS.map((place) => (
          <span
            key={place}
            data-hero-art="bracket"
            className={`pointer-events-none absolute size-bracket border-on-dark-muted ${place}`}
          />
        ))}
      </div>
      <div className="relative">{children}</div>
    </section>
  );
}
