/**
 * The rank mover list of Power rankings, in the Ledger look: one row per team with its rank, its name, a bar from the
 * center for its move, and an arrow with the number of places. Its schema is in lib/data/blocks/.
 */
"use client";

import { motion } from "framer-motion";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { type RankMoversBlock, moveWords } from "@/lib/data/blocks/rank-movers-schema";
import { SLOW, fadeIn, riseIn, staggerOf } from "./motion";

/* The bar of one move from the center: to the right in the up color for a rise, to the left in the down color for a
   fall. Its length is the move against the biggest move of the week. */
function MoveBar({ move, biggest, index, live }: { move: number; biggest: number; index: number; live: boolean }) {
  const off = useMotionOff();
  const width = biggest > 0 ? (Math.abs(move) / biggest) * 50 : 0;
  // A bar grows out from the center line, so the eye sees the way of the move before its size.
  const grow = live ? { initial: off ? { opacity: 0 } : { opacity: 0, scaleX: 0 }, animate: off ? { opacity: 1 } : { opacity: 1, scaleX: 1 }, transition: fadeIn(SLOW, 0.2 + staggerOf(index)) } : {};
  return (
    <span aria-hidden className="relative block h-1.5">
      <span className="absolute inset-y-[-3px] left-1/2 w-px bg-rule" />
      {move !== 0 && (
        <motion.span
          className={`absolute inset-y-0 rounded-pill ${move > 0 ? "left-1/2 origin-left bg-move-up" : "right-1/2 origin-right bg-move-down"}`}
          style={{ width: `${width}%` }}
          {...grow}
        />
      )}
    </span>
  );
}

/* The arrow and the number of places, in words for a screen reader through the label of the row. */
function Move({ move }: { move: number | null }) {
  const way = move === null || move === 0 ? "none" : move > 0 ? "up" : "down";
  const color = way === "up" ? "text-move-up" : way === "down" ? "text-move-down" : "text-mute";
  return (
    <span data-move={way} aria-hidden className={`flex-none text-right font-mono text-meta leading-tight font-semibold tabular-nums ${color}`}>
      {way === "none" ? "–" : `${way === "up" ? "▲" : "▼"}${Math.abs(move!)}`}
    </span>
  );
}

export function RankMoverList({ block, live }: { block: RankMoversBlock; live: boolean }) {
  const off = useMotionOff();
  const biggest = Math.max(0, ...block.rows.map((row) => Math.abs(row.move ?? 0)));
  return (
    <div className="flex min-w-0 flex-col gap-sp-2" data-block="rank_movers">
      <ul aria-label="Power rankings" className="m-0 flex list-none flex-col border-t border-rule p-0">
        {block.rows.map((row, index) => (
          <motion.li
            key={row.roster_id}
            aria-label={`${row.rank}. ${row.name}${row.you ? ", your team" : ""}, ${moveWords(row.move)}`}
            {...(row.you ? { "data-you": "" } : {})}
            className="grid grid-cols-[1.5rem_minmax(0,1fr)_minmax(3.5rem,30%)_2.25rem] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0"
            {...(live ? riseIn(off, { delay: staggerOf(index) }) : {})}
          >
            <span aria-hidden className="font-mono text-meta leading-tight text-mute tabular-nums">{row.rank}</span>
            <span aria-hidden className="flex min-w-0 items-baseline gap-sp-2">
              <span className={`truncate text-row leading-tight font-semibold ${row.you ? "text-accent-ink" : "text-ink"}`}>{row.name}</span>
              {/* "You" names the row of Your team in words, so it never rests on the red alone. */}
              {row.you && <span className="flex-none font-mono text-meta leading-tight tracking-caps text-accent-ink uppercase">You</span>}
            </span>
            <MoveBar move={row.move ?? 0} biggest={biggest} index={index} live={live} />
            <Move move={row.move} />
          </motion.li>
        ))}
      </ul>
    </div>
  );
}
