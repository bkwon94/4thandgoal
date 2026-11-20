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
  const word =
    block.score > block.opponent_score
      ? "Won"
      : block.score < block.opponent_score
        ? "Lost"
        : "Tied";
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
    live
      ? {
          initial: off ? { opacity: 0 } : { opacity: 0, scaleY: 0 },
          animate: off ? { opacity: 1 } : { opacity: 1, scaleY: 1 },
          transition: fadeIn(SLOW, 0.15 + index * STAGGER),
        }
      : {};
  // The marks grow low to high, so the strip reads left to right as the eye does.
  const lowFirst = [...block.strip].reverse();
  return (
    <div className="gap-sp-1 flex flex-col">
      <div role="img" aria-label={label} className="relative h-14">
        {/* The "You" label sits over the red mark, so the mark of Your team reads in words and not by color alone. */}
        <span
          aria-hidden
          className="text-meta tracking-caps text-accent-ink absolute top-0 -translate-x-1/2 font-mono leading-tight font-semibold uppercase"
          style={{ left: `${clamp(you, LABEL_EDGE, 100 - LABEL_EDGE)}%` }}
        >
          You
        </span>
        <span aria-hidden className="bottom-sp-2 bg-rule absolute inset-x-0 h-px" />
        {block.median !== null && (
          <motion.span
            aria-hidden
            data-median
            className="border-ink-2 absolute bottom-0 h-8 -translate-x-1/2 border-l border-dashed"
            style={{ left: `${placeOf(block.median, low, high)}%` }}
            {...(live
              ? {
                  initial: { opacity: 0 },
                  animate: { opacity: 1 },
                  transition: fadeIn(SLOW, 0.15 + block.teams * STAGGER),
                }
              : {})}
          />
        )}
        {lowFirst.map((mark, index) => (
          <motion.span
            key={mark.roster_id}
            aria-hidden
            data-mark={mark.you ? "you" : "team"}
            title={`${mark.name} ${num(mark.score)}`}
            className={`bottom-sp-2 rounded-pill absolute origin-bottom -translate-x-1/2 ${mark.you ? "bg-accent z-10 h-7 w-1" : "bg-mute h-4 w-0.5"}`}
            style={{ left: `${placeOf(mark.score, low, high)}%` }}
            {...grow(index)}
          />
        ))}
      </div>
      {/* The scale: the lowest and the highest score at the ends, and the median under its tick. */}
      <div className="text-meta text-mute relative h-4 font-mono leading-tight tabular-nums">
        <span className="absolute left-0">{num(low)}</span>
        {block.median !== null && (
          <span
            className="text-ink-2 absolute -translate-x-1/2 whitespace-nowrap"
            style={{
              left: `${clamp(placeOf(block.median, low, high), LABEL_EDGE + 10, 90 - LABEL_EDGE)}%`,
            }}
          >
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
    <div
      role="group"
      aria-label="Your week"
      className="gap-sp-4 flex min-w-0 flex-col"
      data-block="recap"
    >
      <motion.div
        className="gap-x-sp-4 gap-y-sp-1 flex min-w-0 flex-wrap items-end justify-between"
        {...rise(0)}
      >
        <div className="gap-sp-1 flex min-w-0 flex-col">
          <p className="text-meta tracking-caps text-mute m-0 font-mono leading-tight uppercase">
            Your score
          </p>
          <p className="text-stat text-ink m-0 leading-tight font-bold tabular-nums">
            {num(block.score)}
          </p>
        </div>
        <div className="gap-sp-1 flex min-w-0 flex-col items-end text-right">
          <p className="text-row text-ink m-0 leading-tight font-semibold tabular-nums">{`${ordinal(block.place)} of ${block.teams}`}</p>
          {result && (
            <p className="text-meta text-mute m-0 max-w-full truncate font-mono leading-tight tabular-nums">
              {result}, {num(block.opponent_score!)}
            </p>
          )}
        </div>
      </motion.div>
      <Strip block={block} live={live} />
      {top && (
        <motion.div
          className="gap-x-sp-3 border-rule py-sp-2 grid grid-cols-[minmax(0,1fr)_auto] items-center border-y"
          {...rise(0.15 + block.teams * STAGGER)}
        >
          <span className="flex min-w-0 flex-col">
            <span className="text-meta tracking-caps text-mute font-mono leading-tight uppercase">
              Top scorer
            </span>
            <span className="gap-sp-2 flex min-w-0 items-baseline">
              <span className="text-row text-ink truncate leading-tight font-semibold">
                {top.name}
              </span>
              <span className="text-meta text-mute flex-none font-mono leading-tight">
                {top.position}
              </span>
            </span>
          </span>
          <span className="flex flex-col items-end">
            <span className="text-row text-ink font-mono leading-tight font-bold tabular-nums">
              {num(top.points)}
            </span>
            {top.projection !== null && (
              <span className="text-meta text-mute font-mono leading-tight tabular-nums">
                Proj {num(top.projection)}
                {beat !== null && beat !== 0 && (
                  <span className={`ml-sp-1 ${beat > 0 ? "text-move-up" : "text-move-down"}`}>
                    {gap(beat)}
                  </span>
                )}
              </span>
            )}
          </span>
        </motion.div>
      )}
      {block.sentence && (
        <motion.p
          className="text-body leading-body text-ink-2 m-0"
          {...rise(VERY_SLOW * 0.6 + block.teams * STAGGER, true)}
        >
          {block.sentence}
        </motion.p>
      )}
    </div>
  );
}
