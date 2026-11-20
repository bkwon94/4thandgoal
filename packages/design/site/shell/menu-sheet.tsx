/**
 * The menu button of the top band and the sheet of pages that it opens, below the desktop tier on every page.
 * The sheet drops from under the band with one row per page, the week row, and "Past weeks". From the desktop tier the pill bar takes its place.
 */
"use client";

import { PendingButton } from "../ui/pending-button";
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
import {
  createContext,
  useContext,
  useEffect,
  useId,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  Sheet,
  SheetBackdrop,
  SheetContent,
  SheetGrip,
  SheetTitle,
  SheetTrigger,
} from "../ui/sheet";
import { weekChipLabel, type NavItem, type NavKind, type WeekLink } from "./nav";

type SheetKind = Exclude<NavKind, "midseason">;

/* Closes the menu sheet, then runs `then` once the sheet finishes its exit. A part in the foot slot calls it, so a
   layer that it opens never starts under the sheet. Outside the menu sheet it is null. */
const CloseMenuSheet = createContext<((then: () => void) => void) | null>(null);

export function useCloseMenuSheet() {
  return useContext(CloseMenuSheet);
}

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
  // The rows of the open page under the rows of the pages. The app layer passes them, so the shell names no part of a page.
  foot?: ReactNode;
};

/* The sheet drops from the top edge, rests at the height of its rows, and moves on the default iOS spring of the
   Drawer, with no tune (decision 08). Under reduced motion the Drawer fades it and does not slide it (ADR 0034). */
export function MenuSheet({ items: all, weeks, current, pageHref, foot }: MenuSheetProps) {
  const items = all.filter(
    (item): item is NavItem & { kind: SheetKind } => item.kind !== "midseason",
  );
  const [open, setOpen] = useState(false);
  const [pastOpen, setPastOpen] = useState(false);
  const button = useRef<HTMLButtonElement>(null);
  const sheet = useRef<HTMLDivElement>(null);
  // The step that a foot row asks to run once the sheet is closed.
  const afterClose = useRef<(() => void) | null>(null);
  const closeThen = (then: () => void) => {
    afterClose.current = then;
    setOpen(false);
  };
  const closed = (isOpen: boolean) => {
    const then = afterClose.current;
    if (isOpen || !then) return;
    afterClose.current = null;
    then();
  };

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
      onOpenChangeComplete={closed}
      persistentElements={band}
      container={typeof document === "undefined" ? undefined : document.body}
    >
      {/* The X takes the place of the icon of the menu, in the same spot, so the way out sits under the thumb that opened it.
          The negative margin lines the icon up with the edge. */}
      <SheetTrigger
        ref={button}
        aria-expanded={open}
        aria-label={open ? "Close the menu" : "Open the menu"}
        className="press -mr-sp-3 size-touch text-ink hover-fine:text-accent-ink desktop:hidden flex flex-none items-center justify-center [@media(scripting:none)]:hidden"
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
      <SheetContent ref={sheet} data-menu-sheet="" className="desktop:hidden flex w-full flex-col">
        <SheetTitle className="sr-only">Pages</SheetTitle>
        <nav aria-label="Pages">
          <ul className="max-w-band gap-sp-1 px-gutter pt-sp-2 pb-sp-1 m-0 mx-auto flex list-none flex-col">
            {items.map((item) => {
              const Icon = ICONS[item.kind];
              const here = item.href === current;
              return (
                <li key={item.href}>
                  <a
                    href={item.href}
                    aria-current={here ? "page" : undefined}
                    className="press min-h-dock gap-sp-3 rounded-tile px-sp-2 text-ink hover-fine:bg-raised aria-[current=page]:bg-raised flex items-center no-underline"
                  >
                    <span
                      aria-hidden
                      className="size-touch rounded-tile bg-raised text-ink-2 flex flex-none items-center justify-center"
                    >
                      <Icon className="size-sp-5" />
                    </span>
                    <span className="flex min-w-0 flex-auto flex-col">
                      <span className="text-body truncate leading-tight font-semibold">
                        {item.label}
                      </span>
                      <span className="text-meta text-mute truncate leading-tight">
                        {NOTES[item.kind]}
                      </span>
                    </span>
                    {here && (
                      <CheckIcon
                        aria-hidden
                        data-check=""
                        className="size-sp-5 text-accent-ink flex-none"
                        strokeWidth={2.5}
                      />
                    )}
                  </a>
                  {item === week && past.length > 0 && (
                    <PastWeeks
                      weeks={past}
                      pageHref={pageHref}
                      open={pastOpen}
                      onToggle={() => setPastOpen((was) => !was)}
                    />
                  )}
                </li>
              );
            })}
          </ul>
        </nav>
        {foot && (
          <CloseMenuSheet.Provider value={closeThen}>
            <div className="max-w-band px-gutter pb-sp-1 mx-auto w-full">{foot}</div>
          </CloseMenuSheet.Provider>
        )}
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
    // oxlint-disable-next-line design/no-arbitrary-value -- the chips line up under the label, past the 44 px icon and one step
    <div className="pl-[calc(var(--spacing-touch)+var(--spacing-sp-5))]">
      <PendingButton
        type="button"
        aria-expanded={open}
        aria-controls={id}
        onClick={onToggle}
        className="press min-h-touch gap-sp-1 text-meta text-ink-2 hover-fine:text-ink flex items-center font-semibold"
      >
        Past weeks
        <ChevronDownIcon
          aria-hidden
          data-open={open || undefined}
          className="menu-chevron size-sp-4"
        />
      </PendingButton>
      {/* The pad sits on the inner list, never on the grid track, so the closed track has no height left. */}
      <div
        id={id}
        data-open={open || undefined}
        aria-hidden={!open || undefined}
        inert={!open}
        className="menu-past"
      >
        <div className="min-h-0 overflow-hidden">
          <ul aria-label="Past weeks" className="gap-sp-2 pb-sp-2 m-0 flex list-none flex-wrap p-0">
            {weeks.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  aria-current={link.href === pageHref ? "page" : undefined}
                  className="press min-h-touch min-w-touch rounded-pill border-rule bg-card px-sp-4 text-meta tracking-caps text-ink aria-[current=page]:border-accent flex items-center justify-center border font-mono font-bold no-underline"
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
