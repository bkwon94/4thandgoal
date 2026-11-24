/**
 * The Deadline banner: the strip under the top band of each page before the Lock, with the countdown to the trade
 * deadline. The whole strip is one button, the trigger of the shared sheet that holds the Trade Wire. At the Lock it
 * renders nothing.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useLayoutEffect, useRef } from "react";
import { Sheet, SheetBackdrop, SheetTrigger } from "@cpc/design/ui/sheet";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import type { ApiTarget } from "../lib/api";
import { type Deadline, type DeadlinePhase } from "../lib/deadline";
import { useDeadline } from "../lib/use-deadline";
import { useTradeWire } from "../lib/use-trade-wire";
import { SMOOTH_OUT } from "@cpc/design/lib/motion";
import { LiveDot, type TradeLinks, WireSheet } from "./wire-sheet";

/* The surface of each phase, from the theme tokens only, so the banner reads in light and in dark. */
const TONE: Record<OpenPhase, string> = {
  open: "border-rule bg-card text-ink",
  "last-hours": "border-accent bg-accent text-on-dark",
};

/* The phases that show the banner. At the Lock the phase is closed, and the banner is gone. */
type OpenPhase = Exclude<DeadlinePhase, "closed" | "ended">;
type OpenDeadline = Deadline & { phase: OpenPhase };

const isOpen = (deadline: Deadline): deadline is OpenDeadline =>
  deadline.phase === "open" || deadline.phase === "last-hours";

/* The banner for the Lock `lock`, in ms since the epoch. The app passes it only for a client with a Lock. It also passes
   the API of the Trade Wire route and the trade links, because the package reads no config. findHref is null while the
   finder flag is off. */
export function DeadlineBanner({
  lock,
  api,
  gradeHref,
  findHref,
}: { lock: number; api: ApiTarget } & TradeLinks) {
  const deadline = useDeadline(lock);
  const ref = useRef<HTMLDivElement>(null);
  const over = deadline !== null && !isOpen(deadline);

  // The top band grows by the height of the banner, so each page that sizes itself under the band, such as the front
  // door, reads the band height token with the banner in it. The CSS adds this height while the banner is in the page.
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const root = document.documentElement;
    // The box height keeps the fraction of a pixel. offsetHeight rounds it, so the band token would end a fraction short
    // of the real bottom of the band.
    const measure = () =>
      root.style.setProperty("--deadline-banner-h", `${el.getBoundingClientRect().height}px`);
    measure();
    // A browser with no ResizeObserver, such as jsdom, keeps the first height.
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measure);
    observer?.observe(el);
    return () => {
      observer?.disconnect();
      root.style.removeProperty("--deadline-banner-h");
    };
  }, [over]);

  if (over) return null;
  const phase = deadline?.phase ?? "open";
  return (
    <div ref={ref} data-deadline-banner="" data-phase={phase}>
      {deadline !== null && isOpen(deadline) ? (
        <Banner deadline={deadline} api={api} links={{ gradeHref, findHref }} />
      ) : (
        <Placeholder />
      )}
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

/* The name of the button. Before the first read the count is not known, so the name gives none. */
function nameOf(count: number | null): string {
  if (count === null) return "Open the Trade Wire";
  return `Open the Trade Wire, ${count} new ${count === 1 ? "trade" : "trades"}`;
}

function Banner({
  deadline,
  api,
  links,
}: {
  deadline: OpenDeadline;
  api: ApiTarget;
  links: TradeLinks;
}) {
  const phase = deadline.phase;
  // The poll stops when the banner leaves at the Lock, because the hook ends with the banner.
  const wire = useTradeWire(api, true);
  const count = wire.trades === null ? null : wire.trades.length;
  const name = nameOf(count);
  return (
    <Sheet side="bottom" container={typeof document === "undefined" ? undefined : document.body}>
      {/* The press of transitions.dev: the grid sinks to 0.98 in 150 ms with the ease-out while the press holds, and the
          surface dims a little, so the tap reads at once. */}
      <SheetTrigger
        aria-label={name}
        className={cn(
          "group focus-visible:outline-accent block w-full cursor-pointer border-0 border-t border-solid p-0 text-left transition-[filter] duration-150 ease-(--ease-out) focus-visible:outline-2 focus-visible:-outline-offset-2 active:brightness-95",
          TONE[phase],
        )}
      >
        <Grid phase={phase} countdown={deadline.countdown} count={count ?? 0} />
      </SheetTrigger>
      <SheetBackdrop />
      <WireSheet countdown={deadline.countdown} wire={wire} links={links} />
    </Sheet>
  );
}

/* One grid: a gutter for the live dot, then one left edge for the eyebrow and the countdown, then "Trade Wire" and its
   badge on the right, centred on the two lines. The pad above and under the grid is the same. */
function Grid({
  phase,
  countdown,
  count = 0,
  hidden = false,
}: {
  phase: OpenPhase;
  countdown: string | null;
  count?: number;
  hidden?: boolean;
}) {
  const last = phase === "last-hours";
  return (
    <span
      data-deadline-grid
      className={cn(
        "max-w-band gap-x-sp-2 px-gutter py-sp-2 mx-auto grid grid-cols-[var(--spacing-sp-2)_minmax(0,1fr)_auto] items-center",
        "transition-transform duration-150 ease-(--ease-out) group-active:scale-[0.98] motion-reduce:transition-none",
        hidden && "invisible",
      )}
    >
      {/* The eyebrow takes the meta size, the smallest size of the scale over the floor of 11px for other text at
            every tier. The label size is 10px on a phone, under the floor. */}
      <span
        data-deadline-eyebrow
        className={cn(
          "text-meta tracking-caps col-start-2 row-start-1 font-mono leading-tight font-bold uppercase",
          last ? "deadline-shimmer text-on-dark" : "text-mute",
        )}
      >
        Trade deadline
      </span>
      <LiveDot className={cn("col-start-1 row-start-2", last && "bg-on-dark")} />
      {/* A non-breaking space keeps the line height before the first tick. */}
      <span
        data-deadline-countdown
        className="text-body col-start-2 row-start-2 font-mono leading-tight font-bold tabular-nums"
      >
        {countdown ?? " "}
      </span>
      <span className="gap-sp-2 text-row col-start-3 row-span-2 row-start-1 flex items-center font-bold">
        Trade Wire
        {/* The count of the trades of the week. With no trade the badge leaves, so the banner never says "0 new". The name of the button carries the count, so the badge is hidden
            from a screen reader. */}
        {count > 0 && (
          <span
            aria-hidden="true"
            data-deadline-badge
            className={cn(
              // oxlint-disable-next-line design/no-arbitrary-value -- the gap before "new" is a quarter of the text size, so it scales with the font in em
              "rounded-pill px-sp-2 py-sp-0 text-meta flex items-center gap-[0.25em] font-mono",
              last ? "bg-on-dark text-accent" : "bg-accent text-on-dark",
            )}
          >
            <Count value={count} /> new
          </span>
        )}
      </span>
    </span>
  );
}

/* A count that changes in place, as the number subtle change of transitions.dev: the new digit rises in with a short
   cross-fade, so "2 new" turns "3 new" without a jump. Under reduced motion the digit swaps with a plain fade. */
function Count({ value }: { value: number }) {
  const off = useMotionOff();
  return (
    <span className="relative inline-grid overflow-hidden tabular-nums">
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={value}
          initial={off ? { opacity: 0 } : { opacity: 0, y: 6, filter: "blur(2px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={off ? { opacity: 0 } : { opacity: 0, y: -6, filter: "blur(2px)" }}
          transition={{ duration: 0.25, ease: SMOOTH_OUT }}
        >
          {value}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}
