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
import { stableId } from "@cpc/design/lib/stable-id";

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
    <span ref={box} data-score className="font-mono text-meta font-bold tabular-nums">
      {oneDecimal(value)}
    </span>
  );
}

/* The red seed chip of a team. The chip of a winner slides into its seat in the next round, so the chip of the seat
   and the chip of the winner share one layout id. The stable id names the round and the team, so a frame of the
   replay keeps it. */
function Chip({ team, round, flight, pace }: { team: { roster_id: number; seed: number }; round: number; flight?: string; pace: Pace }) {
  const moving = !pace.off && !pace.still;
  return (
    <motion.span
      {...stableId("bracket", round, team.roster_id)}
      layoutId={moving ? flight : undefined}
      transition={SPRING}
      className="inline-flex size-sp-6 flex-none items-center justify-center rounded-report bg-accent font-mono text-meta font-bold text-white"
    >
      {team.seed}
    </motion.span>
  );
}

function TeamRow({
  team,
  round,
  decided,
  won,
  live,
  flight,
  pace,
}: {
  team: BracketTeam;
  round: number;
  decided: boolean;
  won: boolean;
  live: boolean;
  // The layout id of the chip, when the team came from a game of the round before.
  flight?: string;
  pace: Pace;
}) {
  return (
    <div className={cn("relative flex items-center gap-sp-2 py-sp-1", decided && !won ? "text-on-dark-muted" : "text-on-dark")}>
      <Chip team={team} round={round} flight={flight} pace={pace} />
      {/* A long name wraps between its words, so each name shows in full in the narrow columns of three rounds. */}
      <span data-team-name className="min-w-0 flex-1 text-meta leading-tight font-semibold">
        {team.name}
      </span>
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
   when the rounds stack. It spans the whole gap to the next card, where the winner chip waits. It draws in with its
   card and lights red once the game has a winner. */
function Line({ lit, last, pace }: { lit: boolean; last: boolean; pace: Pace }) {
  if (last) return null;
  const color = lit ? "bg-accent" : "bg-rule-dark";
  return (
    <>
      <motion.span
        aria-hidden="true"
        {...enter(pace, { scaleX: 0 }, { duration: 0.4, delay: 0.3 })}
        className={cn("absolute top-1/2 left-full hidden h-0.5 w-sp-6 origin-left transition-colors duration-300 @xl:block", color)}
      />
      <motion.span
        aria-hidden="true"
        {...enter(pace, { scaleY: 0 }, { duration: 0.4, delay: 0.3 })}
        className={cn("absolute top-full left-1/2 h-sp-6 w-0.5 origin-top transition-colors duration-300 @xl:hidden", color)}
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
      className="relative rounded-report border border-rule-dark bg-chip-dark px-sp-2 py-sp-1"
    >
      {[high, low].map((team) => (
        <TeamRow
          key={team.roster_id}
          team={team}
          round={round}
          decided={decided}
          won={winner === team.roster_id}
          live={live}
          flight={flight(team.roster_id)}
          pace={pace}
        />
      ))}
      {decided && departed && (
        // The winner chip waits in the gap past the card until the next round draws in, then flies to its seat there.
        // The gap is as wide as the chip, so the chip covers no name or score.
        <span
          data-departed
          aria-hidden="true"
          className="absolute top-full left-1/2 -translate-x-1/2 @xl:top-1/2 @xl:left-full @xl:translate-x-0 @xl:-translate-y-1/2"
        >
          <Chip team={winner === high.roster_id ? high : low} round={round + 1} flight={`seat-${round}-${winner}`} pace={pace} />
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
  // The rounds take columns by the width of the stage, not of the page. Each gap between cards fits the chip of a
  // winner, so the waiting chip covers no card.
  return (
    <div className="@container">
      <ol aria-label="Bracket" className="m-0 grid list-none gap-sp-6 p-0 @xl:grid-cols-3">
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
              <div className="flex flex-1 flex-col justify-around gap-sp-6 @xl:gap-sp-3">
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
                    className="flex items-center gap-sp-2 rounded-report border border-dashed border-rule-dark px-sp-2 py-sp-2 text-on-dark"
                  >
                    <Chip team={team} round={r} pace={pace} />
                    {/* A long name wraps between its words, so each name shows in full in the narrow columns of three rounds. */}
      <span data-team-name className="min-w-0 flex-1 text-meta leading-tight font-semibold">
        {team.name}
      </span>
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
