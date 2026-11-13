/**
 * The menu button of the top band and the sheet of pages that it opens, on a page that has no dock, such as the front door.
 * The sheet drops from under the band with one row per page, the week row, "Past weeks", and the rows that the page adds.
 * From the desktop tier the pill bar takes its place.
 */
"use client";

import { CheckIcon, ChevronDownIcon, type LucideIcon, MenuIcon, XIcon } from "lucide-react";
import { type PointerEvent as ReactPointerEvent, type ReactNode, useEffect, useId, useRef, useState } from "react";
import { ICONS } from "./dock";
import { weekChipLabel, type NavItem, type NavKind, type WeekLink } from "./nav";

type SheetKind = Exclude<NavKind, "midseason">;

/* The note under the name of each page. The name says what the page is, and the note says what a manager does there. */
const NOTES: Record<SheetKind, string> = {
  home: "Ask about your team",
  week: "Scores and recaps",
  rankings: "The league, ranked",
  managers: "Grades and records",
  analyzer: "Check a trade",
  waiver: "Adds worth a claim",
};

/* A drag must move this far before the sheet follows it, so a tap on a row stays a tap. */
const SLOP = 8;
/* A drag up past this distance, or a flick faster than this speed in px per ms, closes the sheet on release. */
const CLOSE_DISTANCE = 56;
const CLOSE_SPEED = 0.4;

/* A drag down past the open place meets more and more friction, as the edge of a native sheet. */
function rubberband(overshoot: number) {
  return (overshoot * 120 * 0.55) / (120 + 0.55 * overshoot);
}

type MenuSheetProps = {
  items: NavItem[];
  // The published weeks, newest first.
  weeks: WeekLink[];
  // The href of the item to mark, from currentHref.
  current?: string;
  // The href of the open page.
  pageHref?: string;
  // The rows that the page adds under the pages, each a MenuRow, such as the row of the front door that changes the
  // passphrase. The app passes them, so the shell names no page.
  rows?: ReactNode;
};

type Drag = { id: number; startY: number; lastY: number; lastT: number; speed: number; moving: boolean };

export function MenuSheet({ items: all, weeks, current, pageHref, rows }: MenuSheetProps) {
  const items = all.filter((item): item is NavItem & { kind: SheetKind } => item.kind !== "midseason");
  const [open, setOpen] = useState(false);
  const [pastOpen, setPastOpen] = useState(false);
  const button = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLElement>(null);
  const drag = useRef<Drag | null>(null);
  // A drag that moved ends in a click on the row under the finger, and that click must not open the row.
  const dragged = useRef(false);
  const id = useId();

  const close = () => {
    setOpen(false);
    button.current?.focus();
  };

  useEffect(() => {
    if (!open) return;
    // The focus goes to the sheet, so a keyboard user and a screen reader start at the top of the rows.
    panel.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  // The sheet moves with the finger. The transform goes on the panel alone, so no child restyles on each move.
  const place = (offset: number | null) => {
    const element = panel.current;
    if (!element) return;
    element.style.transform = offset === null ? "" : `translateY(${offset}px)`;
    element.style.transition = offset === null ? "" : "none";
  };

  const onPointerDown = (event: ReactPointerEvent<HTMLElement>) => {
    // A second finger does not take over the drag, so the sheet never jumps to it.
    if (drag.current || !event.isPrimary) return;
    dragged.current = false;
    drag.current = { id: event.pointerId, startY: event.clientY, lastY: event.clientY, lastT: event.timeStamp, speed: 0, moving: false };
  };

  const onPointerMove = (event: ReactPointerEvent<HTMLElement>) => {
    const state = drag.current;
    if (!state || state.id !== event.pointerId) return;
    const offset = event.clientY - state.startY;
    if (!state.moving) {
      if (Math.abs(offset) < SLOP) return;
      state.moving = true;
      dragged.current = true;
      // The capture keeps the drag on the sheet when the finger leaves it. jsdom has no capture.
      event.currentTarget.setPointerCapture?.(event.pointerId);
    }
    const elapsed = event.timeStamp - state.lastT;
    if (elapsed > 0) state.speed = (event.clientY - state.lastY) / elapsed;
    state.lastY = event.clientY;
    state.lastT = event.timeStamp;
    place(offset < 0 ? offset : rubberband(offset));
  };

  const onPointerEnd = (event: ReactPointerEvent<HTMLElement>) => {
    const state = drag.current;
    if (!state || state.id !== event.pointerId) return;
    drag.current = null;
    if (!state.moving) return;
    const offset = event.clientY - state.startY;
    // The panel takes its transition back in the same frame as the close, so it leaves from where the finger let go.
    place(null);
    if (offset <= -CLOSE_DISTANCE || state.speed <= -CLOSE_SPEED) close();
  };

  const onPointerCancel = (event: ReactPointerEvent<HTMLElement>) => {
    if (drag.current?.id !== event.pointerId) return;
    drag.current = null;
    place(null);
  };

  const week = items.find((item) => item.kind === "week");
  return (
    <>
      {/* The X takes the place of the icon of the menu, in the same spot, so the way out sits under the thumb that opened it.
          The negative margin lines the icon up with the edge. */}
      <button
        ref={button}
        type="button"
        aria-label={open ? "Close the menu" : "Open the menu"}
        aria-expanded={open}
        aria-controls={id}
        onClick={() => (open ? close() : setOpen(true))}
        className="press -mr-sp-3 flex size-touch flex-none items-center justify-center text-ink hover-fine:text-accent-ink desktop:hidden [@media(scripting:none)]:hidden"
      >
        <span aria-hidden data-open={open || undefined} className="menu-icon">
          <MenuIcon className="size-sp-5" />
          <XIcon className="size-sp-5" />
        </span>
      </button>
      {/* The page under the band dims while the sheet is open, and a tap on it closes the sheet. It starts under the
          band, so the band and its X stay bright. */}
      <div
        aria-hidden
        data-testid="menu-scrim"
        data-open={open || undefined}
        onClick={close}
        className="menu-scrim fixed inset-x-0 top-band-height bottom-0 bg-scrim desktop:hidden"
      />
      {/* The clip hides the sheet while it sits up under the band, so it seems to drop out of the band. */}
      <div className="pointer-events-none absolute inset-x-0 top-full overflow-hidden desktop:hidden">
        <nav
          ref={panel}
          id={id}
          aria-label="Pages"
          aria-hidden={!open || undefined}
          inert={!open}
          tabIndex={-1}
          data-open={open || undefined}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerEnd}
          onPointerCancel={onPointerCancel}
          onBlur={(event) => {
            // A Tab past the last row moves the focus to the page, so the sheet closes and leaves the focus there.
            // A tap on the dimmed page gives no next focus, and its own close puts the focus on the button.
            const next = event.relatedTarget;
            if (next instanceof Node && !event.currentTarget.contains(next) && next !== button.current) setOpen(false);
          }}
          onClickCapture={(event) => {
            if (!dragged.current) return;
            dragged.current = false;
            event.preventDefault();
            event.stopPropagation();
          }}
          className="menu-sheet rounded-b-card border-b border-rule bg-page shadow-drop outline-none"
        >
          <ul className="mx-auto m-0 flex max-w-band list-none flex-col gap-sp-1 px-gutter pt-sp-2 pb-sp-3">
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
                    <RowFace icon={Icon} label={item.label} note={NOTES[item.kind]} />
                    {here && <CheckIcon aria-hidden data-check="" className="size-sp-5 flex-none text-accent-ink" strokeWidth={2.5} />}
                  </a>
                  {item === week && weeks.length > 0 && (
                    <PastWeeks weeks={weeks} pageHref={pageHref} open={pastOpen} onToggle={() => setPastOpen((was) => !was)} />
                  )}
                </li>
              );
            })}
            {/* A row of the page acts on the page, so the sheet closes once the row acts, and the page takes the focus. */}
            {rows && <li onClick={() => setOpen(false)}>{rows}</li>}
          </ul>
        </nav>
      </div>
    </>
  );
}

/* The icon tile, the name, and the note of one row of the sheet. */
function RowFace({ icon: Icon, label, note }: { icon: LucideIcon; label: string; note: string }) {
  return (
    <>
      <span aria-hidden className="flex size-touch flex-none items-center justify-center rounded-tile bg-raised text-ink-2">
        <Icon className="size-sp-5" />
      </span>
      <span className="flex min-w-0 flex-auto flex-col">
        <span className="truncate text-body leading-tight font-semibold">{label}</span>
        <span className="truncate text-meta leading-tight text-mute">{note}</span>
      </span>
    </>
  );
}

/* A row of the sheet that acts on the page in place of a link, with the look of the row of a page. */
export function MenuRow({ icon, label, note, onClick }: { icon: LucideIcon; label: string; note: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="press flex min-h-dock w-full items-center gap-sp-3 rounded-tile px-sp-2 text-left text-ink hover-fine:bg-raised"
    >
      <RowFace icon={icon} label={label} note={note} />
    </button>
  );
}

type PastWeeksProps = { weeks: WeekLink[]; pageHref?: string; open: boolean; onToggle: () => void };

/* "Past weeks" under the week row, and the chips of every week that it opens, newest first. The list grows on the
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
