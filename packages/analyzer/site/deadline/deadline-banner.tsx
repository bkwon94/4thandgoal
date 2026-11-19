/**
 * The Deadline banner: the strip under the top band of each page during Deadline week, with the countdown to the trade
 * deadline. The whole strip is one button, the trigger of the shared sheet that holds the Trade Wire.
 */
"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Sheet, SheetBackdrop, SheetClose, SheetContent, SheetGrip, SheetTitle, SheetTrigger } from "@cpc/design/ui/sheet";
import { cn } from "@cpc/design/lib/utils";
import { type Deadline, type DeadlinePhase, deadlineOf } from "../lib/deadline";

/* The state of Deadline week, read from the clock each second. It is null until the first tick in the browser, because
   the static export renders at build time, and the time of the build is not the time of the reader. A tick that gives the
   same phase and text keeps the old state, so the banner renders only when its text changes. */
function useDeadline(lock: number): Deadline | null {
  const [deadline, setDeadline] = useState<Deadline | null>(null);
  useEffect(() => {
    const tick = () =>
      setDeadline((last) => {
        const next = deadlineOf(Date.now(), lock);
        return last !== null && last.phase === next.phase && last.countdown === next.countdown ? last : next;
      });
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [lock]);
  return deadline;
}

/* The surface of each phase, from the theme tokens only, so the banner reads in light and in dark. */
const TONE: Record<Exclude<DeadlinePhase, "ended">, string> = {
  open: "border-rule bg-card text-ink",
  "last-hours": "border-accent bg-accent text-on-dark",
  closed: "border-rule bg-raised text-ink",
};

const PASSED = "The trade deadline has passed. Good luck in the playoffs.";

/* The banner for the Lock `lock`, in ms since the epoch. The app passes it only for a client with a Lock. */
export function DeadlineBanner({ lock }: { lock: number }) {
  const deadline = useDeadline(lock);
  const ref = useRef<HTMLDivElement>(null);
  const ended = deadline?.phase === "ended";

  // The top band grows by the height of the banner, so each page that sizes itself under the band, such as the front
  // door, reads the band height token with the banner in it. The CSS adds this height while the banner is in the page.
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const root = document.documentElement;
    const measure = () => root.style.setProperty("--deadline-banner-h", `${el.offsetHeight}px`);
    measure();
    // A browser with no ResizeObserver, such as jsdom, keeps the first height.
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measure);
    observer?.observe(el);
    return () => {
      observer?.disconnect();
      root.style.removeProperty("--deadline-banner-h");
    };
  }, [ended]);

  if (ended) return null;
  const phase = deadline?.phase ?? "open";
  return (
    <div ref={ref} data-deadline-banner="" data-phase={phase}>
      {deadline === null ? <Placeholder /> : <Banner deadline={deadline} />}
    </div>
  );
}

/* The banner of the static export, before the first tick. It keeps the height of the open banner, so the page does not
   move when the countdown fills in. It shows no text, because the time of the build is not the time of the reader. */
function Placeholder() {
  return (
    <div aria-hidden="true" className={cn("border-t border-solid", TONE.open)}>
      <Grid phase="open" countdown={null} hidden />
    </div>
  );
}

function Banner({ deadline }: { deadline: Deadline }) {
  const phase = deadline.phase === "ended" ? "closed" : deadline.phase;
  const closed = phase === "closed";
  const name = closed ? "Open the Trade Wire, final. The trade deadline has passed." : "Open the Trade Wire";
  return (
    <Sheet side="bottom" container={typeof document === "undefined" ? undefined : document.body}>
      {/* The press of transitions.dev: the grid sinks to 0.98 in 150 ms with the ease-out while the press holds, and the
          surface dims a little, so the tap reads at once. */}
      <SheetTrigger
        aria-label={name}
        className={cn(
          "group block w-full cursor-pointer border-0 border-t border-solid p-0 text-left transition-[filter] duration-150 ease-(--ease-out) active:brightness-95 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent",
          TONE[phase],
        )}
      >
        <Grid phase={phase} countdown={deadline.countdown} />
      </SheetTrigger>
      <SheetBackdrop />
      <WireSheet closed={closed} countdown={deadline.countdown} />
    </Sheet>
  );
}

/* One grid: a gutter for the live dot, then one left edge for the eyebrow and the countdown, then "Trade Wire" and its
   badge on the right, centred on the two lines. The pad above and under the grid is the same. */
function Grid({ phase, countdown, hidden = false }: { phase: Exclude<DeadlinePhase, "ended">; countdown: string | null; hidden?: boolean }) {
  const closed = phase === "closed";
  const last = phase === "last-hours";
  return (
    <span
      data-deadline-grid
      className={cn(
        "mx-auto grid max-w-band grid-cols-[var(--spacing-sp-2)_minmax(0,1fr)_auto] items-center gap-x-sp-2 px-gutter py-sp-2",
        "transition-transform duration-150 ease-(--ease-out) group-active:scale-[0.98] motion-reduce:transition-none",
        hidden && "invisible",
      )}
    >
      {closed ? (
        <span className="col-start-2 row-span-2 text-row leading-tight font-bold text-pretty">{PASSED}</span>
      ) : (
        <>
          <span
            data-deadline-eyebrow
            className={cn(
              "col-start-2 row-start-1 font-mono text-label leading-tight font-bold tracking-caps uppercase",
              last ? "deadline-shimmer text-on-dark" : "text-mute",
            )}
          >
            Trade deadline
          </span>
          <LiveDot className={cn("col-start-1 row-start-2", last && "bg-on-dark")} />
          {/* A non-breaking space keeps the line height before the first tick. */}
          <span data-deadline-countdown className="col-start-2 row-start-2 font-mono text-body leading-tight font-bold tabular-nums">
            {countdown ?? " "}
          </span>
        </>
      )}
      <span className="col-start-3 row-span-2 row-start-1 flex items-center gap-sp-2 text-row font-bold">
        Trade Wire
        {/* The count of new trades comes with the Trade Wire. With no trade the badge leaves, so the banner never says
            "0 new". After the trade deadline the badge reads Final. */}
        {closed && (
          <span aria-hidden="true" className="rounded-pill border border-rule bg-card px-sp-2 py-sp-0 font-mono text-meta text-mute">
            Final
          </span>
        )}
      </span>
    </span>
  );
}

/* The live dot: a soft ring grows and fades while the trade deadline is open. It rests under reduced motion. */
function LiveDot({ className }: { className?: string }) {
  return <span aria-hidden="true" className={cn("deadline-live relative size-sp-2 flex-none rounded-full bg-accent", className)} />;
}

/* The sheet of the Trade Wire: the eyebrow with the countdown, the title, and the list. The list of trades comes with the
   Trade Wire route, so the sheet shows the empty line for now. */
function WireSheet({ closed, countdown }: { closed: boolean; countdown: string | null }) {
  return (
    <SheetContent
      data-wire-sheet
      className="mx-auto flex max-h-[85dvh] w-full max-w-sheet flex-col rounded-t-hero border border-b-0 border-rule bg-card shadow-sheet"
    >
      <SheetGrip className="mt-sp-2 h-sp-1 w-sp-6" />
      <div className="flex flex-none flex-col gap-sp-1 px-sp-5 pt-sp-3 pb-sp-2">
        <span className="font-mono text-label leading-tight font-bold tracking-caps text-mute uppercase">
          {closed ? "Final" : `Trade deadline ${countdown}`}
        </span>
        <SheetTitle className="m-0 text-score leading-tight font-bold tracking-tight">Trade Wire</SheetTitle>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-sp-5 pb-[calc(var(--spacing-sp-6)+env(safe-area-inset-bottom))]">
        <p data-wire-empty className="m-0 border-t border-rule py-sp-6 text-center text-row text-mute">
          {closed ? "No trades this week." : "No trades yet this week."}
        </p>
      </div>
      <SheetClose className="sr-only">Close</SheetClose>
    </SheetContent>
  );
}
