/**
 * The NFL game card of a free answer, in the Ledger look: a tug bar of the expected margin from the two DEF projections,
 * a strip of the 32 defenses against a position with the opponent lit, and two pass-share bars against a league mark.
 */
"use client";

import { motion } from "framer-motion";
import { num, oneDecimal, ordinal } from "@cpc/design/format/format";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { z } from "zod";
import { SLOW, SMOOTH, VERY_SLOW, fadeIn, riseIn } from "./motion";

const sideSchema = z.object({ code: z.string(), name: z.string(), projected: z.number() });

export const nflGameBlockSchema = z.object({
  kind: z.literal("nfl_game"),
  week: z.number(),
  title: z.string(),
  sides: z.tuple([sideSchema, sideSchema]),
  margin: z.number(),
  strip: z.object({
    position: z.string().nullable(),
    lit: z.string(),
    average: z.number().nullable(),
    defenses: z.array(z.object({ team: z.string(), allowed: z.number() })),
  }),
  pass_share: z.object({
    league: z.number().nullable(),
    sides: z.array(z.object({ code: z.string(), share: z.number().nullable() })),
  }),
});
export type NflGameBlock = z.infer<typeof nflGameBlockSchema>;

/* A margin of two scores pulls the tug bar to its end, so a close game reads as close and a rout as a rout. */
const FULL_PULL = 14;
/* The height in px of the tallest tick of the strip. */
const STRIP_HEIGHT = 28;

/* The margin in words: "Packers by 3", or "even" for a tie. */
function marginWords(block: NflGameBlock): string {
  if (block.margin === 0) return "even";
  const favorite = block.margin > 0 ? block.sides[0] : block.sides[1];
  return `${favorite.name} by ${num(Math.abs(block.margin))}`;
}

const percent = (share: number) => `${Math.round(share * 100)}%`;

/* The place of the lit defense among the defenses, from 1, the fewest allowed. */
function litPlace(block: NflGameBlock): number {
  return block.strip.defenses.findIndex((row) => row.team === block.strip.lit) + 1;
}

/* The facts of the lit defense: the name of the opponent, and what it allows a game with its place, or null with no
   game yet. */
function litFacts(block: NflGameBlock): { opponent: string; allows: string | null } {
  const lit = block.strip.defenses.find((row) => row.team === block.strip.lit);
  const opponent = block.sides.find((side) => side.code === block.strip.lit)?.name ?? block.strip.lit;
  if (!lit) return { opponent, allows: null };
  const what = block.strip.position ? `${block.strip.position} points` : "points to all positions";
  return { opponent, allows: `${oneDecimal(lit.allowed)} ${what} a game, ${ordinal(litPlace(block))} fewest of ${block.strip.defenses.length}` };
}

function stripWords(block: NflGameBlock): string {
  const { opponent, allows } = litFacts(block);
  return allows === null ? `${opponent} defense: no games yet` : `${opponent} defense allows ${allows}`;
}

/* The card as one short line of plain text, so the turn of the Answer carries it. */
export function nflGameText(block: NflGameBlock): string {
  const [left, right] = block.sides;
  const head = `${block.title}. Projected ${left.name} ${oneDecimal(left.projected)}, ${right.name} ${oneDecimal(right.projected)}: ${marginWords(block)}.`;
  const passes = block.pass_share.sides
    .map((side) => {
      const name = block.sides.find((s) => s.code === side.code)?.name ?? side.code;
      return side.share === null ? null : `${name} pass ${percent(side.share)}`;
    })
    .filter(Boolean)
    .join(", ");
  const league = block.pass_share.league === null ? "" : ` (league ${percent(block.pass_share.league)})`;
  return `${head} ${stripWords(block)}.${passes ? ` ${passes}${league}.` : ""}`;
}

/* The props of a part of the card that rises from a soft blur, or none for a kept card. */
function useRise(live: boolean) {
  const off = useMotionOff();
  return (delay: number) => (live ? riseIn(off, { text: true, delay }) : {});
}

/* The props of a bar that grows along one axis from its anchor. With motion off it only fades in, and a kept card shows
   it at once. */
function useGrow(live: boolean) {
  const off = useMotionOff();
  return (axis: "scaleX" | "scaleY", delay: number) =>
    live ? { initial: off ? { opacity: 0 } : { opacity: 0, [axis]: 0 }, animate: off ? { opacity: 1 } : { opacity: 1, [axis]: 1 }, transition: off ? fadeIn(SLOW, delay) : { duration: SLOW, ease: SMOOTH, delay } } : {};
}

/* One team in the head of the card. The favorite carries the red ink; the other is quiet. */
function Team({ side, favorite, align }: { side: NflGameBlock["sides"][number]; favorite: boolean; align: "left" | "right" }) {
  return (
    <div className={`flex min-w-0 flex-col gap-sp-1 ${align === "right" ? "items-end text-right" : ""}`}>
      <p className={`m-0 max-w-full truncate text-row leading-tight font-semibold ${favorite ? "text-accent-ink" : "text-ink-2"}`}>{side.name}</p>
      <p className={`m-0 text-stat leading-tight tabular-nums ${favorite ? "font-bold text-ink" : "font-semibold text-mute"}`}>{oneDecimal(side.projected)}</p>
    </div>
  );
}

/* The tug bar: a red pull from the center line toward the favorite, as long as the margin against two scores. An even
   game has no pull. */
function Tug({ block, live }: { block: NflGameBlock; live: boolean }) {
  const grow = useGrow(live);
  const words = marginWords(block);
  const width = (Math.min(Math.abs(block.margin), FULL_PULL) / FULL_PULL) * 50;
  const side = block.margin > 0 ? "left" : "right";
  return (
    <div className="flex flex-col gap-sp-1">
      <div role="img" aria-label={`Expected margin: ${block.margin === 0 ? "even game" : words}`} className="relative h-2 rounded-pill bg-rule">
        <span aria-hidden className="absolute inset-y-[-3px] left-1/2 w-px bg-mute" />
        {block.margin !== 0 && (
          <motion.span
            aria-hidden
            data-tug={side}
            className={`absolute inset-y-0 rounded-pill bg-accent ${side === "left" ? "right-1/2 origin-right" : "left-1/2 origin-left"}`}
            style={{ width: `${width}%` }}
            {...grow("scaleX", VERY_SLOW * 0.6)}
          />
        )}
      </div>
      <p className="m-0 text-center font-mono text-meta leading-tight text-mute tabular-nums">{block.margin === 0 ? "Even game" : words}</p>
    </div>
  );
}

/* The strip of the 32 defenses, fewest points allowed on the left. Each tick stands as tall as what its defense allows,
   and only the defense of the opponent is red. The ticks rise from the base line in one quick sweep. */
function DefenseStrip({ block, live }: { block: NflGameBlock; live: boolean }) {
  const grow = useGrow(live);
  const values = block.strip.defenses.map((row) => row.allowed);
  const low = Math.min(...values);
  const span = Math.max(...values) - low || 1;
  const words = stripWords(block);
  const facts = litFacts(block);
  return (
    <div className="flex flex-col gap-sp-1">
      <p className="m-0 font-mono text-meta leading-tight tracking-caps text-mute uppercase">Defense vs {block.strip.position ?? "all positions"}</p>
      <div role="img" aria-label={`${words}.`} className="flex items-end gap-px" style={{ height: STRIP_HEIGHT }}>
        {block.strip.defenses.map((row, index) => {
          const lit = row.team === block.strip.lit;
          // The shortest tick keeps a fifth of the height, so every defense shows on the strip.
          const height = Math.round((0.2 + (0.8 * (row.allowed - low)) / span) * STRIP_HEIGHT);
          return (
            <motion.span
              key={row.team}
              data-defense={row.team}
              className={`block min-w-0 flex-1 origin-bottom rounded-t-[1px] ${lit ? "bg-accent" : "bg-rule"}`}
              style={{ height }}
              {...grow("scaleY", VERY_SLOW * 0.6 + index * 0.008)}
            />
          );
        })}
      </div>
      <p className="m-0 flex justify-between font-mono text-meta leading-tight text-mute">
        <span>Fewest</span>
        <span>Most</span>
      </p>
      <p className="m-0 text-row leading-tight text-ink-2">
        <span className="font-semibold text-accent-ink">{facts.opponent}</span>{" "}
        <span className="tabular-nums">{facts.allows === null ? "have no games yet" : `allow ${facts.allows}`}</span>
      </p>
    </div>
  );
}

/* The pass share of each team as a bar from the left, with a tick at the share of the league. */
function PassShare({ block, live }: { block: NflGameBlock; live: boolean }) {
  const grow = useGrow(live);
  const league = block.pass_share.league;
  return (
    <div className="flex flex-col gap-sp-2">
      <p className="m-0 flex justify-between font-mono text-meta leading-tight tracking-caps text-mute uppercase">
        <span>Pass share</span>
        {league !== null && (
          <span className="flex items-center gap-sp-1 normal-case tracking-normal">
            <span aria-hidden className="inline-block h-sp-3 w-px bg-ink" />
            League {percent(league)}
          </span>
        )}
      </p>
      {block.pass_share.sides.map((side, index) => {
        const name = block.sides.find((s) => s.code === side.code)?.name ?? side.code;
        if (side.share === null) return null;
        const label = `${name} pass ${percent(side.share)} of plays${league === null ? "" : `, against ${percent(league)} for the league`}`;
        return (
          <div key={side.code} className="grid grid-cols-[5.5rem_minmax(0,1fr)_2.75rem] items-center gap-x-sp-2">
            <span className="truncate text-row leading-tight text-ink-2">{name}</span>
            <span role="img" aria-label={label} className="relative block h-1.5 rounded-pill bg-rule">
              <motion.span aria-hidden className="absolute inset-y-0 left-0 origin-left rounded-pill bg-mute" style={{ width: `${side.share * 100}%` }} {...grow("scaleX", VERY_SLOW * 0.6 + 0.08 * (index + 1))} />
              {league !== null && <span aria-hidden data-league-mark className="absolute inset-y-[-4px] w-px bg-ink" style={{ left: `${league * 100}%` }} />}
            </span>
            <span className="text-right font-mono text-row leading-tight text-ink tabular-nums">{percent(side.share)}</span>
          </div>
        );
      })}
    </div>
  );
}

/* The card: the title and the two teams with their projected points, the tug bar, the strip, and the pass share. */
export function NflGameView({ block, live }: { block: NflGameBlock; live: boolean }) {
  const rise = useRise(live);
  const [left, right] = block.sides;
  return (
    <div role="group" aria-label={block.title} className="flex min-w-0 flex-col gap-sp-4" data-block="nfl_game">
      <motion.div className="flex flex-col gap-sp-3" {...rise(VERY_SLOW * 0.6)}>
        <p className="m-0 truncate font-mono text-meta leading-tight tracking-caps text-mute uppercase">{block.title} · Projected</p>
        <div className="grid grid-cols-2 items-end gap-x-sp-4">
          <Team side={left} favorite={block.margin > 0} align="left" />
          <Team side={right} favorite={block.margin < 0} align="right" />
        </div>
        <Tug block={block} live={live} />
      </motion.div>
      <motion.div className="border-t border-rule pt-sp-3" {...rise(VERY_SLOW * 0.6 + 0.08)}>
        <DefenseStrip block={block} live={live} />
      </motion.div>
      <motion.div className="border-t border-rule pt-sp-3" {...rise(VERY_SLOW * 0.6 + 0.16)}>
        <PassShare block={block} live={live} />
      </motion.div>
    </div>
  );
}
