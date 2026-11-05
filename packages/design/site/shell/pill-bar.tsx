/**
 * The pill bar: the destinations of the menu with their full labels, in the top band from the desktop tier up.
 * The open destination is marked. Below the desktop tier the dock takes its place.
 */
import { cn } from "../lib/utils";
import type { NavItem } from "./nav";

type PillBarProps = {
  items: NavItem[];
  // The href of the item to mark, from currentHref.
  current?: string;
  // The place of the bar in the top band.
  className?: string;
};

export function PillBar({ items, current, className }: PillBarProps) {
  return (
    // A long list scrolls inside the bar, so the page never scrolls sideways.
    <nav aria-label="Site menu" className={cn("hidden items-center gap-sp-1 overflow-x-auto desktop:flex", className)}>
      {items.map((item) => (
        // A plain anchor, so the static export moves with scripts off and with no client router.
        // The raised fill marks the open destination, so the mark is not color alone: the pill has a shape.
        <a
          key={item.href}
          href={item.href}
          aria-current={item.href === current ? "page" : undefined}
          className="press inline-flex min-h-touch flex-none items-center rounded-pill px-sp-4 text-meta font-semibold whitespace-nowrap text-ink-2 no-underline hover-fine:text-ink aria-[current=page]:bg-raised aria-[current=page]:text-ink"
        >
          {item.label}
        </a>
      ))}
    </nav>
  );
}
