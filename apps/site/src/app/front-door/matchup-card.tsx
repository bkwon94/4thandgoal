/**
 * The matchup card of Your last matchup and Your next matchup, in the Ledger look: the two teams and their scores, a tug
 * bar, and the lineups slot by slot with a bar from the center line for the gap of each slot. Its schema is in lib/data/blocks/.
 */
"use client";

import { motion } from "framer-motion";
import { gap, num, shortName } from "@cpc/design/format/format";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { type MatchupBlock, type MatchupSlot, slotGap } from "@/lib/data/blocks/matchup-schema";
import { SLOW, fadeIn, riseIn, staggerOf } from "./motion";

/* The tug bar: the share of Your team, red from the left, against the share of the other team, gray from the right. It
   reads the win odds when the card has them, and the share of the two scores when it does not. */
function Tug({ block, live }: { block: MatchupBlock; live: boolean }) {
  const off = useMotionOff();
  const total = block.you.score + block.them.score;
  const share = block.odds ?? (total > 0 ? block.you.score / total : 0.5);
  const percent = Math.round(share * 100);
  const label =
    block.odds === null ? `Your share of the points, ${percent}%` : `Your win odds, ${percent}%`;
  // The red part grows out from the left edge, as the eye reads; with motion off it only fades in.
  const grow = live
    ? {
        initial: off ? { opacity: 0 } : { opacity: 0, scaleX: 0 },
        animate: off ? { opacity: 1 } : { opacity: 1, scaleX: 1 },
        transition: fadeIn(SLOW, 0.1),
      }
    : {};
  return (
    <div className="gap-sp-1 flex flex-col">
      <div
        role="img"
        aria-label={label}
        className="rounded-pill bg-rule relative h-2 overflow-hidden"
      >
        <motion.span
          aria-hidden
          data-tug
          className="rounded-pill bg-accent absolute inset-y-0 left-0 origin-left"
          style={{ width: `${share * 100}%` }}
          {...grow}
        />
      </div>
      {block.odds !== null && (
        <p className="text-meta text-mute m-0 flex justify-between font-mono leading-tight tabular-nums">
          <span className="text-accent-ink">{percent}%</span>
          <span>{100 - percent}%</span>
        </p>
      )}
    </div>
  );
}

/* One team in the head of the card. The team ahead carries the ink; the other is quiet. */
function Team({
  name,
  score,
  ahead,
  align,
}: {
  name: string;
  score: number;
  ahead: boolean;
  align: "left" | "right";
}) {
  return (
    <div
      className={`gap-sp-1 flex min-w-0 flex-col ${align === "right" ? "items-end text-right" : ""}`}
    >
      <p
        className={`text-row m-0 max-w-full truncate leading-tight font-semibold ${align === "left" ? "text-accent-ink" : "text-ink-2"}`}
      >
        {name}
      </p>
      <p
        className={`text-stat m-0 leading-tight tabular-nums ${ahead ? "text-ink font-bold" : "text-mute font-semibold"}`}
      >
        {num(score)}
      </p>
    </div>
  );
}

/* One side of one slot: the short name and the points, or "Empty" for a slot with no player. */
function Side({
  player,
  won,
  align,
}: {
  player: MatchupSlot["you"];
  won: boolean;
  align: "left" | "right";
}) {
  if (player === null)
    return (
      <span
        className={`text-meta text-mute truncate font-mono leading-tight ${align === "right" ? "text-right" : ""}`}
      >
        Empty
      </span>
    );
  const points = (
    <span
      className={`text-row flex-none font-mono leading-tight tabular-nums ${won ? "text-ink font-bold" : "text-mute"}`}
    >
      {num(player.points)}
    </span>
  );
  const name = (
    <span
      className={`text-row min-w-0 truncate leading-tight ${won ? "text-ink font-semibold" : "text-ink-2"}`}
    >
      {shortName(player.name)}
    </span>
  );
  return (
    <span
      className={`gap-sp-2 flex min-w-0 items-baseline ${align === "right" ? "justify-end" : ""}`}
    >
      {align === "left" ? (
        <>
          {name}
          {points}
        </>
      ) : (
        <>
          {points}
          {name}
        </>
      )}
    </span>
  );
}

/* The bar of one slot from the center line: to the left in red when Your player won the slot, to the right in gray when
   the other player did. Its length is the gap against the widest gap of the card. */
function GapBar({
  value,
  widest,
  index,
  live,
}: {
  value: number;
  widest: number;
  index: number;
  live: boolean;
}) {
  const off = useMotionOff();
  const side = value > 0 ? "you" : value < 0 ? "them" : "even";
  const width = widest > 0 ? (Math.abs(value) / widest) * 50 : 0;
  // A bar grows out from the center line, so the eye sees which way the slot went before how far.
  const grow = live
    ? {
        initial: off ? { opacity: 0 } : { opacity: 0, scaleX: 0 },
        animate: off ? { opacity: 1 } : { opacity: 1, scaleX: 1 },
        transition: fadeIn(SLOW, 0.2 + staggerOf(index)),
      }
    : {};
  return (
    <span aria-hidden className="relative block h-1">
      <span className="bg-rule -inset-y-sp-0 absolute left-1/2 w-px" />
      <motion.span
        data-gap={side}
        className={`rounded-pill absolute inset-y-0 ${side === "you" ? "bg-accent right-1/2 origin-right" : "bg-mute left-1/2 origin-left"}`}
        style={{ width: `${width}%` }}
        {...grow}
      />
    </span>
  );
}

export function MatchupCard({ block, live }: { block: MatchupBlock; live: boolean }) {
  const off = useMotionOff();
  const rise = (delay: number) => (live ? riseIn(off, { delay }) : {});
  const gaps = block.slots.map(slotGap);
  const widest = Math.max(0, ...gaps.map(Math.abs));
  const kind = block.final ? "Final" : "Projected";
  return (
    <div
      role="group"
      aria-label={`${kind} matchup`}
      className="gap-sp-4 flex min-w-0 flex-col"
      data-block="matchup"
    >
      <motion.div className="gap-sp-3 flex flex-col" {...rise(0)}>
        <p className="text-meta tracking-caps text-mute m-0 font-mono leading-tight uppercase">
          {kind}
        </p>
        <div className="gap-x-sp-4 grid grid-cols-2 items-end">
          <Team
            name={block.you.name}
            score={block.you.score}
            ahead={block.you.score >= block.them.score}
            align="left"
          />
          <Team
            name={block.them.name}
            score={block.them.score}
            ahead={block.them.score >= block.you.score}
            align="right"
          />
        </div>
        <Tug block={block} live={live} />
      </motion.div>
      <ul
        aria-label="Slot by slot"
        className="border-rule m-0 flex list-none flex-col border-t p-0"
      >
        {block.slots.map((slot, index) => {
          const value = gaps[index];
          const label = `${slot.slot}: ${slot.you ? `${slot.you.name} ${num(slot.you.points)}` : "empty"}, ${slot.them ? `${slot.them.name} ${num(slot.them.points)}` : "empty"}, ${gap(value)}`;
          return (
            <motion.li
              key={`${slot.slot}-${index}`}
              data-slot={slot.slot}
              aria-label={label}
              className="gap-sp-1 border-rule py-sp-2 flex flex-col border-b last:border-b-0"
              {...rise(0.1 + staggerOf(index + 1))}
            >
              <span className="gap-x-sp-2 grid grid-cols-[minmax(0,1fr)_3rem_minmax(0,1fr)] items-baseline">
                <Side player={slot.you} won={value > 0} align="left" />
                <span className="text-meta tracking-caps text-mute text-center font-mono leading-tight uppercase">
                  {slot.slot}
                </span>
                <Side player={slot.them} won={value < 0} align="right" />
              </span>
              <GapBar value={value} widest={widest} index={index} live={live} />
            </motion.li>
          );
        })}
      </ul>
    </div>
  );
}
