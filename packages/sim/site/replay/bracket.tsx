/**
 * The bracket of the replay: one column per round that slides in from the left, with its game cards, its bye plates,
 * and the line out of each card. A decided game counts its scores up, sweeps a red bar under the winner, lights its
 * line, and the winner chip slides along it into its seat in the next round.
 */
"use client";

import { animate, motion } from "framer-motion";
import { useEffect, useRef } from "react";
import { oneDecimal } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { enter, type Pace, SPRING } from "./pace";
import type { BracketGame, BracketTeam, ReplayRound } from "./season";

/* The count-up of a score, in seconds. */
const COUNT = 0.6;

/* A score that counts up from zero once, when `live`. Otherwise it shows the score at rest. */
function Score({ value, live }: { value: number; live: boolean }) {
  const box = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    if (!live || box.current === null) return;
    const node = box.current;
    const controls = animate(0, value, { duration: COUNT, ease: "easeOut", onUpdate: (v) => (node.textContent = oneDecimal(v)) });
    return () => controls.stop();
  }, [live, value]);
  return (
    <span ref={box} className="font-mono text-meta font-bold tabular-nums">
      {oneDecimal(value)}
    </span>
  );
}

/* The red seed chip of a team. The chip of a winner slides into its seat in the next round, so the chip of the seat
   and the chip of the winner share one layout id. */
function Chip({ team, flight, pace }: { team: { roster_id: number; seed: number }; flight?: string; pace: Pace }) {
  const moving = !pace.off && !pace.still;
  return (
    <motion.span
      layoutId={moving ? flight : undefined}
      transition={SPRING}
      className="inline-flex size-sp-6 flex-none items-center justify-center rounded-sm bg-accent font-mono text-meta font-bold text-white"
    >
      {team.seed}
    </motion.span>
  );
}

function TeamRow({
  team,
  decided,
  won,
  live,
  flight,
  pace,
}: {
  team: BracketTeam;
  decided: boolean;
  won: boolean;
  live: boolean;
  // The layout id of the chip, when the team came from a game of the round before.
  flight?: string;
  pace: Pace;
}) {
  return (
    <div className={cn("relative flex items-center gap-sp-2 py-sp-1", decided && !won ? "text-on-dark-muted" : "text-on-dark")}>
      <Chip team={team} flight={flight} pace={pace} />
      <span className="min-w-0 flex-1 truncate text-meta leading-tight font-semibold">{team.name}</span>
      {decided ? <Score value={team.score} live={live} /> : <span className="font-mono text-meta text-on-dark-muted">–</span>}
      {decided && won && (
        // The red bar sweeps under the winner after the count-up.
        <motion.span
          aria-hidden="true"
          {...enter(pace, { scaleX: 0 }, { duration: 0.5, delay: live ? COUNT : 0 })}
          className="absolute inset-x-0 bottom-0 h-0.5 origin-left bg-accent"
        />
      )}
    </div>
  );
}

/* The line out of a card toward the next round: to the right when the stage is wide enough for three columns, and down
   when the rounds stack. It draws in with its card and lights red once the game has a winner. */
function Line({ lit, last, pace }: { lit: boolean; last: boolean; pace: Pace }) {
  if (last) return null;
  const color = lit ? "bg-accent" : "bg-rule-dark";
  return (
    <>
      <motion.span
        aria-hidden="true"
        {...enter(pace, { scaleX: 0 }, { duration: 0.4, delay: 0.3 })}
        className={cn("absolute top-1/2 left-full hidden h-0.5 w-sp-3 origin-left transition-colors duration-300 @xl:block", color)}
      />
      <motion.span
        aria-hidden="true"
        {...enter(pace, { scaleY: 0 }, { duration: 0.4, delay: 0.3 })}
        className={cn("absolute top-full left-1/2 h-sp-2 w-0.5 origin-top transition-colors duration-300 @xl:hidden", color)}
      />
    </>
  );
}

function Game({
  game,
  decided,
  live,
  last,
  arrived,
  departed,
  round,
  pace,
}: {
  game: BracketGame;
  decided: boolean;
  live: boolean;
  last: boolean;
  // The seats whose chip slid in from the round before, by roster ID.
  arrived: Set<number>;
  // True while the winner chip waits in this card, before the next round draws in.
  departed: boolean;
  round: number;
  pace: Pace;
}) {
  const { high, low, winner } = game;
  const flight = (rid: number) => (arrived.has(rid) ? `seat-${round - 1}-${rid}` : undefined);
  return (
    <div
      role="group"
      aria-label={`Seed ${high.seed} ${high.name} against seed ${low.seed} ${low.name}`}
      data-winner={decided ? winner : undefined}
      className="relative rounded-tile border border-rule-dark bg-chip-dark px-sp-2 py-sp-1"
    >
      {[high, low].map((team) => (
        <TeamRow
          key={team.roster_id}
          team={team}
          decided={decided}
          won={winner === team.roster_id}
          live={live}
          flight={flight(team.roster_id)}
          pace={pace}
        />
      ))}
      {decided && departed && (
        // The winner chip waits at the edge of the card until the next round draws in, then flies to its seat there.
        <span className="absolute top-1/2 right-0 translate-x-1/2 -translate-y-1/2" aria-hidden="true">
          <Chip team={winner === high.roster_id ? high : low} flight={`seat-${round}-${winner}`} pace={pace} />
        </span>
      )}
      <Line lit={decided} last={last} pace={pace} />
    </div>
  );
}

export function Bracket({
  rounds,
  shown,
  decided,
  live,
  pace,
}: {
  rounds: ReplayRound[];
  // The count of rounds that show.
  shown: number;
  // The count of rounds with a result.
  decided: number;
  // True when the last decided round counts its scores up now.
  live: boolean;
  pace: Pace;
}) {
  // The stage sits beside the odds on a desktop, so the rounds take columns by the width of the stage, not of the page.
  return (
    <div className="@container">
      <ol aria-label="Bracket" className="m-0 grid list-none gap-sp-4 p-0 @xl:grid-cols-3 @xl:gap-sp-3">
        {rounds.slice(0, shown).map((round, r) => {
          const last = r === rounds.length - 1;
          const arrived = new Set(r === 0 ? [] : rounds[r - 1].games.map((game) => game.winner));
          return (
            <motion.li
              key={round.label}
              aria-label={`${round.label}, week ${round.week}`}
              {...enter(pace, { x: -24 }, { duration: 0.5 })}
              className="flex flex-col gap-sp-3"
            >
              <div className="flex items-baseline justify-between gap-sp-2">
                <span className="font-mono text-meta font-bold tracking-caps text-on-dark uppercase">{round.label}</span>
                <span className="font-mono text-meta text-on-dark-muted">{`Wk ${round.week}`}</span>
              </div>
              {/* The cards of a later round sit between the cards of the round before, as in a printed bracket. */}
              <div className="flex flex-1 flex-col justify-around gap-sp-3">
                {round.games.map((game) => (
                  <Game
                    key={`${game.high.roster_id}-${game.low.roster_id}`}
                    game={game}
                    decided={r < decided}
                    live={live && r === decided - 1}
                    last={last}
                    arrived={arrived}
                    departed={r === shown - 1 && r < decided && !last}
                    round={r}
                    pace={pace}
                  />
                ))}
                {round.byes.map((team) => (
                  <div
                    key={team.roster_id}
                    className="flex items-center gap-sp-2 rounded-tile border border-dashed border-rule-dark px-sp-2 py-sp-2 text-on-dark"
                  >
                    <Chip team={team} pace={pace} />
                    <span className="min-w-0 flex-1 truncate text-meta leading-tight font-semibold">{team.name}</span>
                    <span className="font-mono text-meta font-bold tracking-caps text-on-dark-2">BYE</span>
                  </div>
                ))}
              </div>
            </motion.li>
          );
        })}
      </ol>
    </div>
  );
}
