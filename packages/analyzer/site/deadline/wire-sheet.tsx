/**
 * The sheet of the Trade Wire: the two trade links, the eyebrow with the countdown, the title, the live line, and the
 * accepted trades of Deadline week, newest first. A new trade slides in at the top, and the rows under it move down.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { SheetClose, SheetContent, SheetGrip, SheetTitle } from "@cpc/design/ui/sheet";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { SMOOTH_OUT } from "@cpc/design/lib/motion";
import { cn } from "@cpc/design/lib/utils";
import type { WireTrade } from "../lib/api";
import type { TradeWire } from "../lib/use-trade-wire";

/* The day and the time in Eastern, as the managers read the NFL clock: "Fri 7:04 PM". Some engines put a narrow space
   before PM, so each engine gives the same text. */
const WHEN = new Intl.DateTimeFormat("en-US", {
  weekday: "short",
  hour: "numeric",
  minute: "2-digit",
  timeZone: "America/New_York",
});
export function whenOf(trade: WireTrade): string {
  return WHEN.format(new Date(trade.accepted_at)).replace(/ /g, " ");
}

/* The trade links, "Grade a trade" and "Find a trade". findHref is null while the finder flag is off. */
export type TradeLinks = { gradeHref: string; findHref: string | null };

export function WireSheet({
  countdown,
  wire,
  links,
}: {
  countdown: string | null;
  wire: TradeWire;
  links: TradeLinks;
}) {
  return (
    <SheetContent
      data-wire-sheet
      className="max-w-sheet rounded-t-hero border-rule bg-card shadow-sheet mx-auto flex max-h-[85dvh] w-full flex-col border border-b-0"
    >
      <SheetGrip className="mt-sp-2 h-sp-1 w-sp-6" />
      <div className="gap-sp-3 px-sp-5 pt-sp-3 pb-sp-2 flex flex-none flex-col">
        <Links links={links} />
        <div className="gap-sp-1 flex flex-col">
          {/* The meta size, as the eyebrow of the banner: the label size is 10px on a phone, under the floor of 11px. */}
          <span className="text-meta tracking-caps text-mute font-mono leading-tight font-bold uppercase">
            {`Trade deadline ${countdown}`}
          </span>
          <div className="gap-sp-2 flex items-center">
            <SheetTitle className="text-score m-0 leading-tight font-bold tracking-tight">
              Trade Wire
            </SheetTitle>
            {wire.readAt !== null && <LiveLine readAt={wire.readAt} />}
          </div>
          {/* A polite live region, so a screen reader hears the note once, and not each tick of the live line. */}
          <p aria-live="polite" className="text-meta text-mute m-0 font-mono empty:hidden">
            {wire.failed ? "The last update failed." : ""}
          </p>
        </div>
      </div>
      {/* oxlint-disable-next-line design/no-arbitrary-value -- the home bar of an iPhone needs the safe-area inset, which no token adds to a step */}
      <div className="px-sp-5 min-h-0 flex-1 overflow-y-auto overscroll-contain pb-[calc(var(--spacing-sp-6)+env(safe-area-inset-bottom))]">
        {wire.trades !== null && <WireList trades={wire.trades} />}
      </div>
      <SheetClose className="sr-only">Close</SheetClose>
    </SheetContent>
  );
}

/* Two equal halves when the finder flag is on. The light half grades, and the dark half finds, as in the hero. */
function Links({ links }: { links: TradeLinks }) {
  const base =
    "press flex min-h-touch items-center justify-center rounded-card px-sp-3 text-row font-bold no-underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";
  return (
    <div className={cn("gap-sp-2 grid", links.findHref !== null && "grid-cols-2")}>
      <a href={links.gradeHref} className={cn(base, "bg-raised text-ink")}>
        Grade a trade
      </a>
      {links.findHref !== null && (
        <a href={links.findHref} className={cn(base, "bg-ink text-page")}>
          Find a trade
        </a>
      )}
    </div>
  );
}

/* The live dot with "Updated Ns ago", which ticks each second while the sheet is open. */
function LiveLine({ readAt }: { readAt: number }) {
  const ago = useSecondsSince(readAt);
  return (
    <span
      data-wire-updated
      className="gap-sp-2 text-meta text-mute ml-auto flex items-center font-mono tabular-nums"
    >
      <LiveDot />
      Updated {ago}s ago
    </span>
  );
}

/* The live dot: a soft ring grows and fades while the trade deadline is open. It rests under reduced motion. */
export function LiveDot({ className }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={cn("deadline-live size-sp-2 bg-accent relative flex-none rounded-full", className)}
    />
  );
}

/* The whole seconds since `since`, read on each whole second after it. The tick lines up with the
   read and not with the open of the sheet, so the line reads N s at N s after the read, and never up to 1 s late. A new
   read gives a new `since`, and the count starts again from it. */
function useSecondsSince(since: number): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    setNow(Date.now());
    let id: number | undefined;
    const next = () => {
      const intoSecond = (((Date.now() - since) % 1000) + 1000) % 1000;
      id = window.setTimeout(() => {
        setNow(Date.now());
        next();
      }, 1000 - intoSecond);
    };
    next();
    return () => window.clearTimeout(id);
  }, [since]);
  return Math.max(0, Math.floor((now - since) / 1000));
}

/* The list. The rows on screen when the sheet opens do not animate. A trade that a poll brings in slides down from the
   top with a short blur, 400 ms with the smooth-out ease, and the rows under it move down by layout. Under reduced
   motion it shows at once. With no trade, one quiet line says so. */
function WireList({ trades }: { trades: WireTrade[] }) {
  const off = useMotionOff();
  if (trades.length === 0) {
    return (
      <p
        data-wire-empty
        className="border-rule py-sp-6 text-row text-mute m-0 border-t text-center"
      >
        No trades yet this week.
      </p>
    );
  }
  return (
    <ol className="border-rule m-0 flex list-none flex-col border-t p-0">
      <AnimatePresence initial={false}>
        {trades.map((trade) => (
          <motion.li
            key={trade.transaction_id}
            data-trade={trade.transaction_id}
            layout={off ? false : "position"}
            initial={off ? false : { opacity: 0, y: -8, filter: "blur(2px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{ duration: 0.4, ease: SMOOTH_OUT }}
            className="border-rule py-sp-4 border-b last:border-b-0"
          >
            <Trade trade={trade} />
          </motion.li>
        ))}
      </AnimatePresence>
    </ol>
  );
}

/* One trade as one even block: the time line and each side are rows with the same gap, sp-2. Each trade sits in an
   equal pad, sp-4, above and under its rule, so the gap between trades is the same. */
function Trade({ trade }: { trade: WireTrade }) {
  return (
    <article className="gap-sp-2 flex flex-col">
      <p data-wire-line className="text-meta text-mute m-0 font-mono leading-tight tabular-nums">
        {whenOf(trade)}
      </p>
      {trade.teams.map((side) => (
        <div key={side.roster_id} data-wire-line className="gap-sp-3 flex min-w-0 items-start">
          {side.avatar ? (
            <img
              src={side.avatar}
              alt=""
              width={24}
              height={24}
              loading="lazy"
              className="size-sp-6 flex-none rounded-full object-cover outline-1 -outline-offset-1 outline-black/10 dark:outline-white/10"
            />
          ) : (
            <span aria-hidden="true" className="size-sp-6 bg-raised flex-none rounded-full" />
          )}
          <div className="gap-sp-0 flex min-w-0 flex-1 flex-col">
            <span className="text-row truncate leading-tight font-bold">{side.team} gets</span>
            <span className="text-row text-ink-2 leading-tight text-pretty">
              {side.players.map((player) => `${player.name} ${player.position}`).join(", ")}
              {side.faab > 0 && (
                <span className="text-meta text-mute font-mono tabular-nums">
                  {side.players.length > 0 ? " · " : ""}${side.faab} FAAB
                </span>
              )}
            </span>
          </div>
        </div>
      ))}
    </article>
  );
}
