/**
 * Screen 2 and screen 3 of the replay of the sim page: the bracket that shows one round at a time, and the champion
 * that lifts out of it, with one line on where Your team finished.
 */
"use client";

import { motion } from "framer-motion";
import { Trophy } from "lucide-react";
import { ordinal, oneDecimal, record } from "@cpc/design/format/format";
import { EASE_OUT } from "@cpc/design/lib/motion";
import { cn } from "@cpc/design/lib/utils";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import type { Avatars } from "../page/sim-page";
import type { BracketTeam, ReplayRound, ReplaySeason, Seed } from "../replay/season";
import { EYEBROW, FLIGHT, MONO, Score } from "./standings";

/* One team of a game or a bye: the seed chip, the avatar, the name, and the score. The name and the avatar carry the
   shared id of the team, so the team flies in from the table and on from round to round. */
function TeamLine({
  team,
  decided,
  won,
  live,
  bye,
  crown,
  you,
  avatar,
  off,
  intro,
}: {
  team: Seed & { score?: number };
  decided: boolean;
  won: boolean;
  live: boolean;
  // True for a seed that waits out the round.
  bye: boolean;
  // The shared id that carries the avatar of the champion out to the champion screen.
  crown?: string;
  you: boolean;
  avatar: string | null;
  off: boolean;
  // True on the first step of the bracket, when the seed chip fades in behind the flight from the table.
  intro: boolean;
}) {
  return (
    <motion.div
      initial={false}
      // A loser dims after the count-up. Framer Motion owns the opacity, so no class sets it.
      animate={{ opacity: decided && !won && !bye ? 0.5 : 1 }}
      transition={{ duration: 0.3, ease: EASE_OUT, delay: decided && live && !off ? 0.7 : 0 }}
      className="relative flex h-touch items-center gap-sp-3 px-sp-3"
    >
      {you && <span aria-hidden="true" className="absolute inset-y-sp-2 left-0 w-1 rounded-report bg-accent" />}
      <motion.span
        initial={intro ? { opacity: 0 } : false}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.25, ease: EASE_OUT, delay: 0.45 }}
        className={cn(MONO, "flex size-sp-5 flex-none items-center justify-center rounded-report bg-accent text-meta font-bold text-white")}
      >
        {team.seed}
      </motion.span>
      <motion.span
        layoutId={off ? undefined : `team-${team.roster_id}`}
        transition={{ layout: { ...FLIGHT, delay: intro ? team.seed * 0.04 : 0 } }}
        className="flex min-w-0 flex-1 items-center gap-sp-2"
      >
        <motion.span layoutId={crown} transition={{ layout: FLIGHT }} className="flex flex-none rounded-full">
          <PhotoFrame src={avatar} name={team.name} size="sm" decorative />
        </motion.span>
        <span className="min-w-0 truncate text-lead leading-tight font-semibold text-on-dark">
          {team.name}
          {you && <span className="sr-only"> (Your team)</span>}
        </span>
      </motion.span>
      {bye ? (
        <span className={cn(EYEBROW, "w-[6ch] flex-none text-right text-on-dark-2")}>Bye</span>
      ) : decided && team.score !== undefined ? (
        <Score value={team.score} live={live} className="w-[6ch] flex-none text-right text-lead" />
      ) : (
        <span className={cn(MONO, "w-[6ch] flex-none text-right text-lead text-on-dark-muted")}>–</span>
      )}
      {decided && won && !bye && (
        // The red bar sweeps under the winner after the count-up.
        <motion.span
          aria-hidden="true"
          initial={live && !off ? { scaleX: 0 } : live ? { opacity: 0 } : false}
          animate={{ scaleX: 1, opacity: 1 }}
          transition={{ duration: 0.4, ease: EASE_OUT, delay: live ? 0.6 : 0 }}
          className="absolute inset-x-sp-3 bottom-0 h-0.5 origin-left bg-accent"
        />
      )}
    </motion.div>
  );
}

/* The marker of the rounds: each round label, with a red mark under the round on the stage. */
function RoundMarker({ rounds, round, off }: { rounds: ReplayRound[]; round: number; off: boolean }) {
  return (
    <div className="flex items-center justify-between gap-sp-3">
      <ol aria-label="Rounds" className="m-0 flex list-none items-center gap-sp-4 p-0">
        {rounds.map((rd, r) => (
          <li
            key={rd.label}
            aria-current={r === round ? "step" : undefined}
            className={cn(
              EYEBROW,
              "relative py-sp-1 whitespace-nowrap transition-colors duration-300",
              r === round ? "text-on-dark" : r < round ? "text-on-dark-2" : "text-on-dark-muted",
            )}
          >
            {rd.label}
            {r === round && (
              <motion.span
                layoutId={off ? undefined : "round-mark"}
                transition={{ type: "spring", bounce: 0, duration: 0.35 }}
                className="absolute inset-x-0 -bottom-px h-0.5 rounded-report bg-accent"
              />
            )}
          </li>
        ))}
      </ol>
      <span className={cn(MONO, "text-meta whitespace-nowrap text-on-dark-2")}>{`Week ${rounds[round].week}`}</span>
    </div>
  );
}

/* The bracket: one round on the stage at a time, full width. When a round has its result, the winners fly on to their
   seats in the next round, and the marker moves with them. A bye seed waits in its own card until its round. */
export function BracketScreen({
  season,
  round,
  decided,
  jumped,
  avatars,
  yourTeam,
  off,
}: {
  season: ReplaySeason;
  round: number;
  // True when the round `round` has its result.
  decided: boolean;
  // True after a skip, so no score counts up.
  jumped: boolean;
  avatars: Avatars;
  yourTeam: number;
  off: boolean;
}) {
  const { rounds, champion } = season;
  const rd = rounds[round];
  const last = rounds.length - 1;
  const live = decided && !jumped;
  // The first step of the bracket, when the seeds fly in from the table.
  const intro = round === 0 && !decided && !jumped && !off;
  // The frame of each card fades in while its teams fly into it. Under reduced motion it only fades.
  const frame = (i: number) =>
    off
      ? { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.3 } }
      : { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.3, ease: EASE_OUT, delay: 0.2 + i * 0.04 } };
  const line = (team: BracketTeam | Seed, extra: { decided: boolean; won: boolean; bye: boolean }) => (
    <TeamLine
      key={team.roster_id}
      team={team}
      {...extra}
      live={live}
      // The id is set from the mount of the final seat, because Framer Motion reads a shared id when the part mounts.
      crown={round === last && team.roster_id === champion.roster_id && !off ? `champion-${team.roster_id}` : undefined}
      you={team.roster_id === yourTeam}
      avatar={avatars[String(team.roster_id)] ?? null}
      off={off}
      intro={intro}
    />
  );
  return (
    <div className="flex h-full min-h-0 flex-col gap-sp-4">
      <RoundMarker rounds={rounds} round={round} off={off} />
      <section aria-label={`${rd.label}, week ${rd.week}`} key={round} className="flex min-h-0 flex-1 flex-col justify-center gap-sp-3">
        {rd.games.map((game, i) => (
          <div
            key={`${game.high.roster_id}-${game.low.roster_id}`}
            role="group"
            aria-label={`Seed ${game.high.seed} ${game.high.name} against seed ${game.low.seed} ${game.low.name}`}
            className="relative py-sp-1"
          >
            <motion.span
              aria-hidden="true"
              {...frame(i)}
              className={cn(
                "absolute inset-0 rounded-report border bg-chip-dark transition-colors duration-300",
                decided ? "border-rule-dark" : "border-on-dark-muted",
              )}
            />
            {[game.high, game.low].map((team) => line(team, { decided, won: game.winner === team.roster_id, bye: false }))}
          </div>
        ))}
        {rd.byes.length > 0 && (
          <div role="group" aria-label="Byes this round" className="relative py-sp-1">
            <motion.span
              aria-hidden="true"
              {...frame(rd.games.length)}
              className="absolute inset-0 rounded-report border border-dashed border-rule-dark"
            />
            {rd.byes.map((team) => line(team, { decided: false, won: false, bye: true }))}
          </div>
        )}
      </section>
    </div>
  );
}

type PathStep = { label: string; bye: true } | { label: string; bye: false; them: BracketTeam; score: string };

/* The playoff wins of the champion, round by round, with a bye as its own line. */
function pathOf(season: ReplaySeason): PathStep[] {
  const rid = season.champion.roster_id;
  return season.rounds.flatMap((round): PathStep[] => {
    const game = round.games.find((g) => g.high.roster_id === rid || g.low.roster_id === rid);
    if (game === undefined) return round.byes.some((b) => b.roster_id === rid) ? [{ label: round.label, bye: true as const }] : [];
    const [me, them] = game.high.roster_id === rid ? [game.high, game.low] : [game.low, game.high];
    return [{ label: round.label, bye: false as const, them, score: `${oneDecimal(me.score)}–${oneDecimal(them.score)}` }];
  });
}

/* Where Your team finished, in one line, when it did not win the title. */
function yourLine(season: ReplaySeason, yourTeam: number): string {
  const final = season.weeks.at(-1)?.standings ?? season.start;
  const row = final.find((r) => r.roster_id === yourTeam);
  const seed = season.seeds.find((s) => s.roster_id === yourTeam);
  if (row === undefined) return "";
  if (seed === undefined) return `Your team finished ${ordinal(row.place)} at ${record(row.wins, row.losses)} and missed the playoffs.`;
  for (const round of season.rounds) {
    const game = round.games.find((g) => g.high.roster_id === yourTeam || g.low.roster_id === yourTeam);
    if (game !== undefined && game.winner !== yourTeam) {
      const by = game.high.roster_id === game.winner ? game.high : game.low;
      return round.label === "Final"
        ? `Your team, the ${ordinal(seed.seed)} seed, lost the Final to ${by.name}.`
        : `Your team, the ${ordinal(seed.seed)} seed, lost to ${by.name} in ${round.label === "Semifinal" ? "the Semifinal" : round.label}.`;
    }
  }
  return "";
}

/* The rays of the big moment: thin wedges of the accent around the avatar. */
const RAYS = "repeating-conic-gradient(from 0deg, var(--color-accent) 0deg 4deg, transparent 4deg 18deg)";

export function ChampionScreen({
  season,
  avatars,
  yourTeam,
  off,
  jumped,
}: {
  season: ReplaySeason;
  avatars: Avatars;
  yourTeam: number;
  off: boolean;
  jumped: boolean;
}) {
  const { champion } = season;
  const mine = champion.roster_id === yourTeam;
  const final = season.weeks.at(-1)?.standings ?? season.start;
  const row = final.find((r) => r.roster_id === champion.roster_id)!;
  const path = pathOf(season);
  const burst = mine && !off && !jumped;
  // The text waits for the avatar to land from the bracket, then rises in line by line.
  const rise = (i: number) =>
    off
      ? { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.3, delay: 0.2 + i * 0.05 } }
      : {
          initial: { opacity: 0, y: 8, filter: "blur(3px)" },
          animate: { opacity: 1, y: 0, filter: "blur(0px)" },
          transition: { duration: 0.5, ease: EASE_OUT, delay: 0.45 + i * 0.08 },
        };
  return (
    <div
      className="relative flex h-full min-h-0 flex-col items-center justify-center gap-sp-3 overflow-hidden text-center"
      // The big moment lights the stage with the glow of the brand red. A loss keeps the plain stage.
      style={mine ? { background: "radial-gradient(60% 45% at 50% 35%, var(--color-accent-glow), transparent)" } : undefined}
    >
      <div className="relative flex flex-none items-center justify-center">
        {burst && (
          <>
            <motion.span
              aria-hidden="true"
              className="pointer-events-none absolute -inset-sp-6 rounded-full"
              style={{ background: RAYS }}
              initial={{ opacity: 0, rotate: 0, scale: 0.7 }}
              animate={{ opacity: [0, 0.5, 0.25], rotate: 24, scale: 1.1 }}
              transition={{ duration: 1.4, delay: 0.5, ease: EASE_OUT }}
            />
            <motion.span
              aria-hidden="true"
              className="pointer-events-none absolute inset-0 rounded-full border-2 border-accent"
              initial={{ opacity: 1, scale: 0.7 }}
              animate={{ opacity: 0, scale: 1.8 }}
              transition={{ duration: 0.9, delay: 0.5, ease: EASE_OUT }}
            />
          </>
        )}
        <motion.span
          layoutId={off ? undefined : `champion-${champion.roster_id}`}
          transition={{ layout: FLIGHT }}
          className="relative flex rounded-full"
        >
          <PhotoFrame
            src={avatars[String(champion.roster_id)] ?? null}
            name={champion.name}
            size="lg"
            decorative
            className="size-[calc(var(--spacing-headshot)*1.875)]"
          />
        </motion.span>
        <motion.span
          aria-hidden="true"
          {...rise(0)}
          className="absolute -top-sp-1 -right-sp-1 flex size-sp-6 items-center justify-center rounded-full bg-band text-accent-text"
        >
          <Trophy className="size-sp-4" strokeWidth={2.5} />
        </motion.span>
      </div>
      <div className="flex flex-col items-center gap-sp-0">
        <motion.span {...rise(1)} className={cn(EYEBROW, "text-accent-text")}>
          {mine ? "Your team wins the title" : "Champion of this run"}
        </motion.span>
        <motion.h2 {...rise(2)} className="m-0 text-score leading-tight font-bold tracking-tight text-balance text-on-dark">
          {champion.name}
        </motion.h2>
        <motion.span {...rise(3)} className={cn(MONO, "text-meta text-on-dark-2")}>
          {`${ordinal(champion.seed)} seed · ${record(row.wins, row.losses)} in the regular season`}
        </motion.span>
      </div>
      <motion.ol {...rise(4)} aria-label="Path to the title" className="m-0 flex w-full max-w-[26rem] list-none flex-col gap-sp-1 p-0">
        {path.map((step) => (
          <li key={step.label} className="flex items-center gap-sp-2 rounded-report bg-chip-dark px-sp-3 py-sp-2 text-left">
            <span className={cn(EYEBROW, "w-[6rem] flex-none text-on-dark-2")}>{step.label}</span>
            {step.bye ? (
              <span className="flex-1 text-meta text-on-dark-muted">Bye</span>
            ) : (
              <>
                <span className="min-w-0 flex-1 truncate text-meta text-on-dark">{`Beat ${step.them.name}`}</span>
                <span className={cn(MONO, "text-meta font-bold text-on-dark")}>{step.score}</span>
              </>
            )}
          </li>
        ))}
      </motion.ol>
      {!mine && (
        <motion.p {...rise(5)} className="m-0 max-w-[26rem] text-meta text-pretty text-on-dark-2">
          {yourLine(season, yourTeam)}
        </motion.p>
      )}
    </div>
  );
}
