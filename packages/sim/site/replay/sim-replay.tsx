/**
 * The sim replay: each press of "Sim the season" plays one stored run of the sim in the Broadcast motion, from week 9
 * to a champion, above the odds of all runs. It reads only the sim file; the reader never picks the winner of a game.
 */
"use client";

import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { thousands } from "@cpc/design/format/format";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { Sim } from "../schema/sim-types";
import { type Beat, beatsOf } from "./beats";
import { Bracket } from "./bracket";
import { ChampionCard } from "./champion-card";
import { LowerThird } from "./lower-third";
import { Odds } from "./odds";
import type { Pace } from "./pace";
import { replaySeason, type ReplaySeason } from "./season";
import { Standings } from "./standings";
import { WeekStrip } from "./week-strip";

/* The run on the stage. A new press gives a new take, so the stage mounts fresh and no part of the old run stays. */
type Play = { run: number; take: number; step: number; still: boolean; card: boolean };

/* A random run of the stored runs, so two managers see different endings. */
const randomRun = (count: number) => Math.floor(Math.random() * count);

const BUTTON = "min-h-touch rounded-pill px-sp-4 font-mono text-meta font-bold tracking-caps uppercase";

/* The week of the strip at a beat: the regular week, the last regular week through the split, then the bracket week. */
function weekAt(season: ReplaySeason, beat: Beat): number {
  if (beat.kind === "week") return season.weeks[beat.index].week;
  if (beat.kind === "split" || beat.kind === "final") return season.weeks.at(-1)!.week;
  if (beat.kind === "champion") return season.rounds.at(-1)!.week;
  return season.rounds[beat.index].week;
}

/* The line a screen reader hears at each beat. */
function sayAt(season: ReplaySeason, beat: Beat): string {
  switch (beat.kind) {
    case "week":
      return `Week ${season.weeks[beat.index].week} final`;
    case "split":
      return "Playoffs";
    case "final":
      return "Final standings";
    case "draw":
      return season.rounds[beat.index].label;
    case "result":
      return `${season.rounds[beat.index].label} results`;
    case "champion":
      return `${season.champion.name} wins the title in this run`;
  }
}

/* The red PLAYOFFS band of the split. It wipes in from the left, holds, and wipes off to the right. Only the band
   scales; its text fades, so the text never stretches. Under reduced motion the band only fades in and out. */
function PlayoffsBand({ pace }: { pace: Pace }) {
  const times = [0, 0.25, 0.75, 1];
  const band = pace.off
    ? { initial: { opacity: 0 }, animate: { opacity: [0, 1, 1, 0] } }
    : { initial: { scaleX: 0, originX: 0 }, animate: { scaleX: [0, 1, 1, 0], originX: [0, 0, 1, 1] } };
  return (
    <div className="pointer-events-none absolute inset-x-0 top-1/3 z-10 flex h-[5rem] items-center justify-center">
      <motion.span aria-hidden="true" className="absolute inset-0 bg-accent" {...band} transition={{ duration: 1.6, times }} />
      <motion.span
        className="relative font-mono text-headline leading-tight font-bold tracking-wide text-white"
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 1, 1, 0] }}
        transition={{ duration: 1.6, times: [0, 0.3, 0.7, 0.95] }}
      >
        PLAYOFFS
      </motion.span>
    </div>
  );
}

function Stage({
  season,
  beat,
  play,
  runs,
  pace,
  onClose,
}: {
  season: ReplaySeason;
  beat: Beat;
  play: Play;
  // The count of all runs of the sim.
  runs: number;
  pace: Pace;
  onClose: () => void;
}) {
  const spots = season.seeds.length;
  const final = season.weeks.at(-1)!.standings;
  if (beat.kind === "week") {
    const week = season.weeks[beat.index];
    return (
      <div className="flex flex-col gap-sp-3">
        <Standings rows={week.standings} label="Standings" pace={pace} />
        <LowerThird key={week.week} week={week} pace={pace} />
      </div>
    );
  }
  if (beat.kind === "split" || beat.kind === "final") {
    return (
      <>
        <Standings rows={final} label="Final standings" pace={pace} marks={{ spots, byes: season.byes }} />
        {beat.kind === "split" && !pace.still && <PlayoffsBand pace={pace} />}
      </>
    );
  }
  const shown = beat.kind === "champion" ? season.rounds.length : beat.index + 1;
  const decided = beat.kind === "draw" ? beat.index : shown;
  return (
    <>
      <Bracket rounds={season.rounds} shown={shown} decided={decided} live={beat.kind === "result" && !pace.still} pace={pace} />
      {beat.kind === "champion" && play.card && (
        <ChampionCard champion={season.champion} runs={runs} pace={pace} onClose={onClose} />
      )}
    </>
  );
}

export function SimReplay({
  sim,
  pick = randomRun,
}: {
  sim: Sim;
  // Picks the index of the run to play from the count of stored runs. A test passes its own pick.
  pick?: (count: number) => number;
}) {
  const off = useMotionOff();
  const [play, setPlay] = useState<Play | null>(null);
  const run = play?.run ?? null;
  const season = useMemo(() => (run === null ? null : replaySeason(sim, run)), [sim, run]);
  const beats = useMemo(() => (season === null ? [] : beatsOf(season)), [season]);
  const beat = play === null ? null : beats[play.step];
  const running = play !== null && play.step < beats.length - 1;

  // Each beat holds for its time, then the next beat starts. A new take or a skip clears the clock of the old one.
  useEffect(() => {
    if (play === null || play.step >= beats.length - 1) return;
    const timer = setTimeout(() => {
      setPlay((now) => (now !== null && now.take === play.take ? { ...now, step: now.step + 1 } : now));
    }, beats[play.step].ms);
    return () => clearTimeout(timer);
  }, [play, beats]);

  const press = () => {
    const next = pick(sim.sample.length);
    setPlay((now) => ({ run: next, take: (now?.take ?? 0) + 1, step: 0, still: false, card: true }));
  };
  const skip = () => setPlay((now) => (now === null ? now : { ...now, step: beats.length - 1, still: true }));
  const closeCard = () => setPlay((now) => (now === null ? now : { ...now, card: false }));

  const regular = sim.weeks.filter((week) => !sim.bracket_weeks.includes(week));
  const seeds =
    season !== null && beat !== null && beat.kind !== "week"
      ? new Map(season.seeds.map((seed) => [seed.roster_id, seed.seed]))
      : null;
  const pace: Pace = { off, still: play?.still ?? false };

  return (
    <section aria-labelledby="sim-heading" className="flex flex-col gap-sp-3">
      <div className="flex flex-wrap items-baseline justify-between gap-x-sp-3 gap-y-sp-1">
        <h3 id="sim-heading" className="m-0 text-stat leading-tight font-bold">
          Sim the rest of the season
        </h3>
        <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">
          {`Weeks ${sim.weeks[0]} to ${sim.weeks.at(-1)}`}
        </span>
      </div>
      <p className="m-0 max-w-measure text-lead text-ink-2">
        {`Each press replays one of ${sim.sample.length} stored runs of the sim. The odds come from all ${thousands(sim.runs)} runs.`}
      </p>
      <div className="flex flex-wrap gap-sp-2">
        <button type="button" onClick={press} className={`${BUTTON} bg-accent text-white`}>
          Sim the season
        </button>
        {running && (
          <button type="button" onClick={skip} className={`${BUTTON} border border-rule text-ink`}>
            Skip to the end
          </button>
        )}
      </div>
      {/* The stage takes the full width of the column at every width, and the odds sit below it. Beside the odds on a
          laptop, the stage had room for one letter of each team name. */}
      <div className="flex flex-col gap-sp-3">
        <section
          aria-label="The replay"
          // The stage keeps a fixed least height, so the page does not jump when the table becomes the bracket. The rounds
          // stack on a phone, so the stage is taller there than from a tablet up.
          className="relative flex min-h-[46rem] tablet:min-h-[40rem] flex-col gap-sp-4 overflow-hidden rounded-card border border-rule-dark bg-band p-sp-4 text-on-dark"
        >
          <WeekStrip regular={regular} playoffs={sim.bracket_weeks} current={season && beat ? weekAt(season, beat) : null} />
          <p role="status" className="sr-only">
            {season && beat ? sayAt(season, beat) : ""}
          </p>
          {play === null || season === null || beat === null ? (
            <div className="flex flex-col gap-sp-3">
              <span className="font-mono text-meta font-bold tracking-caps text-on-dark-2 uppercase">{`Standings after week ${sim.week}`}</span>
              <Standings rows={replaySeason(sim, 0).start} label="Standings" pace={{ off, still: true }} />
            </div>
          ) : (
            // The champion card fills the whole stage, so this box sets no position of its own.
            <div key={play.take} className="flex flex-1 flex-col">
              <Stage season={season} beat={beat} play={play} runs={sim.runs} pace={pace} onClose={closeCard} />
            </div>
          )}
        </section>
        <Odds sim={sim} seeds={seeds} />
      </div>
    </section>
  );
}
