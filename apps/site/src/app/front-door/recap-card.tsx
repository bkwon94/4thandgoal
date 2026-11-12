/**
 * The recap card of Week recap, in the Ledger look: the score and the place, a strip with a mark for each team, the top
 * scorer of Your team against his projection, and the first sentence of the recap. Its schema is in lib/data/blocks/.
 */
"use client";

import { motion } from "framer-motion";
import { gap, num, ordinal } from "@cpc/design/format/format";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { RecapBlock } from "@/lib/data/blocks/recap-schema";
import { SLOW, STAGGER, VERY_SLOW, fadeIn, riseIn } from "./motion";

/* The marks sit inside 4% to 96% of the strip, so the end marks never touch the edge of the card. */
const EDGE = 4;
/* A label over a mark stays inside 12% to 88%, so a label at the top or the bottom score never runs off the card. */
const LABEL_EDGE = 12;

const clamp = (value: number, low: number, high: number) => Math.min(high, Math.max(low, value));

/* The place of a score on the strip, in percent of its width, from the lowest score to the highest. */
function placeOf(score: number, low: number, high: number): number {
  return high === low ? 50 : EDGE + ((100 - 2 * EDGE) * (score - low)) / (high - low);
}

/* The result of the game of Your team, in words, such as "Won vs Teehee". */
function resultOf(block: RecapBlock): string | null {
  if (block.opponent === null || block.opponent_score === null) return null;
  const word = block.score > block.opponent_score ? "Won" : block.score < block.opponent_score ? "Lost" : "Tied";
  return `${word} vs ${block.opponent}`;
}

/* The strip: one mark per team on a line from the lowest score to the highest. The mark of Your team is red and tall,
   the rest are gray. A dashed tick marks the median, only in a league that plays the median game. The marks grow up
   from the line, low score first, so the eye ends on the high end; with motion off they only fade in. */
function Strip({ block, live }: { block: RecapBlock; live: boolean }) {
  const off = useMotionOff();
  const scores = block.strip.map((mark) => mark.score);
  const low = Math.min(...scores);
  const high = Math.max(...scores);
  const you = placeOf(block.score, low, high);
  const label = `${block.teams} scores from ${num(low)} to ${num(high)}. Yours, ${num(block.score)}, is ${ordinal(block.place)}.${block.median === null ? "" : ` The median ${num(block.median)}.`}`;
  const grow = (index: number) =>
    live ? { initial: off ? { opacity: 0 } : { opacity: 0, scaleY: 0 }, animate: off ? { opacity: 1 } : { opacity: 1, scaleY: 1 }, transition: fadeIn(SLOW, 0.15 + index * STAGGER) } : {};
  // The marks grow low to high, so the strip reads left to right as the eye does.
  const lowFirst = [...block.strip].reverse();
  return (
    <div className="flex flex-col gap-sp-1">
      <div role="img" aria-label={label} className="relative h-14">
        {/* The "You" label sits over the red mark, so the mark of Your team reads in words and not by color alone. */}
        <span aria-hidden className="absolute top-0 -translate-x-1/2 font-mono text-meta leading-tight font-semibold tracking-caps text-accent-ink uppercase" style={{ left: `${clamp(you, LABEL_EDGE, 100 - LABEL_EDGE)}%` }}>
          You
        </span>
        <span aria-hidden className="absolute inset-x-0 bottom-sp-2 h-px bg-rule" />
        {block.median !== null && (
          <motion.span
            aria-hidden
            data-median
            className="absolute bottom-0 h-8 -translate-x-1/2 border-l border-dashed border-ink-2"
            style={{ left: `${placeOf(block.median, low, high)}%` }}
            {...(live ? { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: fadeIn(SLOW, 0.15 + block.teams * STAGGER) } : {})}
          />
        )}
        {lowFirst.map((mark, index) => (
          <motion.span
            key={mark.roster_id}
            aria-hidden
            data-mark={mark.you ? "you" : "team"}
            title={`${mark.name} ${num(mark.score)}`}
            className={`absolute bottom-sp-2 origin-bottom -translate-x-1/2 rounded-pill ${mark.you ? "z-10 h-7 w-1 bg-accent" : "h-4 w-0.5 bg-mute"}`}
            style={{ left: `${placeOf(mark.score, low, high)}%` }}
            {...grow(index)}
          />
        ))}
      </div>
      {/* The scale: the lowest and the highest score at the ends, and the median under its tick. */}
      <div className="relative h-4 font-mono text-meta leading-tight text-mute tabular-nums">
        <span className="absolute left-0">{num(low)}</span>
        {block.median !== null && (
          <span className="absolute -translate-x-1/2 whitespace-nowrap text-ink-2" style={{ left: `${clamp(placeOf(block.median, low, high), LABEL_EDGE + 10, 90 - LABEL_EDGE)}%` }}>
            Median {num(block.median)}
          </span>
        )}
        <span className="absolute right-0">{num(high)}</span>
      </div>
    </div>
  );
}

export function RecapCard({ block, live }: { block: RecapBlock; live: boolean }) {
  const off = useMotionOff();
  const result = resultOf(block);
  const rise = (delay: number, text = false) => (live ? riseIn(off, { delay, text }) : {});
  const top = block.top;
  const beat = top && top.projection !== null ? top.points - top.projection : null;
  return (
    <div role="group" aria-label="Your week" className="flex min-w-0 flex-col gap-sp-4" data-block="recap">
      <motion.div className="flex min-w-0 flex-wrap items-end justify-between gap-x-sp-4 gap-y-sp-1" {...rise(0)}>
        <div className="flex min-w-0 flex-col gap-sp-1">
          <p className="m-0 font-mono text-meta leading-tight tracking-caps text-mute uppercase">Your score</p>
          <p className="m-0 text-stat leading-tight font-bold text-ink tabular-nums">{num(block.score)}</p>
        </div>
        <div className="flex min-w-0 flex-col items-end gap-sp-1 text-right">
          <p className="m-0 text-row leading-tight font-semibold text-ink tabular-nums">{`${ordinal(block.place)} of ${block.teams}`}</p>
          {result && (
            <p className="m-0 max-w-full truncate font-mono text-meta leading-tight text-mute tabular-nums">
              {result}, {num(block.opponent_score!)}
            </p>
          )}
        </div>
      </motion.div>
      <Strip block={block} live={live} />
      {top && (
        <motion.div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-sp-3 border-y border-rule py-sp-2" {...rise(0.15 + block.teams * STAGGER)}>
          <span className="flex min-w-0 flex-col">
            <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">Top scorer</span>
            <span className="flex min-w-0 items-baseline gap-sp-2">
              <span className="truncate text-row leading-tight font-semibold text-ink">{top.name}</span>
              <span className="flex-none font-mono text-meta leading-tight text-mute">{top.position}</span>
            </span>
          </span>
          <span className="flex flex-col items-end">
            <span className="font-mono text-row leading-tight font-bold text-ink tabular-nums">{num(top.points)}</span>
            {top.projection !== null && (
              <span className="font-mono text-meta leading-tight text-mute tabular-nums">
                Proj {num(top.projection)}
                {beat !== null && beat !== 0 && <span className={`ml-sp-1 ${beat > 0 ? "text-move-up" : "text-move-down"}`}>{gap(beat)}</span>}
              </span>
            )}
          </span>
        </motion.div>
      )}
      {block.sentence && (
        <motion.p className="m-0 text-body leading-body text-ink-2" {...rise(VERY_SLOW * 0.6 + block.teams * STAGGER, true)}>
          {block.sentence}
        </motion.p>
      )}
    </div>
  );
}
