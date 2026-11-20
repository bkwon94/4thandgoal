/**
 * The replay of the sim page: three screens on one stage that never scrolls, Season, Playoffs, and Champion, or the two
 * parts of one week, Games and Standings. It plays one stored run, picked in proportion to its weight (decision 04).
 */
"use client";

import { PendingButton } from "@cpc/design/ui/pending-button";
import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import { Pause, Play, RotateCcw, SkipForward, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { EASE_OUT } from "@cpc/design/lib/motion";
import { cn } from "@cpc/design/lib/utils";
import type { Avatars } from "../page/sim-page";
import { replaySeason, type ReplaySeason } from "../replay/season";
import type { WeekSim } from "../schema/sim-types";
import { BracketScreen, ChampionScreen } from "./bracket";
import { pickRun } from "./pick";
import { EYEBROW, FADE_IN, FADE_OUT, Standings, SwapText, WeekGames, ZoneKey } from "./standings";
import { marksOf, stepsOf, type Step } from "./steps";

/* What the reader asked to play: the rest of the season, or one regular week. */
export type StageAsk = { mode: "season" } | { mode: "week"; week: number };

/* The stored runs that the replay picks from: those of the file, or those of the last What-if answer, which each hold
   its set results. The weights are in the order of `sample`. */
export type StageRuns = Pick<WeekSim, "teams" | "sample" | "sample_weights">;

const SCREENS = [
  { id: "season", label: "Season" },
  { id: "bracket", label: "Playoffs" },
  { id: "champion", label: "Champion" },
] as const;

/* The two parts of one week. They take the stage in turn, never together, so each part has the full stage. */
const PARTS = [
  { id: "games", label: "Games" },
  { id: "standings", label: "Standings" },
] as const;

/* Each control is the touch size. The press scales a little, so the stage shows it heard the tap. */
const CONTROL = cn(
  "press h-touch min-w-touch gap-sp-2 rounded-report px-sp-4 text-body flex flex-none items-center justify-center font-semibold",
  "focus-visible:outline-on-dark outline-none focus-visible:outline-2 focus-visible:outline-offset-2",
  "[&_svg]:size-sp-5 [&_svg]:flex-none",
);
const QUIET = "border border-rule-dark text-on-dark hover-fine:bg-chip-dark";

/* The tabs of the header: the screen or the part on the stage takes the red mark, which slides between them. A tab of a
   screen that has played goes back to it. A tab of a screen not yet played stays off and looks off. Under reduced
   motion, a tab fades from off to on, and the red mark fades in on its tab. */
function Tabs({
  items,
  at,
  label,
  off,
  open,
  onGo,
}: {
  items: readonly { id: string; label: string }[];
  at: number;
  label: string;
  off: boolean;
  // True for each tab whose screen has played.
  open: boolean[];
  onGo: (index: number) => void;
}) {
  return (
    <ol aria-label={label} className="gap-sp-1 m-0 flex min-w-0 list-none items-center p-0">
      {items.map((s, i) => (
        <li key={s.id}>
          {/* The reduced-motion rule of the site stops the CSS transition of the opacity, so under reduced motion the
              fade from off to on is an inline motion of its own. */}
          <motion.button
            type="button"
            initial={false}
            animate={off ? { opacity: open[i] ? 1 : 0.4 } : undefined}
            transition={FADE_IN}
            aria-current={i === at ? "step" : undefined}
            disabled={!open[i]}
            onClick={() => onGo(i)}
            className={cn(
              EYEBROW,
              "h-touch px-sp-2 focus-visible:outline-on-dark relative flex items-center transition-[color,opacity] duration-300 outline-none focus-visible:outline-2 focus-visible:outline-offset-[-2px] disabled:cursor-default disabled:opacity-40",
              i === at
                ? "text-on-dark"
                : open[i]
                  ? "text-on-dark-2 hover-fine:text-on-dark"
                  : "text-on-dark-muted",
            )}
          >
            {s.label}
            {i === at && (
              <motion.span
                layoutId={off ? undefined : "stage-mark"}
                initial={off ? { opacity: 0 } : undefined}
                animate={off ? { opacity: 1 } : undefined}
                transition={off ? FADE_IN : { type: "spring", bounce: 0, duration: 0.35 }}
                className="inset-x-sp-2 bottom-sp-2 rounded-report bg-accent absolute h-0.5"
              />
            )}
          </motion.button>
        </li>
      ))}
    </ol>
  );
}

/* The line a screen reader hears at each step. */
function sayAt(season: ReplaySeason, step: Step, week: number): string {
  if (step.screen === "season") {
    if (step.kind === "start") return "Standings at the start of the sim";
    if (step.kind === "cut") return "The playoff field is set";
    return `Week ${season.weeks[step.index].week} final`;
  }
  if (step.screen === "bracket")
    return `${season.rounds[step.round].label}${step.decided ? " results" : ""}`;
  if (step.screen === "champion") return `${season.champion.name} wins the title in this run`;
  return step.kind === "after" ? `Standings after week ${week}` : `Week ${week} games`;
}

/* The part of the week, or the screen, that a step shows, so a tab knows the steps it covers. */
const partOf = (s: Step): string =>
  s.screen === "week" ? (s.kind === "after" ? "standings" : "games") : s.screen;

/* One take of the replay. A take starts at the first step; "Sim again" starts a fresh take. */
function Player({
  startWeek,
  season,
  avatars,
  yourTeam,
  mode,
  weekIndex,
  off,
  onAgain,
  onClose,
}: {
  // The week of the file. The standings at the start of the sim are those after it.
  startWeek: number;
  season: ReplaySeason;
  avatars: Avatars;
  yourTeam: number;
  mode: "season" | "week";
  weekIndex: number;
  off: boolean;
  onAgain: () => void;
  onClose: () => void;
}) {
  const steps = useMemo(() => stepsOf(season, mode), [season, mode]);
  const [at, setAt] = useState(0);
  const [playing, setPlaying] = useState(true);
  // True after a skip or a tab, so no score counts up and no seat waits for a count-up.
  const [jumped, setJumped] = useState(false);
  const step = steps[at];
  const ended = at === steps.length - 1;
  // The furthest step that has played, so a tab can go back to any screen that has played.
  const [reached, setReached] = useState(0);
  useEffect(() => setReached((now) => Math.max(now, at)), [at]);
  const part = partOf(step);
  // True once the standings of one week have moved to the order after the week.
  const [settled, setSettled] = useState(false);
  const afterWeek = step.screen === "week" && step.kind === "after";
  useEffect(() => {
    if (!afterWeek) return;
    const timer = setTimeout(() => setSettled(true), off || jumped ? 0 : 700);
    return () => clearTimeout(timer);
  }, [afterWeek, off, jumped]);

  // Each step holds for its time, then the next step starts. A pause or a skip clears the clock of the old step.
  useEffect(() => {
    if (!playing || ended) return;
    const timer = setTimeout(() => {
      setJumped(false);
      setAt((now) => now + 1);
    }, step.ms);
    return () => clearTimeout(timer);
  }, [at, playing, ended, step.ms]);

  // A skip goes to the last step of the screen on the stage. On that last step, it goes on to the next screen.
  const skip = () => {
    let end = at;
    while (end + 1 < steps.length && partOf(steps[end + 1]) === part) end += 1;
    setJumped(true);
    setAt(end === at ? at + 1 : end);
  };

  // The tabs of the header, each with the range of steps it covers: the three screens of a season, or the two parts of a week.
  // A screen with no step, such as Season with no regular week left, has no tab.
  const firstOf = (id: string) => steps.findIndex((s) => partOf(s) === id);
  const tabs = (mode === "season" ? SCREENS : PARTS).filter((t) => firstOf(t.id) >= 0);
  const lastOf = (id: string) => steps.findLastIndex((s) => partOf(s) === id);
  const tabAt = tabs.findIndex((t) => t.id === part);
  const tabOpen = tabs.map((t) => firstOf(t.id) >= 0 && firstOf(t.id) <= reached);
  // A tap on a tab shows the last played step of its screen, at rest, and pauses, so the reader can look.
  const goTab = (i: number) => {
    const target = Math.min(lastOf(tabs[i].id), reached);
    if (target < 0 || target === at) return;
    setPlaying(false);
    setJumped(true);
    setAt(target);
  };

  const spots = season.seeds.length;
  const screen = step.screen;
  const week = season.weeks[weekIndex];

  let body: React.ReactNode;
  if (step.screen === "season") {
    const shown = step.index;
    const rows = shown < 0 ? season.start : season.weeks[shown].standings;
    const current = shown < 0 ? null : season.weeks[shown];
    const title =
      step.kind === "cut"
        ? "Playoff field set"
        : current === null
          ? `After week ${startWeek}`
          : `Week ${current.week}`;
    body = (
      <div className="gap-sp-2 flex h-full min-h-0 flex-col">
        <SwapText
          text={title}
          off={off}
          className="text-stat text-on-dark leading-tight font-bold"
        />
        <ZoneKey byes={season.byes} spots={spots} />
        <Standings
          rows={rows}
          marks={current === null ? null : marksOf(current)}
          week={current?.week ?? null}
          spots={spots}
          byes={season.byes}
          yourTeam={yourTeam}
          avatars={avatars}
          off={off}
          cut={step.kind === "cut"}
        />
      </div>
    );
  } else if (step.screen === "week") {
    const played = step.kind !== "before";
    const live = step.kind === "games" && !jumped;
    const before = weekIndex === 0 ? season.start : season.weeks[weekIndex - 1].standings;
    // The standings open in the order before the week, then the rows move to their new places.
    const moved = step.kind === "after" && settled;
    body = (
      <div className="gap-sp-2 flex h-full min-h-0 flex-col">
        <span className="text-stat text-on-dark leading-tight font-bold">{`Week ${week.week}`}</span>
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={part}
            initial={off ? { opacity: 0 } : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, transition: { duration: 0.15, ease: EASE_OUT } }}
            transition={{ duration: 0.3, ease: EASE_OUT }}
            className="gap-sp-2 flex min-h-0 flex-1 flex-col"
          >
            {part === "games" ? (
              <WeekGames week={week} played={played} live={live} yourTeam={yourTeam} />
            ) : (
              <>
                <ZoneKey byes={season.byes} spots={spots} />
                <Standings
                  rows={moved ? week.standings : before}
                  marks={moved ? marksOf(week) : null}
                  week={moved ? week.week : null}
                  spots={spots}
                  byes={season.byes}
                  yourTeam={yourTeam}
                  avatars={avatars}
                  off={off}
                  cut={false}
                />
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    );
  } else if (step.screen === "bracket") {
    body = (
      <BracketScreen
        season={season}
        round={step.round}
        decided={step.decided}
        jumped={jumped}
        avatars={avatars}
        yourTeam={yourTeam}
        off={off}
      />
    );
  } else {
    body = (
      <ChampionScreen
        season={season}
        avatars={avatars}
        yourTeam={yourTeam}
        off={off}
        jumped={jumped}
      />
    );
  }

  // The screen enters from a little below, and the old screen leaves fast in place. The shared teams fly between them.
  // The bracket and the champion show at once, because their teams fly in from the screen before and own their fades.
  // Under reduced motion each screen only fades.
  const enterScreen = off
    ? {
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        exit: { opacity: 0 },
        transition: { duration: 0.3 },
      }
    : screen !== "season" && !jumped
      ? {
          initial: false as const,
          animate: { opacity: 1 },
          exit: { opacity: 0, transition: { duration: 0.2, ease: EASE_OUT } },
        }
      : {
          initial: { opacity: 0, y: 8 },
          animate: { opacity: 1, y: 0 },
          exit: { opacity: 0, transition: { duration: 0.2, ease: EASE_OUT } },
          transition: { duration: 0.4, ease: EASE_OUT, delay: 0.1 },
        };

  // The controls of the end, or of the replay while it plays.
  const controls = ended ? (
    <>
      <PendingButton
        type="button"
        onClick={onAgain}
        className={cn(CONTROL, "bg-accent text-on-dark hover-fine:opacity-90")}
      >
        <RotateCcw aria-hidden />
        Sim again
      </PendingButton>
      <PendingButton type="button" onClick={onClose} className={cn(CONTROL, QUIET)}>
        Done
      </PendingButton>
    </>
  ) : (
    <>
      <PendingButton
        type="button"
        aria-label={playing ? "Pause" : "Play"}
        onClick={() => setPlaying((now) => !now)}
        className={cn(CONTROL, QUIET, "px-0")}
      >
        {playing ? <Pause aria-hidden /> : <Play aria-hidden />}
      </PendingButton>
      <PendingButton type="button" onClick={skip} className={cn(CONTROL, QUIET)}>
        <SkipForward aria-hidden />
        Skip
      </PendingButton>
      {/* During the replay, "Sim again" stays quiet. It takes the brand red only at the end, where it is the next step. */}
      <PendingButton type="button" onClick={onAgain} className={cn(CONTROL, QUIET, "ml-auto")}>
        <RotateCcw aria-hidden />
        Sim again
      </PendingButton>
    </>
  );

  return (
    <>
      <p role="status" className="sr-only">
        {sayAt(season, step, week?.week ?? 0)}
      </p>
      <header className="gap-sp-3 flex h-[calc(var(--spacing-touch)+var(--spacing-sp-2))] flex-none items-center justify-between">
        <Tabs
          items={tabs}
          at={tabAt}
          label={mode === "season" ? "Screens" : "Parts of the week"}
          off={off}
          open={tabOpen}
          onGo={goTab}
        />
        <PendingButton
          type="button"
          aria-label="Close the replay"
          onClick={onClose}
          className={cn(CONTROL, "text-on-dark hover-fine:bg-chip-dark px-0")}
        >
          <X aria-hidden />
        </PendingButton>
      </header>
      <div data-testid="stage-body" className="relative min-h-0 flex-1">
        <LayoutGroup>
          <AnimatePresence initial={false}>
            <motion.div key={screen} {...enterScreen} className="absolute inset-0 flex flex-col">
              {body}
            </motion.div>
          </AnimatePresence>
        </LayoutGroup>
      </div>
      <div
        role="group"
        aria-label="Replay controls"
        className="gap-sp-2 pt-sp-3 flex flex-none items-center pb-[max(var(--spacing-sp-3),var(--spacing-door-safe))]"
      >
        {off ? (
          // Under reduced motion, the end swaps the controls through a fade: the old set fades out before the new set
          // fades in, so no control jumps to a new place and none takes the node of another.
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={ended ? "end" : "play"}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, transition: FADE_OUT }}
              transition={FADE_IN}
              className="gap-sp-2 flex min-w-0 flex-1 items-center"
            >
              {controls}
            </motion.div>
          </AnimatePresence>
        ) : (
          controls
        )}
      </div>
    </>
  );
}

/* The replay opens as a fixed layer under the site header and over the page, and the page under it cannot scroll.
   `random` gives a number in [0, 1), as Math.random does. Each open and each "Sim again" picks a new run. */
export function SimStage({
  sim,
  runs,
  avatars,
  yourTeam,
  ask,
  random,
  onDone,
}: {
  sim: WeekSim;
  runs: StageRuns;
  avatars: Avatars;
  yourTeam: number;
  ask: StageAsk;
  random: () => number;
  onDone: () => void;
}) {
  const off = useMotionOff();
  const pick = useCallback(() => pickRun(runs.sample_weights, random), [runs, random]);
  // Each take holds its own run, so "Sim again" plays a fresh take even when the pick gives the same run.
  const [take, setTake] = useState(() => ({ index: pick(), count: 0 }));
  const [closing, setClosing] = useState(false);
  const layer = useRef<HTMLElement>(null);
  const season = useMemo(
    () => replaySeason({ ...sim, teams: runs.teams, sample: [runs.sample[take.index]] }, 0),
    [sim, runs, take.index],
  );
  const found = ask.mode === "week" ? season.weeks.findIndex((w) => w.week === ask.week) : -1;
  const weekIndex = found < 0 ? 0 : found;

  const close = useCallback(() => setClosing(true), []);
  const again = () => setTake((was) => ({ index: pick(), count: was.count + 1 }));

  // The page under the layer holds still, so nothing scrolls during the replay.
  useEffect(() => {
    const root = document.documentElement;
    const was = root.style.overflow;
    root.style.overflow = "hidden";
    layer.current?.focus();
    return () => {
      root.style.overflow = was;
    };
  }, []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => event.key === "Escape" && close();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [close]);

  // The layer closes faster than it opens, so a close feels instant. The timer, not the end of the motion, ends the
  // close, so the layer goes even when no frame of the motion runs.
  useEffect(() => {
    if (!closing) return;
    const timer = setTimeout(onDone, 150);
    return () => clearTimeout(timer);
  }, [closing, onDone]);

  return (
    <motion.section
      ref={layer}
      tabIndex={-1}
      aria-label="Sim replay"
      initial={off ? { opacity: 0 } : { opacity: 0, y: 8 }}
      animate={closing ? (off ? { opacity: 0 } : { opacity: 0, y: 8 }) : { opacity: 1, y: 0 }}
      transition={{ duration: closing ? 0.15 : 0.25, ease: EASE_OUT }}
      className="top-band-height h-door-fill bg-band px-gutter text-on-dark fixed inset-x-0 z-30 flex flex-col overflow-hidden outline-none"
    >
      <div className="max-w-stage mx-auto flex h-full min-h-0 w-full flex-col">
        <Player
          key={take.count}
          startWeek={sim.week}
          season={season}
          avatars={avatars}
          yourTeam={yourTeam}
          mode={ask.mode}
          weekIndex={weekIndex}
          off={off}
          onAgain={again}
          onClose={close}
        />
      </div>
    </motion.section>
  );
}
