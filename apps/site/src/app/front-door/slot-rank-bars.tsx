/**
 * The slot rank bars of How you stack up: one row each for QB, RB, WR, and TE, with a bar from the league middle and
 * the rank, under the roster grade and its read. It holds the schema of the block, its short text, and its view.
 */
"use client";

import { motion } from "framer-motion";
import { z } from "zod";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { FAST, VERY_SLOW, fadeIn, riseIn, staggerOf } from "./motion";

export const slotRanksBlockSchema = z.object({
  kind: z.literal("slot_ranks"),
  grade: z.string(),
  read: z.string(),
  teams: z.number(),
  rows: z.array(z.object({ position: z.string(), rank: z.number(), label: z.string() })),
});
export type SlotRanksBlock = z.infer<typeof slotRanksBlockSchema>;

export function slotRanksText(block: SlotRanksBlock): string {
  return `Roster grade ${block.grade}. ${block.read} Slot ranks: ${block.rows.map((row) => `${row.position} ${row.label}`).join(", ")}.`;
}

/* The lean of a rank from the league middle, from -1 at the last place to 1 at the first. The middle of 12 teams sits
   between 6th and 7th, so no rank is 0 in an even league. */
export function leanOf(rank: number, teams: number): number {
  const middle = (teams + 1) / 2;
  return teams > 1 ? (middle - rank) / (middle - 1) : 0;
}

/* One bar on a track with a center line. A better rank grows right in the accent color, and a worse rank grows left
   in gray. The bar grows from the center line, so its origin sits on the side of the line. */
function Bar({ lean, live, index }: { lean: number; live: boolean; index: number }) {
  const off = useMotionOff();
  const better = lean > 0;
  const width = `${Math.max(Math.abs(lean) * 50, 2)}%`;
  const grow = live && !off;
  return (
    <span aria-hidden className="relative block h-sp-2 rounded-pill bg-bar-off">
      <span className="absolute inset-y-0 left-1/2 w-px -translate-x-1/2 bg-mute" />
      <motion.span
        data-lean={better ? "better" : "worse"}
        className={`absolute inset-y-0 rounded-pill ${better ? "left-1/2 origin-left bg-accent" : "right-1/2 origin-right bg-mute"}`}
        style={{ width }}
        initial={grow ? { opacity: 0, scaleX: 0.2 } : live ? { opacity: 0 } : false}
        animate={{ opacity: 1, scaleX: 1 }}
        transition={fadeIn(FAST * 1.6, VERY_SLOW * 0.6 + staggerOf(index + 1))}
      />
    </span>
  );
}

export function SlotRanksView({ block, live }: { block: SlotRanksBlock; live: boolean }) {
  const off = useMotionOff();
  const enter = (index: number) => (live ? riseIn(off, { delay: VERY_SLOW * 0.4 + staggerOf(index) }) : {});
  return (
    <div className="flex min-w-0 flex-col gap-sp-3" data-block="slot_ranks">
      <motion.div role="group" aria-label="Roster grade" className="flex items-baseline gap-sp-3" {...enter(0)}>
        <span className="text-score leading-tight font-bold tracking-tight text-ink">{block.grade}</span>
        <span className="min-w-0 text-body leading-body text-ink-2">{block.read}</span>
      </motion.div>
      <div className="flex justify-between font-mono text-label leading-tight tracking-caps text-mute uppercase" aria-hidden>
        <span>Worse</span>
        <span>League middle</span>
        <span>Better</span>
      </div>
      <ol aria-label="Slot ranks" className="m-0 flex list-none flex-col border-t border-rule p-0">
        {block.rows.map((row, index) => (
          <motion.li
            key={row.position}
            className="grid grid-cols-[2.5rem_minmax(0,1fr)_5.5rem] items-center gap-x-sp-3 border-b border-rule py-sp-3 last:border-b-0"
            {...enter(index + 1)}
          >
            <span className="font-mono text-row leading-tight font-semibold text-ink">{row.position}</span>
            <Bar lean={leanOf(row.rank, block.teams)} live={live} index={index} />
            <span className="text-right font-mono text-row leading-tight text-ink-2 tabular-nums">{row.label}</span>
          </motion.li>
        ))}
      </ol>
    </div>
  );
}
