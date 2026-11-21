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
    <span aria-hidden className="h-sp-2 rounded-pill bg-bar-off relative block">
      <span className="bg-mute absolute inset-y-0 left-1/2 w-px -translate-x-1/2" />
      <motion.span
        data-lean={better ? "better" : "worse"}
        className={`rounded-pill absolute inset-y-0 ${better ? "bg-accent left-1/2 origin-left" : "bg-mute right-1/2 origin-right"}`}
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
  const enter = (index: number) =>
    live ? riseIn(off, { delay: VERY_SLOW * 0.4 + staggerOf(index) }) : {};
  return (
    <div className="gap-sp-3 flex min-w-0 flex-col" data-block="slot_ranks">
      <motion.div
        role="group"
        aria-label="Roster grade"
        className="gap-sp-3 flex items-baseline"
        {...enter(0)}
      >
        <span className="text-score text-ink leading-tight font-bold tracking-tight">
          {block.grade}
        </span>
        <span className="text-body leading-body text-ink-2 min-w-0">{block.read}</span>
      </motion.div>
      <div
        className="text-label tracking-caps text-mute flex justify-between font-mono leading-tight uppercase"
        aria-hidden
      >
        <span>Worse</span>
        <span>League middle</span>
        <span>Better</span>
      </div>
      <ol aria-label="Slot ranks" className="border-rule m-0 flex list-none flex-col border-t p-0">
        {block.rows.map((row, index) => (
          <motion.li
            key={row.position}
            // The rank column fits "10th of 12" on one line at the larger type of the desktop, and every row keeps the
            // same width so the bars line up.
            className="gap-x-sp-3 border-rule py-sp-3 grid grid-cols-[2.5rem_minmax(0,1fr)_6.5rem] items-center border-b last:border-b-0"
            {...enter(index + 1)}
          >
            <span className="text-row text-ink font-mono leading-tight font-semibold">
              {row.position}
            </span>
            <Bar lean={leanOf(row.rank, block.teams)} live={live} index={index} />
            <span className="text-row text-ink-2 text-right font-mono leading-tight whitespace-nowrap tabular-nums">
              {row.label}
            </span>
          </motion.li>
        ))}
      </ol>
    </div>
  );
}
