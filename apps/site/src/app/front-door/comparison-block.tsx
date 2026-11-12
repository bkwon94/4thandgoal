/**
 * The comparison block of a typed "Start A or B?", in the Ledger look: one pair of bars from a center line for each fact,
 * the side that wins a fact in red, a dot on each fact that the checked text cites, and the pick under them.
 */
"use client";

import { motion } from "framer-motion";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { z } from "zod";
import { SLOW, SMOOTH, STAGGER, VERY_SLOW, fadeIn, riseIn, staggerOf } from "./motion";

const playerSchema = z.object({
  name: z.string(),
  player_id: z.string(),
  position: z.string(),
  nfl_team: z.string().nullable(),
  opponent: z.string().nullable(),
  // The kickoff in epoch ms, UTC.
  kickoff: z.number().nullable(),
  projection: z.number().nullable(),
  // The Sleeper injury status, or the reason he cannot play, such as Bye.
  status: z.string().nullable(),
});

const side = z.union([z.literal(0), z.literal(1)]);

const factSchema = z.object({
  key: z.string(),
  label: z.string(),
  values: z.tuple([z.number().nullable(), z.number().nullable()]),
  shown: z.tuple([z.string().nullable(), z.string().nullable()]),
  // The side that wins the fact, or null for a tie or a fact with no side that wins.
  winner: side.nullable(),
  // The checked text gives the number of this fact. The block from code, before the check, cites none.
  cited: z.boolean(),
});

export const comparisonBlockSchema = z.object({
  kind: z.literal("comparison"),
  topic: z.literal("start_sit"),
  team: z.number(),
  week: z.number(),
  players: z.tuple([playerSchema, playerSchema]),
  facts: z.array(factSchema),
  // The player to start, or null when neither can play.
  pick: side.nullable(),
});
export type ComparisonBlock = z.infer<typeof comparisonBlockSchema>;
type Fact = ComparisonBlock["facts"][number];

/* The pick as the block closes on it: "Start K. Mumpfield.", or the line for two players who cannot play. */
export function pickLine(block: ComparisonBlock): string {
  if (block.pick === null) return "Neither can play this week.";
  const name = block.players[block.pick].name;
  // A name such as "K. Pitts Sr." ends the sentence with its own period.
  return `Start ${name}${name.endsWith(".") ? "" : "."}`;
}

const shownOf = (value: string | null) => value ?? "none";

/* The block as one short line of plain text, so the turn of the Answer carries it. */
export function comparisonText(block: ComparisonBlock): string {
  const [left, right] = block.players;
  const facts = block.facts.map((fact) => `${fact.label} ${shownOf(fact.shown[0])} to ${shownOf(fact.shown[1])}`);
  return `${left.name} or ${right.name}, week ${block.week}: ${facts.join("; ")}. ${pickLine(block)}`;
}

/* The length of each bar of a fact, from 0 to 1 of its half. The longer value fills its half, and a value below 0, such
   as a margin, sits on a floor at the lowest value. */
function lengths(fact: Fact): [number, number] {
  const [a, b] = fact.values.map((value) => value ?? 0);
  const low = Math.min(0, a, b);
  const span = Math.max(a, b) - low || 1;
  return [(a - low) / span, (b - low) / span];
}

function factWords(block: ComparisonBlock, fact: Fact): string {
  const [left, right] = block.players;
  const wins = fact.winner === null ? "Neither side wins it." : `${block.players[fact.winner].name} wins it.`;
  return `${fact.label}: ${left.name} ${shownOf(fact.shown[0])}, ${right.name} ${shownOf(fact.shown[1])}. ${wins}`;
}

/* One player at the head of the block. The pick carries the red ink, and the other player is quiet. */
function Head({ player, picked, align }: { player: ComparisonBlock["players"][number]; picked: boolean; align: "left" | "right" }) {
  const game = [player.position, player.nfl_team, player.opponent && `vs ${player.opponent}`].filter(Boolean).join(" ");
  return (
    <div className={`flex min-w-0 flex-col gap-sp-1 ${align === "right" ? "items-end text-right" : ""}`}>
      <p className={`m-0 max-w-full truncate text-row leading-tight font-semibold ${picked ? "text-accent-ink" : "text-ink-2"}`}>{player.name}</p>
      <p className="m-0 max-w-full truncate font-mono text-meta leading-tight text-mute">
        {game}
        {player.status && <span className="text-ink-2"> · {player.status}</span>}
      </p>
    </div>
  );
}

/* One fact: its label with the dot of a cited fact, then the two values at the outer ends and the two bars that grow
   out from the center line. The bars grow on the stagger of the rows, and with motion off they only fade in. */
function FactRow({ block, fact, index, live }: { block: ComparisonBlock; fact: Fact; index: number; live: boolean }) {
  const off = useMotionOff();
  const delay = VERY_SLOW * 0.6 + staggerOf(index + 1);
  const grow = live ? { initial: off ? { opacity: 0 } : { opacity: 0, scaleX: 0 }, animate: off ? { opacity: 1 } : { opacity: 1, scaleX: 1 }, transition: off ? fadeIn(SLOW, delay) : { duration: SLOW, ease: SMOOTH, delay: delay + STAGGER } } : {};
  const rise = live ? riseIn(off, { delay }) : {};
  const size = lengths(fact);
  return (
    <motion.li data-fact={fact.key} className="flex flex-col gap-sp-1 border-b border-rule py-sp-2 last:border-b-0" {...rise}>
      <p className="m-0 flex items-center justify-center gap-sp-1 font-mono text-meta leading-tight tracking-caps text-mute uppercase">
        {fact.cited && <span data-cited aria-label="Cited" role="img" className="inline-block size-1.5 flex-none rounded-full bg-accent" />}
        {fact.label}
      </p>
      <div role="img" aria-label={factWords(block, fact)} className="grid grid-cols-[3rem_minmax(0,1fr)_minmax(0,1fr)_3rem] items-center gap-x-sp-2">
        <span aria-hidden className={`font-mono text-row leading-tight tabular-nums ${fact.winner === 0 ? "font-semibold text-ink" : "text-mute"}`}>{shownOf(fact.shown[0])}</span>
        {([0, 1] as const).map((at) => (
          <span key={at} aria-hidden className={`relative block h-2 ${at === 0 ? "border-r" : "border-l"} border-mute`}>
            <motion.span
              data-side={at}
              className={`absolute inset-y-0 rounded-pill ${at === 0 ? "right-0 origin-right" : "left-0 origin-left"} ${fact.winner === at ? "bg-accent" : "bg-rule"}`}
              style={{ width: `${size[at] * 100}%` }}
              {...grow}
            />
          </span>
        ))}
        <span aria-hidden className={`text-right font-mono text-row leading-tight tabular-nums ${fact.winner === 1 ? "font-semibold text-ink" : "text-mute"}`}>{shownOf(fact.shown[1])}</span>
      </div>
    </motion.li>
  );
}

/* The block: the two players, one row per fact, and the pick. */
export function ComparisonView({ block, live }: { block: ComparisonBlock; live: boolean }) {
  const off = useMotionOff();
  const [left, right] = block.players;
  const rise = (delay: number) => (live ? riseIn(off, { text: true, delay }) : {});
  return (
    <div role="group" aria-label={`${left.name} or ${right.name}`} className="flex min-w-0 flex-col gap-sp-3" data-block="comparison">
      <motion.div className="grid grid-cols-2 items-end gap-x-sp-4" {...rise(VERY_SLOW * 0.6)}>
        <Head player={left} picked={block.pick === 0} align="left" />
        <Head player={right} picked={block.pick === 1} align="right" />
      </motion.div>
      <ul className="m-0 flex list-none flex-col border-t border-rule p-0">
        {block.facts.map((fact, index) => (
          <FactRow key={fact.key} block={block} fact={fact} index={index} live={live} />
        ))}
      </ul>
      <motion.p className="m-0 text-stat leading-tight font-bold text-ink" {...rise(VERY_SLOW * 0.6 + staggerOf(block.facts.length + 1))}>
        {pickLine(block)}
      </motion.p>
    </div>
  );
}
