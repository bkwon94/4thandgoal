/**
 * The bye grid of Weak spots: a dot matrix of the starters and the bench against the next weeks, with a red dot for a
 * starter in his bye week. It holds the schema of the block, its short text, and its view.
 */
"use client";

import { motion } from "framer-motion";
import { z } from "zod";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { FAST, VERY_SLOW, fadeIn, riseIn, staggerOf } from "./motion";

export const byeGridBlockSchema = z.object({
  kind: z.literal("bye_grid"),
  weeks: z.array(z.number()),
  players: z.array(
    z.object({
      name: z.string(),
      position: z.string(),
      nfl_team: z.string().nullable(),
      slot: z.string().nullable(),
      starter: z.boolean(),
      bye: z.number().nullable(),
    }),
  ),
});
export type ByeGridBlock = z.infer<typeof byeGridBlockSchema>;
type ByePlayer = ByeGridBlock["players"][number];

/* The words of each dot for a screen reader, so the grid never rests on color alone. */
export const STARTER_BYE = "Starter on a bye";
export const BENCH_BYE = "Bench on a bye";

const weekSpan = (weeks: number[]) => (weeks.length > 1 ? `weeks ${weeks[0]} to ${weeks[weeks.length - 1]}` : `week ${weeks[0]}`);

export function byeGridText(block: ByeGridBlock): string {
  const out = block.players.filter((player) => player.bye !== null && block.weeks.includes(player.bye));
  const starters = out.filter((player) => player.starter).map((player) => `${player.name} week ${player.bye}`);
  const bench = out.filter((player) => !player.starter).map((player) => `${player.name} week ${player.bye}`);
  return `Byes, ${weekSpan(block.weeks)}. Starters: ${starters.join(", ") || "none"}. Bench: ${bench.join(", ") || "none"}.`;
}

/* One dot of the grid. A starter in his bye week gets the red dot, the bench in his bye week a gray ring, and every
   other week a faint dot, so each column still reads as a week. The red dot settles in from a small scale. */
function Dot({ player, week, live, delay }: { player: ByePlayer; week: number; live: boolean; delay: number }) {
  const off = useMotionOff();
  const out = player.bye === week;
  if (!out) return <span aria-hidden className="block size-sp-1 rounded-full bg-rule" />;
  const pop = live && !off && player.starter;
  return (
    <>
      <motion.span
        aria-hidden
        className={`block rounded-full ${player.starter ? "size-sp-3 bg-accent" : "size-sp-3 border-2 border-mute"}`}
        initial={pop ? { opacity: 0, scale: 0.5 } : live ? { opacity: 0 } : false}
        animate={{ opacity: 1, scale: 1 }}
        transition={fadeIn(FAST, delay)}
      />
      <span className="sr-only">{player.starter ? STARTER_BYE : BENCH_BYE}</span>
    </>
  );
}

export function ByeGridView({ block, live }: { block: ByeGridBlock; live: boolean }) {
  const off = useMotionOff();
  const title = `Byes, ${weekSpan(block.weeks)}`;
  const enter = (index: number) => (live ? riseIn(off, { delay: VERY_SLOW * 0.4 + staggerOf(index) }) : {});
  const firstBench = block.players.findIndex((player) => !player.starter);
  return (
    <div className="flex min-w-0 flex-col gap-sp-2" data-block="bye_grid">
      <motion.div className="flex flex-wrap items-center justify-between gap-x-sp-4 gap-y-sp-1" {...enter(0)}>
        <p className="m-0 font-mono text-meta leading-tight tracking-caps text-mute uppercase">{title}</p>
        <p aria-hidden className="m-0 flex items-center gap-sp-3 font-mono text-meta leading-tight text-mute">
          <span className="flex items-center gap-sp-1">
            <span className="block size-sp-2 rounded-full bg-accent" />
            Starter
          </span>
          <span className="flex items-center gap-sp-1">
            <span className="block size-sp-2 rounded-full border-2 border-mute" />
            Bench
          </span>
        </p>
      </motion.div>
      <table aria-label={title} className="w-full table-fixed border-collapse border-t border-rule">
        <colgroup>
          <col />
          {block.weeks.map((week) => (
            <col key={week} className="w-sp-6 sm:w-touch" />
          ))}
        </colgroup>
        <thead>
          <tr className="border-b border-rule">
            <th scope="col" className="py-sp-2 text-left font-mono text-meta leading-tight font-normal tracking-caps text-mute uppercase">
              Player
            </th>
            {block.weeks.map((week) => (
              <th key={week} scope="col" className="py-sp-2 text-center font-mono text-meta leading-tight font-normal text-mute tabular-nums">
                {week}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {block.players.map((player, index) => (
            <motion.tr
              key={`${player.name}-${index}`}
              className={`border-b border-rule last:border-b-0 ${index === firstBench && index > 0 ? "border-t-2 border-t-rule" : ""}`}
              {...enter(index + 1)}
            >
              <th scope="row" data-name={player.name} className="py-sp-2 pr-sp-2 text-left font-normal">
                <span className="flex min-w-0 items-baseline gap-sp-2">
                  <span className="w-[2.25rem] flex-none font-mono text-label leading-tight tracking-caps text-mute uppercase">{player.slot ?? "BN"}</span>
                  <span title={player.name} className={`truncate text-row leading-tight ${player.starter ? "font-semibold text-ink" : "text-ink-2"}`}>
                    {player.name}
                  </span>
                </span>
              </th>
              {block.weeks.map((week) => (
                <td key={week} className="py-sp-2">
                  <span className="flex items-center justify-center">
                    <Dot player={player} week={week} live={live} delay={VERY_SLOW + staggerOf(index)} />
                  </span>
                </td>
              ))}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
