/**
 * The sheet of the Trade Wire: the two trade links, the eyebrow with the countdown, the title, the live line, and the
 * accepted trades of Deadline week, newest first. A new trade slides in at the top, and the rows under it move down.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { SheetClose, SheetContent, SheetGrip, SheetTitle } from "@cpc/design/ui/sheet";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import type { WireTrade } from "../lib/api";
import type { TradeWire } from "../lib/use-trade-wire";

/* The smooth-out ease of transitions.dev, for a panel that opens and for a change of position. */
export const SMOOTH_OUT = [0.22, 1, 0.36, 1] as const;

/* The day and the time in Eastern, as the managers read the NFL clock: "Fri 7:04 PM". Some engines put a narrow space
   before PM, so each engine gives the same text. */
const WHEN = new Intl.DateTimeFormat("en-US", { weekday: "short", hour: "numeric", minute: "2-digit", timeZone: "America/New_York" });
export function whenOf(trade: WireTrade): string {
  return WHEN.format(new Date(trade.accepted_at)).replace(/ /g, " ");
}

/* The trade links, "Grade a trade" and "Find a trade". findHref is null while the finder flag is off. */
export type TradeLinks = { gradeHref: string; findHref: string | null };

export function WireSheet({
  closed,
  countdown,
  wire,
  links,
}: {
  closed: boolean;
  countdown: string | null;
  wire: TradeWire;
  links: TradeLinks;
}) {
  return (
    <SheetContent
      data-wire-sheet
      className="mx-auto flex max-h-[85dvh] w-full max-w-sheet flex-col rounded-t-hero border border-b-0 border-rule bg-card shadow-sheet"
    >
      <SheetGrip className="mt-sp-2 h-sp-1 w-sp-6" />
      <div className="flex flex-none flex-col gap-sp-3 px-sp-5 pt-sp-3 pb-sp-2">
        {/* After the trade deadline Sleeper blocks a trade, so the links leave. */}
        {!closed && <Links links={links} />}
        <div className="flex flex-col gap-sp-1">
          <span className="font-mono text-label leading-tight font-bold tracking-caps text-mute uppercase">
            {closed ? "Final" : `Trade deadline ${countdown}`}
          </span>
          <div className="flex items-center gap-sp-2">
            <SheetTitle className="m-0 text-score leading-tight font-bold tracking-tight">Trade Wire</SheetTitle>
            {wire.readAt !== null && <LiveLine closed={closed} readAt={wire.readAt} count={wire.trades?.length ?? 0} />}
          </div>
          {/* A polite live region, so a screen reader hears the note once, and not each tick of the live line. */}
          <p aria-live="polite" className="m-0 font-mono text-meta text-mute empty:hidden">
            {wire.failed ? "The last update failed." : ""}
          </p>
        </div>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-sp-5 pb-[calc(var(--spacing-sp-6)+env(safe-area-inset-bottom))]">
        {wire.trades !== null && <WireList trades={wire.trades} closed={closed} />}
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
    <div className={cn("grid gap-sp-2", links.findHref !== null && "grid-cols-2")}>
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

/* The live dot with "Updated Ns ago", which ticks each second while the sheet is open. After the trade deadline the list
   is final, so the line counts the trades of the week instead. */
function LiveLine({ closed, readAt, count }: { closed: boolean; readAt: number; count: number }) {
  const now = useNow(!closed);
  if (closed) {
    return (
      <span className="ml-auto font-mono text-meta text-mute tabular-nums">
        {count} {count === 1 ? "trade" : "trades"} this week
      </span>
    );
  }
  const ago = Math.max(0, Math.floor((now - readAt) / 1000));
  return (
    <span data-wire-updated className="ml-auto flex items-center gap-sp-2 font-mono text-meta text-mute tabular-nums">
      <LiveDot />
      Updated {ago}s ago
    </span>
  );
}

/* The live dot: a soft ring grows and fades while the trade deadline is open. It rests under reduced motion. */
export function LiveDot({ className }: { className?: string }) {
  return <span aria-hidden="true" className={cn("deadline-live relative size-sp-2 flex-none rounded-full bg-accent", className)} />;
}

/* The clock, read each second while `ticks` holds. */
function useNow(ticks: boolean): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    setNow(Date.now());
    if (!ticks) return;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [ticks]);
  return now;
}

/* The list. The rows on screen when the sheet opens do not animate. A trade that a poll brings in slides down from the
   top with a short blur, 400 ms with the smooth-out ease, and the rows under it move down by layout. Under reduced
   motion it shows at once. With no trade, one quiet line says so. */
function WireList({ trades, closed }: { trades: WireTrade[]; closed: boolean }) {
  const off = useMotionOff();
  if (trades.length === 0) {
    return (
      <p data-wire-empty className="m-0 border-t border-rule py-sp-6 text-center text-row text-mute">
        {closed ? "No trades this week." : "No trades yet this week."}
      </p>
    );
  }
  return (
    <ol className="m-0 flex list-none flex-col border-t border-rule p-0">
      <AnimatePresence initial={false}>
        {trades.map((trade) => (
          <motion.li
            key={trade.transaction_id}
            data-trade={trade.transaction_id}
            layout={off ? false : "position"}
            initial={off ? false : { opacity: 0, y: -8, filter: "blur(2px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{ duration: 0.4, ease: SMOOTH_OUT }}
            className="border-b border-rule py-sp-4 last:border-b-0"
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
    <article className="flex flex-col gap-sp-2">
      <p data-wire-line className="m-0 font-mono text-meta leading-tight text-mute tabular-nums">
        {whenOf(trade)}
      </p>
      {trade.teams.map((side) => (
        <div key={side.roster_id} data-wire-line className="flex min-w-0 items-start gap-sp-3">
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
            <span aria-hidden="true" className="size-sp-6 flex-none rounded-full bg-raised" />
          )}
          <div className="flex min-w-0 flex-1 flex-col gap-sp-0">
            <span className="truncate text-row leading-tight font-bold">{side.team} gets</span>
            <span className="text-row leading-tight text-ink-2 text-pretty">
              {side.players.map((player) => `${player.name} ${player.position}`).join(", ")}
              {side.faab > 0 && (
                <span className="font-mono text-meta text-mute tabular-nums">
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
