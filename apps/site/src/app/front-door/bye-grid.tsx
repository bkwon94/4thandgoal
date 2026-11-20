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

const weekSpan = (weeks: number[]) =>
  weeks.length > 1 ? `weeks ${weeks[0]} to ${weeks[weeks.length - 1]}` : `week ${weeks[0]}`;

export function byeGridText(block: ByeGridBlock): string {
  const out = block.players.filter(
    (player) => player.bye !== null && block.weeks.includes(player.bye),
  );
  const starters = out
    .filter((player) => player.starter)
    .map((player) => `${player.name} week ${player.bye}`);
  const bench = out
    .filter((player) => !player.starter)
    .map((player) => `${player.name} week ${player.bye}`);
  return `Byes, ${weekSpan(block.weeks)}. Starters: ${starters.join(", ") || "none"}. Bench: ${bench.join(", ") || "none"}.`;
}

/* One dot of the grid. A starter in his bye week gets the red dot, the bench in his bye week a gray ring, and every
   other week a faint dot, so each column still reads as a week. The red dot settles in from a small scale. */
function Dot({
  player,
  week,
  live,
  delay,
}: {
  player: ByePlayer;
  week: number;
  live: boolean;
  delay: number;
}) {
  const off = useMotionOff();
  const out = player.bye === week;
  if (!out) return <span aria-hidden className="size-sp-1 bg-rule block rounded-full" />;
  const pop = live && !off && player.starter;
  return (
    <>
      <motion.span
        aria-hidden
        className={`block rounded-full ${player.starter ? "size-sp-3 bg-accent" : "size-sp-3 border-mute border-2"}`}
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
  const enter = (index: number) =>
    live ? riseIn(off, { delay: VERY_SLOW * 0.4 + staggerOf(index) }) : {};
  const firstBench = block.players.findIndex((player) => !player.starter);
  return (
    <div className="gap-sp-2 flex min-w-0 flex-col" data-block="bye_grid">
      <motion.div
        className="gap-x-sp-4 gap-y-sp-1 flex flex-wrap items-center justify-between"
        {...enter(0)}
      >
        <p className="text-meta tracking-caps text-mute m-0 font-mono leading-tight uppercase">
          {title}
        </p>
        <p
          aria-hidden
          className="gap-sp-3 text-meta text-mute m-0 flex items-center font-mono leading-tight"
        >
          <span className="gap-sp-1 flex items-center">
            <span className="size-sp-2 bg-accent block rounded-full" />
            Starter
          </span>
          <span className="gap-sp-1 flex items-center">
            <span className="size-sp-2 border-mute block rounded-full border-2" />
            Bench
          </span>
        </p>
      </motion.div>
      <table aria-label={title} className="border-rule w-full table-fixed border-collapse border-t">
        <colgroup>
          <col />
          {block.weeks.map((week) => (
            <col key={week} className="w-sp-6 sm:w-touch" />
          ))}
        </colgroup>
        <thead>
          <tr className="border-rule border-b">
            <th
              scope="col"
              className="py-sp-2 text-meta tracking-caps text-mute text-left font-mono leading-tight font-normal uppercase"
            >
              Player
            </th>
            {block.weeks.map((week) => (
              <th
                key={week}
                scope="col"
                className="py-sp-2 text-meta text-mute text-center font-mono leading-tight font-normal tabular-nums"
              >
                {week}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {block.players.map((player, index) => (
            <motion.tr
              key={`${player.name}-${index}`}
              className={`border-rule border-b last:border-b-0 ${index === firstBench && index > 0 ? "border-t-rule border-t-2" : ""}`}
              {...enter(index + 1)}
            >
              <th
                scope="row"
                data-name={player.name}
                className="py-sp-2 pr-sp-2 text-left font-normal"
              >
                <span className="gap-sp-2 flex min-w-0 items-baseline">
                  <span className="text-label tracking-caps text-mute w-[2.25rem] flex-none font-mono leading-tight uppercase">
                    {player.slot ?? "BN"}
                  </span>
                  <span
                    title={player.name}
                    className={`text-row truncate leading-tight ${player.starter ? "text-ink font-semibold" : "text-ink-2"}`}
                  >
                    {player.name}
                  </span>
                </span>
              </th>
              {block.weeks.map((week) => (
                <td key={week} className="py-sp-2">
                  <span className="flex items-center justify-center">
                    <Dot
                      player={player}
                      week={week}
                      live={live}
                      delay={VERY_SLOW + staggerOf(index)}
                    />
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
