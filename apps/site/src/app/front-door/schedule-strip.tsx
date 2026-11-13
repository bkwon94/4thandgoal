/**
 * The schedule strip of Your season, in the Ledger look: a dashed step path of the standings of the opponents over the
 * weeks left, drawn against the playoff line, then one row per week. Its schema is in lib/data/blocks/.
 */
"use client";

import { motion } from "framer-motion";
import { useId } from "react";
import { ordinal } from "@cpc/design/format/format";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { ScheduleBlock } from "@/lib/data/blocks/schedule-schema";
import { SLOW, VERY_SLOW, fadeIn, riseIn, staggerOf } from "./motion";

/* The units of the drawing: one column of COLUMN per week and a height of HEIGHT. The SVG scales as one, so a dot stays
   round at each width, and each stroke keeps its width through `vector-effect`. */
const COLUMN = 60;
const HEIGHT = 84;
const PAD = 10;

/* The height of a standing in the drawing: rank 1 at the top, the last rank at the bottom. A half rank places the
   playoff line between two rows of the ladder. */
function yOf(rank: number, teams: number): number {
  return teams <= 1 ? HEIGHT / 2 : PAD + ((HEIGHT - 2 * PAD) * (rank - 1)) / (teams - 1);
}

/* The step path: a flat step across the column of each week at the height of the standing of its opponent, joined by a
   rise or a drop at each new week. */
function stepPath(block: ScheduleBlock): string {
  return block.rows
    .map((row, index) => {
      const y = yOf(row.rank, block.teams);
      return `${index === 0 ? "M" : "L"} ${index * COLUMN} ${y} L ${(index + 1) * COLUMN} ${y}`;
    })
    .join(" ");
}

/* The drawing. The path draws in from the left under a clip, as the weeks run; with motion off it only fades in. A dot
   marks each week: filled for an opponent over the playoff line, hollow for one under it. */
function Steps({ block, live }: { block: ScheduleBlock; live: boolean }) {
  const off = useMotionOff();
  const clip = useId().replace(/:/g, "");
  const width = block.rows.length * COLUMN;
  const cut = yOf(block.playoff_teams + 0.5, block.teams);
  const over = block.rows.filter((row) => row.rank <= block.playoff_teams).length;
  const label = `${block.rows.length} weeks left. ${over} of your opponents sit over the playoff line, ${block.rows.length - over} under it.`;
  const draw = live && !off;
  return (
    <div className="flex flex-col gap-sp-1">
      <svg role="img" aria-label={label} viewBox={`0 0 ${width} ${HEIGHT}`} className="block h-auto w-full overflow-visible">
        <defs>
          <clipPath id={clip}>
            <motion.rect x={0} y={-PAD} height={HEIGHT + 2 * PAD} width={width} initial={draw ? { width: 0 } : false} animate={{ width }} transition={fadeIn(VERY_SLOW * 2, 0.15)} />
          </clipPath>
        </defs>
        {/* The playoff line: a solid rule in the ink between the last playoff spot and the first team out. */}
        <line data-cut x1={0} x2={width} y1={cut} y2={cut} className="stroke-ink-2" strokeWidth={1.5} vectorEffect="non-scaling-stroke" />
        <motion.g clipPath={`url(#${clip})`} {...(live && off ? { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: fadeIn(SLOW, 0.15) } : {})}>
          <path data-path d={stepPath(block)} fill="none" className="stroke-ink-2" strokeWidth={2} strokeDasharray="4 4" strokeLinecap="round" strokeLinejoin="round" vectorEffect="non-scaling-stroke" />
          {block.rows.map((row, index) => {
            const inside = row.rank <= block.playoff_teams;
            return (
              <circle
                key={row.week}
                data-step={inside ? "over" : "under"}
                cx={index * COLUMN + COLUMN / 2}
                cy={yOf(row.rank, block.teams)}
                r={4}
                strokeWidth={1.5}
                vectorEffect="non-scaling-stroke"
                className={inside ? "fill-ink-2 stroke-ink-2" : "fill-card stroke-ink-2"}
              />
            );
          })}
        </motion.g>
      </svg>
      {/* The scale: the week under each column, and the playoff line named in words. */}
      <div aria-hidden className="grid font-mono text-meta leading-tight text-mute tabular-nums" style={{ gridTemplateColumns: `repeat(${block.rows.length}, minmax(0, 1fr))` }}>
        {block.rows.map((row) => (
          <span key={row.week} className="text-center">
            Wk {row.week}
          </span>
        ))}
      </div>
    </div>
  );
}

export function ScheduleStrip({ block, live }: { block: ScheduleBlock; live: boolean }) {
  const off = useMotionOff();
  return (
    <div className="flex min-w-0 flex-col gap-sp-3" data-block="schedule">
      <motion.p className="m-0 flex items-baseline justify-between gap-sp-3 font-mono text-meta leading-tight tracking-caps text-mute uppercase" {...(live ? riseIn(off) : {})}>
        <span className="truncate">Opponents by standing</span>
        <span className="flex flex-none items-center gap-sp-1 text-ink-2">
          <span aria-hidden className="inline-block h-0.5 w-3 bg-ink-2" />
          Playoff line
        </span>
      </motion.p>
      <Steps block={block} live={live} />
      <ul aria-label="Weeks left" className="m-0 flex list-none flex-col border-t border-rule p-0">
        {block.rows.map((row, index) => {
          const inside = row.rank <= block.playoff_teams;
          return (
            <motion.li
              key={row.week}
              data-week={row.week}
              aria-label={`Week ${row.week}, ${row.opponent}, ${ordinal(row.rank)}, ${row.record}${inside ? ", over the playoff line" : ""}`}
              className="grid grid-cols-[3rem_minmax(0,1fr)_2.5rem_2.75rem] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0"
              {...(live ? riseIn(off, { delay: 0.1 + staggerOf(index) }) : {})}
            >
              <span aria-hidden className="font-mono text-meta leading-tight text-mute tabular-nums">Wk {row.week}</span>
              <span aria-hidden className="truncate text-row leading-tight font-semibold text-ink">{row.opponent}</span>
              <span aria-hidden className={`text-right font-mono text-meta leading-tight tabular-nums ${inside ? "font-semibold text-ink" : "text-mute"}`}>{ordinal(row.rank)}</span>
              <span aria-hidden className="text-right font-mono text-meta leading-tight text-ink-2 tabular-nums">{row.record}</span>
            </motion.li>
          );
        })}
      </ul>
    </div>
  );
}
