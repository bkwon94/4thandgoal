/**
 * The dock: the destinations of the menu as icons with short labels, fixed at the bottom of the viewport on a phone and a tablet.
 * It stays on screen at every scroll. From the desktop tier up the pill bar of the top band takes its place.
 * The full labels of the pill bar do not fit on one row beside the brand at a tablet width, so the dock serves the tablet too.
 */
"use client";

import {
  ArrowLeftRightIcon,
  CalendarDaysIcon,
  HouseIcon,
  TrophyIcon,
  UsersIcon,
  WalletIcon,
  type LucideIcon,
} from "lucide-react";
import { useKeyboardOpen } from "./keyboard";
import type { NavItem, NavKind } from "./nav";

/* The icon of each kind of destination. The label under the icon names the item, so each icon is decorative.
   The header sheet uses the same icons, so a page has one icon in the dock and in the sheet. */
export const ICONS: Record<Exclude<NavKind, "midseason">, LucideIcon> = {
  home: HouseIcon,
  week: CalendarDaysIcon,
  rankings: TrophyIcon,
  managers: UsersIcon,
  analyzer: ArrowLeftRightIcon,
  waiver: WalletIcon,
};

type DockProps = {
  items: NavItem[];
  // The href of the item to mark, from currentHref.
  current?: string;
};

/* The dock holds five items, so the midseason report has no dock item. The pill bar lists it, and the home page links it. */
export function Dock({ items: all, current }: DockProps) {
  const items = all.filter((item): item is NavItem & { kind: Exclude<NavKind, "midseason"> } => item.kind !== "midseason");
  // While the on-screen keyboard is open, the dock tucks away, as the tab bar of a native app, so the field sits right
  // above the keyboard. The tucked dock is inert, so a tab or a screen reader never lands on it.
  const tucked = useKeyboardOpen();
  return (
    // The dock floats one step above the bottom edge and the safe area of the phone. The body keeps the same space free
    // under the page (globals.css), so the dock never covers the end of the page. On a phone on its side, each end
    // keeps clear of the notch.
    <nav
      aria-label="Bottom menu"
      data-tucked={tucked || undefined}
      inert={tucked}
      className="dock-tuck fixed right-[max(var(--spacing-sp-3),env(safe-area-inset-right))] left-[max(var(--spacing-sp-3),env(safe-area-inset-left))] bottom-[calc(var(--spacing-sp-3)+env(safe-area-inset-bottom))] z-40 rounded-card border border-rule bg-card p-sp-1 desktop:hidden"
    >
      <ul className="m-0 grid list-none auto-cols-fr grid-flow-col gap-sp-1 p-0">
        {items.map((item) => {
          const Icon = ICONS[item.kind];
          const open = item.href === current;
          return (
            <li key={item.href}>
              {/* The label is 12px, over the 11px floor of other text. The raised fill and the accent bar mark the open item,
                  so the mark is not color alone. */}
              <a
                href={item.href}
                aria-current={open ? "page" : undefined}
                className="press relative flex min-h-dock flex-col items-center justify-center gap-sp-1 rounded-tile text-meta leading-tight font-semibold text-mute no-underline aria-[current=page]:bg-raised aria-[current=page]:text-ink"
              >
                {open && <span aria-hidden className="absolute top-sp-1 h-sp-0 w-sp-4 rounded-pill bg-accent" />}
                <Icon aria-hidden className="size-sp-5" />
                <span className="whitespace-nowrap">{item.short}</span>
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
