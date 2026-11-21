/**
 * The art of the sim Announcement: Your team's name and playoff odds, the standings rows around Your team with the
 * playoff line, and the What-if chip of a win this week. Each number comes from the week sim file.
 */
"use client";

import { Button } from "@cpc/design/ui/button";
import { animate, motion, useMotionValue, useTransform } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import { LABEL } from "../page/format";
import type { PreviewData, PreviewRow } from "./preview";

/* The beat between the stop of the sheet and the automatic turn of the chip. The rows land first, so the eye reads the
   race, then sees one What-if move it. */
export const AUTO_WHAT_IF_MS = 700;

/* --ease-smooth-out of the motion tokens, the curve of each entry and each move of the art. */
const SMOOTH = [0.22, 1, 0.36, 1] as const;
const STAGGER = 0.04;

/* Three rows: the team above Your team, Your team, and the team below. At the top or the foot of the table, the three
   rows nearest to it. */
function windowOf(table: PreviewRow[], you: number): PreviewRow[] {
  const at = table.findIndex((row) => row.id === you);
  const start = Math.max(0, Math.min(table.length - 3, at - 1));
  return table.slice(start, start + 3);
}

/* A number that counts to its value from where it is, so a change never jumps. Tabular figures keep its width still.
   With motion off, it shows the value at once. The count is for the eye, so a screen reader reads the live line. */
function Count({ value, off, delay = 0 }: { value: number; off: boolean; delay?: number }) {
  const count = useMotionValue(off ? value : 0);
  const text = useTransform(count, (v) => String(Math.round(v)));
  useEffect(() => {
    if (off) {
      count.set(value);
      return;
    }
    const run = animate(count, value, { duration: 0.5, delay, ease: SMOOTH });
    return () => run.stop();
  }, [count, value, off, delay]);
  // A motion value paints on the next frame, so with motion off the plain number shows in the same render.
  if (off) {
    return (
      <span aria-hidden className="tabular-nums">
        {value}
      </span>
    );
  }
  return (
    <motion.span aria-hidden className="tabular-nums">
      {text}
    </motion.span>
  );
}

/* `settled` turns true once the sheet stops on open. The chip then turns on once by itself, unless motion is off or the
   manager has tapped it. */
export function SimPreview({
  data,
  you,
  settled,
}: {
  data: PreviewData;
  you: number;
  settled: boolean;
}) {
  const off = useMotionOff();
  const own = data.table.find((row) => row.id === you)!;
  const rows = windowOf(data.table, you);
  const whatIfOdds = data.whatIf[you] ?? null;
  const whatIf =
    whatIfOdds === null
      ? null
      : { label: `What-if: ${own.name} win${data.median ? " both" : ""}`, odds: whatIfOdds };
  const spots = data.spots;
  const [on, setOn] = useState(false);
  // The chip turns on by itself at most once, and never after a tap.
  const touched = useRef(false);

  useEffect(() => {
    if (!settled || off || !whatIf || touched.current) return;
    const timer = window.setTimeout(() => {
      if (touched.current) return;
      touched.current = true;
      setOn(true);
    }, AUTO_WHAT_IF_MS);
    return () => window.clearTimeout(timer);
  }, [settled, off, whatIf]);

  const yours = on && whatIf ? whatIf.odds : own.odds;
  const gain = whatIf ? whatIf.odds - own.odds : 0;
  // The first count waits for the rows to rise. After the first turn of the chip, each change moves at once, on or off.
  const moved = touched.current;
  const countDelay = moved ? 0 : 0.35;

  return (
    <div className="gap-sp-3 rounded-card bg-card-band p-sp-4 text-on-dark flex flex-col">
      <div className="gap-sp-3 flex items-start justify-between">
        <div className="gap-sp-0 flex min-w-0 flex-col">
          <span className={cn(LABEL, "text-on-dark-muted")}>Your team</span>
          <span className="text-body truncate leading-tight font-semibold">{own.name}</span>
        </div>
        <div className="gap-sp-1 flex flex-none flex-col items-end">
          <span aria-hidden className="gap-sp-1 flex items-baseline">
            {/* The gain of the What-if rises in beside the odds while the chip is on. */}
            <motion.span
              initial={false}
              animate={{ opacity: on ? 1 : 0, y: on && !off ? 0 : off ? 0 : 4 }}
              transition={{ duration: off ? 0.15 : 0.25, ease: SMOOTH }}
              className="text-meta text-accent-text font-mono leading-tight font-bold tabular-nums"
            >
              {gain >= 0 ? `+${gain}` : String(gain)}
            </motion.span>
            <span className="text-score leading-tight font-bold tracking-tight">
              <Count value={yours} off={off} delay={countDelay} />%
            </span>
          </span>
          <span aria-hidden className={cn(LABEL, "text-on-dark-muted font-normal")}>
            Playoff odds
          </span>
          <span role="status" className="sr-only">{`Playoff odds ${yours}%`}</span>
        </div>
      </div>

      <ol
        aria-label="Standings near your team"
        className="gap-sp-1 m-0 flex list-none flex-col p-0"
      >
        {rows.map((row, index) => {
          const mine = row.id === you;
          const value = mine ? yours : row.odds;
          return (
            <li key={row.id} className="flex flex-col">
              {/* Under reduced motion, each row and its bar show at once. */}
              <motion.div
                initial={off ? false : { opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, ease: SMOOTH, delay: 0.2 + index * STAGGER }}
                className="gap-sp-2 grid grid-cols-[1.25rem_minmax(0,1fr)_34%_2.75rem] items-center"
              >
                <span className="text-label text-on-dark-muted font-mono leading-tight tabular-nums">
                  {row.place}
                </span>
                <span
                  data-team
                  className={cn(
                    "text-row truncate leading-tight",
                    mine ? "text-on-dark font-bold" : "text-on-dark-2",
                  )}
                >
                  {row.name}
                </span>
                <span aria-hidden className="rounded-pill bg-chip-dark h-1.5 overflow-hidden">
                  <motion.span
                    className={cn(
                      "rounded-pill block h-full origin-left",
                      mine ? "bg-accent" : "bg-on-dark-muted",
                    )}
                    initial={off ? false : { scaleX: 0 }}
                    animate={{ scaleX: value / 100 }}
                    transition={{
                      duration: mine && moved ? 0.5 : 0.7,
                      ease: SMOOTH,
                      delay: mine && moved ? 0 : 0.3 + index * STAGGER,
                    }}
                  />
                </span>
                <span
                  className={cn(
                    "text-meta text-right font-mono leading-tight tabular-nums",
                    mine ? "font-bold" : "text-on-dark-2",
                  )}
                >
                  {mine ? <Count value={value} off={off} delay={countDelay} /> : value}%
                </span>
              </motion.div>
              {row.place === spots && (
                <span className="mt-sp-1 gap-sp-2 flex items-center">
                  <span
                    aria-hidden
                    className="border-on-dark-muted/60 h-px flex-1 border-t border-dashed"
                  />
                  <span className={cn(LABEL, "text-on-dark-muted font-normal")}>Playoff line</span>
                </span>
              )}
            </li>
          );
        })}
      </ol>

      {whatIf && (
        <Button
          variant="plain"
          type="button"
          aria-pressed={on}
          onClick={() => {
            touched.current = true;
            setOn((now) => !now);
          }}
          className="press min-h-touch gap-sp-2 rounded-pill border-rule-dark px-sp-4 text-row focus-visible:outline-on-dark hover-fine:not-aria-pressed:border-on-dark-muted aria-pressed:border-accent aria-pressed:bg-accent/30 flex items-center justify-between border text-left leading-tight font-semibold transition-[background-color,border-color] duration-200 outline-none focus-visible:outline-2 focus-visible:outline-offset-2"
        >
          <span className="truncate">{whatIf.label}</span>
          <span aria-hidden className="text-label tracking-caps flex-none font-mono uppercase">
            {on ? "On" : "Tap"}
          </span>
        </Button>
      )}
    </div>
  );
}
