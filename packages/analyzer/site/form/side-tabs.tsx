/**
 * The switcher of the sides of a trade: one tab per team, with a pill that slides to the open tab, and one panel per tab.
 * The same switcher holds a 2-team and a 3-team trade at every width, so each trade size reads with one pattern.
 */
"use client";

import { useId, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { cn } from "@cpc/design/lib/utils";
import { openId } from "@cpc/design/lib/stable-id";

/* One tab: its key, the team name on the tab, and the panel it opens. */
export type SideTab = { key: string | number; label: string; panel: ReactNode };

/* The keys that move the open tab. The arrows wrap at each end, as the tab pattern of the ARIA guide says. */
function nextIndex(key: string, index: number, count: number): number | null {
  if (key === "ArrowRight") return (index + 1) % count;
  if (key === "ArrowLeft") return (index - 1 + count) % count;
  if (key === "Home") return 0;
  if (key === "End") return count - 1;
  return null;
}

/* The first tab opens first, so a caller puts the tab of the asker first.
   The tabs share the bar in equal columns, so the pill moves by its own width per step and needs no measure of a tab.
   A long team name wraps to two lines in its column, so a 3-team trade fits the phone width with no scroll.
   The pill slides with the brand ease-out in 250 ms, and the label color turns in step. Reduced motion moves both at once.
   Each panel stays in the page and a closed panel is hidden, so a screen reader and the egg hunt find every side. */
export function SideTabs({ label, tabs }: { label: string; tabs: SideTab[] }) {
  const [open, setOpen] = useState(0);
  const base = useId();
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  const count = tabs.length;

  const onKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    const next = nextIndex(event.key, open, count);
    if (next === null) return;
    event.preventDefault();
    setOpen(next);
    refs.current[next]?.focus();
  };

  return (
    <div className="flex flex-col gap-sp-4">
      <div
        role="tablist"
        aria-label={label}
        className="relative grid rounded-pill border border-rule bg-card p-sp-1"
        style={{ gridTemplateColumns: `repeat(${count}, minmax(0, 1fr))` }}
      >
        {/* The pill is one column wide, inside the padding of the bar. It is decorative, because aria-selected names the open tab. */}
        <span
          aria-hidden="true"
          className="pointer-events-none absolute inset-y-sp-1 left-sp-1 rounded-pill bg-accent transition-transform duration-250 ease-out motion-reduce:transition-none"
          style={{ width: `calc((100% - 2 * var(--spacing-sp-1)) / ${count})`, transform: `translateX(${open * 100}%)` }}
        />
        {tabs.map((tab, index) => {
          const selected = index === open;
          return (
            <button
              key={tab.key}
              ref={(el) => {
                refs.current[index] = el;
              }}
              type="button"
              role="tab"
              id={`${base}-tab-${index}`}
              aria-selected={selected}
              aria-controls={`${base}-panel-${index}`}
              tabIndex={selected ? 0 : -1}
              onClick={() => setOpen(index)}
              onKeyDown={onKeyDown}
              {...openId("side-tab", tab.key)}
              className={cn(
                "relative min-h-touch min-w-0 cursor-pointer rounded-pill px-sp-2 py-sp-1 text-meta leading-tight font-bold break-words text-balance transition-colors duration-250 ease-out motion-reduce:transition-none",
                "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
                selected ? "text-on-dark" : "text-ink hover:text-accent-ink",
              )}
            >
              <span className="line-clamp-2">{tab.label}</span>
            </button>
          );
        })}
      </div>
      {tabs.map((tab, index) => (
        <div
          key={tab.key}
          role="tabpanel"
          id={`${base}-panel-${index}`}
          aria-labelledby={`${base}-tab-${index}`}
          hidden={index !== open}
          tabIndex={0}
          className="focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent"
        >
          {tab.panel}
        </div>
      ))}
    </div>
  );
}
