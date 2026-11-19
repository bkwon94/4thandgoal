/**
 * The week switch of the sim page: one item per regular week left, then Playoffs, with a pill that slides to the open item.
 * Under reduced motion the pill moves at once.
 */
"use client";

import { LayoutGroup, motion } from "framer-motion";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import { PRESS } from "./format";

export const PLAYOFFS = "playoffs" as const;
export type WeekItem = number | typeof PLAYOFFS;

/* The slide of the pill: the tabs of transitions-dev, on a spring with no bounce. */
const SLIDE = { type: "spring", bounce: 0, duration: 0.25 } as const;

export function WeekSwitch({ items, open, onOpen }: { items: WeekItem[]; open: WeekItem; onOpen: (item: WeekItem) => void }) {
  const off = useMotionOff();
  return (
    <nav aria-label="Weeks" className="w-full">
      <LayoutGroup id="sim-weeks">
        <ul className="m-0 flex list-none gap-sp-1 rounded-tile bg-card p-sp-1">
          {items.map((item) => {
            const on = item === open;
            return (
              <li key={String(item)} className={cn("min-w-0 flex-1", item === PLAYOFFS && "flex-[1.6]")}>
                <button
                  type="button"
                  aria-current={on ? "page" : undefined}
                  onClick={() => onOpen(item)}
                  className={cn(
                    PRESS,
                    "relative flex min-h-touch w-full items-center justify-center rounded-[14px] text-body font-bold",
                    on ? "text-page" : "text-mute hover-fine:text-ink",
                  )}
                >
                  {on && (
                    <motion.span
                      layoutId="sim-week-pill"
                      aria-hidden
                      className="absolute inset-0 rounded-[14px] bg-ink"
                      transition={off ? { duration: 0 } : SLIDE}
                    />
                  )}
                  <span className="relative tabular-nums">{item === PLAYOFFS ? "Playoffs" : `Wk ${item}`}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </LayoutGroup>
    </nav>
  );
}
