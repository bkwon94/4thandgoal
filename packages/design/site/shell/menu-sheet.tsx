/**
 * The menu button of the top band and the sheet of pages that it opens, below the desktop tier on every page.
 * The sheet drops from under the band with one row per page, the week row, and "Past weeks". From the desktop tier the pill bar takes its place.
 */
"use client";

import {
  ArrowLeftRightIcon,
  CalendarDaysIcon,
  CheckIcon,
  ChevronDownIcon,
  DicesIcon,
  HouseIcon,
  MenuIcon,
  TrophyIcon,
  UsersIcon,
  WalletIcon,
  XIcon,
  type LucideIcon,
} from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";
import { Sheet, SheetBackdrop, SheetContent, SheetGrip, SheetTitle, SheetTrigger } from "../ui/sheet";
import { weekChipLabel, type NavItem, type NavKind, type WeekLink } from "./nav";

type SheetKind = Exclude<NavKind, "midseason">;

/* The icon of each kind of destination. The name in the row names the item, so each icon is decorative. */
export const ICONS: Record<Exclude<NavKind, "midseason">, LucideIcon> = {
  home: HouseIcon,
  week: CalendarDaysIcon,
  rankings: TrophyIcon,
  managers: UsersIcon,
  analyzer: ArrowLeftRightIcon,
  waiver: WalletIcon,
  sim: DicesIcon,
};

/* The desktop tier, the same breakpoint as the desktop variant, --breakpoint-desktop in globals.css. */
const DESKTOP = "(min-width: 64rem)";

/* The note under the name of each page. The name says what the page is, and the note says what a manager does there. */
const NOTES: Record<SheetKind, string> = {
  home: "Ask about your team",
  week: "Scores and recaps",
  rankings: "The league, ranked",
  managers: "Grades and records",
  analyzer: "Check a trade",
  waiver: "Adds worth a claim",
  sim: "Your path to the playoffs",
};

type MenuSheetProps = {
  items: NavItem[];
  // The published weeks, newest first.
  weeks: WeekLink[];
  // The href of the item to mark, from currentHref.
  current?: string;
  // The href of the open page.
  pageHref?: string;
};

/* The sheet drops from the top edge, rests at the height of its rows, and moves on the default iOS spring of the
   Drawer, with no tune (decision 08). Under reduced motion the Drawer fades it and does not slide it (ADR 0034). */
export function MenuSheet({ items: all, weeks, current, pageHref }: MenuSheetProps) {
  const items = all.filter((item): item is NavItem & { kind: SheetKind } => item.kind !== "midseason");
  const [open, setOpen] = useState(false);
  const [pastOpen, setPastOpen] = useState(false);
  const button = useRef<HTMLButtonElement>(null);
  const sheet = useRef<HTMLDivElement>(null);

  // The desktop tier hides the sheet and its button. A modal sheet left open there keeps the page inert under a hidden
  // sheet, with no way out, so the sheet closes once the window reaches the desktop tier.
  useEffect(() => {
    if (!open) return;
    const desktop = window.matchMedia(DESKTOP);
    const closeOnDesktop = () => {
      if (desktop.matches) setOpen(false);
    };
    closeOnDesktop();
    desktop.addEventListener("change", closeOnDesktop);
    return () => desktop.removeEventListener("change", closeOnDesktop);
  }, [open]);

  // The Drawer springs a sheet to each new height of its content. On a sheet from the top that spring moves the top edge
  // up by the growth and back down, so the top edge jumps while "Past weeks" opens or closes. Each later resize of the
  // open sheet ends that spring at once, so the top edge stays still and only the bottom edge follows the list. The
  // first call of the observer is its measure on open, which must not end the drop of the sheet, and a drag keeps its
  // own motion.
  useEffect(() => {
    const el = sheet.current;
    if (!open || !el) return;
    let first = true;
    const observer = new ResizeObserver(() => {
      if (first) {
        first = false;
        return;
      }
      if (el.hasAttribute("data-dragging")) return;
      for (const motion of el.getAnimations()) {
        const frames = (motion.effect as KeyframeEffect | null)?.getKeyframes() ?? [];
        if (frames.some((frame) => "translate" in frame)) motion.finish();
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [open]);

  // The modal sheet makes the page inert. The band stays usable, so its X closes the sheet.
  const band = () => {
    const header = button.current?.closest("header");
    return header ? [header] : [];
  };

  const week = items.find((item) => item.kind === "week");
  // The week row opens the newest week, so "Past weeks" holds only the older weeks.
  const past = weeks.slice(1);
  // The container moves the dim and the sheet out of the band to the body. In place they sit inside the band, and the
  // Drawer then takes a tap on the dim as a tap on the persistent band, so the tap does not close the sheet. The dim and
  // the sheet render only once open, in the browser, so the server never reads document.
  return (
    <Sheet
      side="top"
      open={open}
      onOpenChange={setOpen}
      persistentElements={band}
      container={typeof document === "undefined" ? undefined : document.body}
    >
      {/* The X takes the place of the icon of the menu, in the same spot, so the way out sits under the thumb that opened it.
          The negative margin lines the icon up with the edge. */}
      <SheetTrigger
        ref={button}
        aria-expanded={open}
        aria-label={open ? "Close the menu" : "Open the menu"}
        className="press -mr-sp-3 flex size-touch flex-none items-center justify-center text-ink hover-fine:text-accent-ink desktop:hidden [@media(scripting:none)]:hidden"
      >
        <span aria-hidden data-open={open || undefined} className="menu-icon">
          <MenuIcon className="size-sp-5" />
          <XIcon className="size-sp-5" />
        </span>
      </SheetTrigger>
      {/* The page under the band dims while the sheet is open, and a tap on it closes the sheet. */}
      <SheetBackdrop data-testid="menu-scrim" data-menu-sheet="" className="desktop:hidden" />
      {/* data-menu-sheet lets globals.css move the top edge of the sheet and the dim to the bottom of the band, so the
          band stays on top. */}
      <SheetContent
        ref={sheet}
        data-menu-sheet=""
        className="flex w-full flex-col desktop:hidden"
      >
        <SheetTitle className="sr-only">Pages</SheetTitle>
        <nav aria-label="Pages">
          <ul className="mx-auto m-0 flex max-w-band list-none flex-col gap-sp-1 px-gutter pt-sp-2 pb-sp-1">
            {items.map((item) => {
              const Icon = ICONS[item.kind];
              const here = item.href === current;
              return (
                <li key={item.href}>
                  <a
                    href={item.href}
                    aria-current={here ? "page" : undefined}
                    className="press flex min-h-dock items-center gap-sp-3 rounded-tile px-sp-2 text-ink no-underline hover-fine:bg-raised aria-[current=page]:bg-raised"
                  >
                    <span aria-hidden className="flex size-touch flex-none items-center justify-center rounded-tile bg-raised text-ink-2">
                      <Icon className="size-sp-5" />
                    </span>
                    <span className="flex min-w-0 flex-auto flex-col">
                      <span className="truncate text-body leading-tight font-semibold">{item.label}</span>
                      <span className="truncate text-meta leading-tight text-mute">{NOTES[item.kind]}</span>
                    </span>
                    {here && <CheckIcon aria-hidden data-check="" className="size-sp-5 flex-none text-accent-ink" strokeWidth={2.5} />}
                  </a>
                  {item === week && past.length > 0 && (
                    <PastWeeks weeks={past} pageHref={pageHref} open={pastOpen} onToggle={() => setPastOpen((was) => !was)} />
                  )}
                </li>
              );
            })}
          </ul>
        </nav>
        {/* The grip at the bottom edge shows that the sheet drags. */}
        <SheetGrip className="mb-sp-2" />
      </SheetContent>
    </Sheet>
  );
}

type PastWeeksProps = { weeks: WeekLink[]; pageHref?: string; open: boolean; onToggle: () => void };

/* "Past weeks" under the week row, and the chips of each week older than the newest that it opens, newest first. The list grows on the
   grid rows, so it pushes the rows under it down and never covers them. */
function PastWeeks({ weeks, pageHref, open, onToggle }: PastWeeksProps) {
  const id = useId();
  return (
    <div className="pl-[calc(var(--spacing-touch)+var(--spacing-sp-5))]">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={id}
        onClick={onToggle}
        className="press flex min-h-touch items-center gap-sp-1 text-meta font-semibold text-ink-2 hover-fine:text-ink"
      >
        Past weeks
        <ChevronDownIcon aria-hidden data-open={open || undefined} className="menu-chevron size-sp-4" />
      </button>
      {/* The pad sits on the inner list, never on the grid track, so the closed track has no height left. */}
      <div id={id} data-open={open || undefined} aria-hidden={!open || undefined} inert={!open} className="menu-past">
        <div className="min-h-0 overflow-hidden">
          <ul aria-label="Past weeks" className="m-0 flex list-none flex-wrap gap-sp-2 p-0 pb-sp-2">
          {weeks.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                aria-current={link.href === pageHref ? "page" : undefined}
                className="press flex min-h-touch min-w-touch items-center justify-center rounded-pill border border-rule bg-card px-sp-4 font-mono text-meta font-bold tracking-caps text-ink no-underline aria-[current=page]:border-accent"
              >
                {weekChipLabel(link.number)}
              </a>
            </li>
          ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
