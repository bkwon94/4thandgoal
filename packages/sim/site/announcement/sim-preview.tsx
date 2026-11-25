/**
 * The art of The Race Announcement: Your team's name and odds of a playoff spot, and the League board rows around Your
 * team with the "You" tag and the pill of each team that is Clinched or Out. Each number comes from the week sim file.
 */
"use client";

import { animate, motion, useMotionValue, useTransform } from "framer-motion";
import { useEffect } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import { LABEL, recordText } from "../page/format";
import type { PreviewData, PreviewRow } from "./preview";

/* --ease-smooth-out of the motion tokens, the curve of each entry of the art. */
const SMOOTH = [0.22, 1, 0.36, 1] as const;
const STAGGER = 0.04;

/* Three rows: the team above Your team, Your team, and the team below. At the top or the foot of the board, the three
   rows nearest to it. */
function windowOf(rows: PreviewRow[], you: number): PreviewRow[] {
  const at = rows.findIndex((row) => row.id === you);
  const start = Math.max(0, Math.min(rows.length - 3, at - 1));
  return rows.slice(start, start + 3);
}

/* A number that counts up to its value as the sheet rises. Tabular figures keep its width still. With motion off, it
   shows the value at once. The count is for the eye, so a screen reader reads the live line. */
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

/* The pill sits on the dark band of the art, so it is a quiet chip with light text, not the tint of the page board. */
function Pill({ text }: { text: string }) {
  return (
    <span
      data-pill
      className="rounded-pill bg-chip-dark px-sp-2 py-sp-0 text-label text-on-dark flex-none leading-tight font-bold whitespace-nowrap"
    >
      {text}
    </span>
  );
}

export function SimPreview({ data, you }: { data: PreviewData; you: number }) {
  const off = useMotionOff();
  const own = data.rows.find((row) => row.id === you)!;
  const rows = windowOf(data.rows, you);

  return (
    <div className="gap-sp-3 rounded-card bg-card-band p-sp-4 text-on-dark flex flex-col">
      <div className="gap-sp-3 flex items-start justify-between">
        <div className="gap-sp-0 flex min-w-0 flex-col">
          <span className={cn(LABEL, "text-on-dark-muted")}>Your team</span>
          <span className="text-body truncate leading-tight font-semibold">{own.name}</span>
        </div>
        <div className="gap-sp-1 flex flex-none flex-col items-end">
          <span aria-hidden className="text-score leading-tight font-bold tracking-tight">
            <Count value={own.odds} off={off} delay={0.35} />%
          </span>
          <span aria-hidden className={cn(LABEL, "text-on-dark-muted font-normal")}>
            Spot odds
          </span>
          <span role="status" className="sr-only">{`Odds of a playoff spot ${own.odds}%`}</span>
        </div>
      </div>

      <div className="gap-sp-2 flex flex-col">
        <span aria-hidden className={cn(LABEL, "text-on-dark-muted font-normal")}>
          League board
        </span>
        <ol
          aria-label="League board near your team"
          className="gap-sp-2 m-0 flex list-none flex-col p-0"
        >
          {rows.map((row, index) => {
            const mine = row.id === you;
            return (
              <li key={row.id}>
                {/* Under reduced motion, each row and its bar show at once. */}
                <motion.div
                  initial={off ? false : { opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35, ease: SMOOTH, delay: 0.2 + index * STAGGER }}
                  className="gap-x-sp-3 gap-y-sp-1 grid grid-cols-[minmax(0,1fr)_2.75rem] items-center"
                >
                  <span className="gap-sp-0 flex min-w-0 flex-col">
                    <span className="gap-sp-2 flex min-w-0 items-center">
                      <span
                        data-team
                        className={cn(
                          "text-row min-w-0 truncate leading-tight",
                          mine ? "text-on-dark font-bold" : "text-on-dark-2",
                        )}
                      >
                        {row.name}
                      </span>
                      {mine && <span className={cn(LABEL, "text-accent-text flex-none")}>You</span>}
                      {row.pill !== null && <Pill text={row.pill} />}
                    </span>
                    <span className="text-label text-on-dark-muted leading-tight tabular-nums">
                      {recordText(row.record)}
                    </span>
                  </span>
                  <span
                    className={cn(
                      "text-meta text-right font-mono leading-tight tabular-nums",
                      mine ? "font-bold" : "text-on-dark-2",
                    )}
                  >
                    {mine ? <Count value={row.odds} off={off} delay={0.35} /> : row.odds}%
                  </span>
                  <span
                    aria-hidden
                    className="rounded-pill bg-chip-dark col-span-2 h-1.5 overflow-hidden"
                  >
                    <motion.span
                      className={cn(
                        "rounded-pill block h-full origin-left",
                        mine ? "bg-accent" : "bg-on-dark-muted",
                      )}
                      initial={off ? false : { scaleX: 0 }}
                      animate={{ scaleX: row.odds / 100 }}
                      transition={{ duration: 0.7, ease: SMOOTH, delay: 0.3 + index * STAGGER }}
                    />
                  </span>
                </motion.div>
              </li>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
