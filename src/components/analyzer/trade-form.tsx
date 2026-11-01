/**
 * The trade form: one group of pickers per side, the submit button, the finder, and the result.
 * It owns the picks and the grade state, and it posts the trade to the analyze route.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { PlusIcon } from "lucide-react";
import { useEffect, useRef, useState, type ReactNode } from "react";
import AnalyzeResult from "@/components/analyzer/analyze-result";
import { ErrorLine } from "@/components/parts/error-line";
import { TradeFinder } from "@/components/analyzer/trade-finder";
import { TradeSide } from "@/components/analyzer/trade-side";
import { Button } from "@/components/ui/button";
import type { AnalyzeResponse, FinderTrade } from "@/lib/analyze-types";
import { ApiError, postAnalyze, toErrorLine, type Team } from "@/lib/api";
import { DURATION, enterExit, SWEEP_EASE, useMotionOff } from "@/lib/motion";
import { countEvent } from "@/lib/usage";

// A cold grade takes about 30 seconds and the server caches the result, so a long wait beats a retry.
const TIMEOUT_MS = 60_000;

type GradeState =
  | { status: "idle" }
  | { status: "grading" }
  | { status: "done"; doc: AnalyzeResponse }
  | { status: "error"; message: string; retry: boolean };

type TradeFormProps = {
  teams: Team[];
  // The league season the analyze body sends, and the build flag that shows the finder.
  // The page reads both from the config, so the form imports no config.
  season: number;
  finderOn: boolean;
  passphrase: string;
  // The passphrase is wrong, so the page clears it and asks again.
  onUnauthorized: () => void;
  // Analyze answered 422, so the page fetches the current rosters.
  onRostersStale?: () => void;
  /* The page places the two parts. The result goes after the form's chapter and not inside it, so its own chapters
     read as cards under the form card. The form keeps the grade state, so it hands the parts out and does not lift the state. */
  children?: (parts: FormParts) => ReactNode;
};

/* The form with the finder, and the result of a done grade. */
type FormParts = { form: ReactNode; result: ReactNode };

/* With no layout from the page, the result follows the form. */
const stackParts = ({ form, result }: FormParts) => (
  <>
    {form}
    {result}
  </>
);

/* A given player and the side he goes to. toSide is the id of the destination side, not its roster, so the destination
   holds when that side changes its team. The post turns it into the roster id. See ADR 0003. */
export type PlayerPick = { playerId: string; toSide: number };

/* One side of the trade: a stable id, the picked roster, and the players it gives. The id keys the side, so a remove
   keeps the state and the motion of the sides after it. */
type Side = { id: number; rosterId: number | null; picks: PlayerPick[] };

/* The sides of a trade in order. The first side is the asker, "Your Team". */
type Sides = Side[];

/* The heading of each side, by its place in the order. */
export const SIDE_TITLES = ["Your Team", "Team Two", "Team Three", "Team Four"];

/* The analyze route grades two to four sides. */
const MAX_SIDES = 4;

const EMPTY_SIDES: Sides = [
  { id: 0, rosterId: null, picks: [] },
  { id: 1, rosterId: null, picks: [] },
];

/* A trade to grade: the sides and the season of the data they come from. */
type TradeToGrade = { sides: Sides; season: number };

/* The default destination of a side's picks: the next side in order, and the first side for the last. With two sides it is the other side. */
function defaultTo(sides: Sides, index: number): number {
  return sides[(index + 1) % sides.length].id;
}

/* Points every pick at a side that still exists. With two sides the destination is always the other side.
   With more, a kept destination holds, and a pick to a removed side or to its own side falls back to the default.
   With reset, every pick takes the default. */
function withDestinations(sides: Sides, reset = false): Sides {
  return sides.map((side, index) => {
    const fallback = defaultTo(sides, index);
    const valid = (to: number) =>
      !reset && (sides.length === 2 ? to === fallback : to !== side.id && sides.some((other) => other.id === to));
    return side.picks.every((p) => valid(p.toSide))
      ? side
      : { ...side, picks: side.picks.map((p) => (valid(p.toSide) ? p : { ...p, toSide: fallback })) };
  });
}

/* The team of a roster id, or undefined before a pick. */
function teamOf(teams: Team[], rosterId: number | null): Team | undefined {
  return teams.find((t) => t.roster_id === rosterId);
}

/* The teams a side can pick: every team that no other side holds, so one team cannot be two sides. */
function freeTeams(teams: Team[], sides: Sides, index: number): Team[] {
  return teams.filter((t) => !sides.some((other, i) => i !== index && other.rosterId === t.roster_id));
}

/* The other sides that a pick of a side can go to, each with its team once picked. */
function destinationsOf(teams: Team[], sides: Sides, side: Side) {
  return sides.filter((other) => other.id !== side.id).map((other) => ({ id: other.id, team: teamOf(teams, other.rosterId) }));
}

/* Every side gives at least one player and gets at least one player. The submit gate and the button read it. */
function everySideTrades(sides: Sides): boolean {
  return sides.every(
    (side) =>
      side.rosterId !== null &&
      side.picks.length > 0 &&
      sides.some((other) => other !== side && other.picks.some((p) => p.toSide === side.id)),
  );
}

/* Drops each pick that is not on the current roster of the side's team. A fresh roster can lose a player after a trade.
   It returns the same object when nothing drops, so React skips the render. */
function dropStalePicks(side: Side, teams: Team[]): Side {
  if (side.rosterId === null) return side;
  const team = teamOf(teams, side.rosterId);
  if (!team) return { ...side, rosterId: null, picks: [] };
  const onRoster = new Set(team.players.map((p) => p.player_id));
  const picks = side.picks.filter((p) => onRoster.has(p.playerId));
  return picks.length === side.picks.length ? side : { ...side, picks };
}

/* The grading status. A red bar sweeps along a grey track, so a 20-second wait reads as work in progress.
   Only transform animates. With motion off, the track stays as a still grey line. */
function GradingStatus() {
  const off = useMotionOff();
  return (
    <div role="status" aria-busy="true" className="flex flex-col gap-sp-2">
      <p className="m-0 text-body font-bold">Grading the Trade</p>
      <div aria-hidden="true" className="relative h-sp-1 overflow-hidden rounded-sm bg-gry">
        {!off && (
          <motion.div
            role="presentation"
            className="absolute inset-y-0 left-0 w-1/3 bg-red"
            initial={{ x: "-100%" }}
            animate={{ x: "300%" }}
            transition={{ duration: DURATION.sweep, ease: SWEEP_EASE, repeat: Infinity }}
          />
        )}
      </div>
      <p className="m-0 text-meta text-mute">This can take up to a minute on a new chart week.</p>
    </div>
  );
}

export function TradeForm({ teams, season, finderOn, passphrase, onUnauthorized, onRostersStale, children = stackParts }: TradeFormProps) {
  const [sides, setSides] = useState<Sides>(EMPTY_SIDES);
  // The id of the next added side. EMPTY_SIDES holds ids 0 and 1, and an id is never reused, so a key never repeats.
  const nextSideId = useRef(EMPTY_SIDES.length);
  const [grade, setGrade] = useState<GradeState>({ status: "idle" });
  // A late answer from an old trade must not overwrite the state of a new one.
  const runId = useRef(0);
  // The unmount effect aborts the call in flight, so a closed page does not wait on the API.
  const controllerRef = useRef<AbortController | null>(null);
  const unmounted = useRef(false);
  // A finder card asks for the full result, so the page scrolls the result into view when the grade ends.
  const resultRef = useRef<HTMLDivElement>(null);
  const scrollToResult = useRef(false);
  const off = useMotionOff();

  useEffect(() => {
    // React strict mode runs the cleanup and the effect again on mount, so the effect resets the flag.
    unmounted.current = false;
    return () => {
      unmounted.current = true;
      controllerRef.current?.abort();
    };
  }, []);

  // The scroll waits for the result, because the result is not in the page until the grade ends.
  useEffect(() => {
    if (grade.status !== "done" || !scrollToResult.current) return;
    scrollToResult.current = false;
    resultRef.current?.scrollIntoView({ behavior: off ? "auto" : "smooth", block: "start" });
  }, [grade.status, off]);

  // The page can swap a stored list for the fresh one while the form shows, so a pick of a traded player drops.
  // The check runs in the render, not in an effect, so no render ever shows a stale pick with the submit button on.
  const [seenTeams, setSeenTeams] = useState(teams);
  if (teams !== seenTeams) {
    setSeenTeams(teams);
    const fresh = sides.map((side) => dropStalePicks(side, teams));
    if (fresh.some((side, index) => side !== sides[index])) setSides(withDestinations(fresh));
  }

  const asker = sides[0].rosterId;
  const myTeam = teamOf(teams, asker);
  const ready = everySideTrades(sides);
  // A new side starts with no team, so the reader fills each side before the next one shows.
  const canAdd = sides.length < MAX_SIDES && sides.every((side) => side.rosterId !== null);
  // The finder grades two sides, so it hides once the trade has a third side.
  const twoSides = sides.length === 2;
  // The grade locks the form, so the result always matches the picks on the screen. A result or an error ends it.
  const grading = grade.status === "grading";

  /* A change to the trade makes the old result stale, so it clears the result and drops a late answer to the old trade. */
  function changeTrade(update: (current: Sides) => Sides) {
    runId.current += 1;
    setSides(update);
    setGrade({ status: "idle" });
  }

  // A new team makes the old picks and the old result stale, so a change clears them.
  function pickTeam(index: number, rosterId: number) {
    changeTrade((current) => withDestinations(current.map((side, i) => (i === index ? { ...side, rosterId, picks: [] } : side))));
  }

  /* The player picker reports the full list of ids. A kept player keeps his pick, so his destination holds. */
  function pickPlayers(index: number, playerIds: string[]) {
    setSides((current) =>
      withDestinations(
        current.map((side, i) => {
          if (i !== index) return side;
          const picks = playerIds.map(
            (playerId) => side.picks.find((p) => p.playerId === playerId) ?? { playerId, toSide: defaultTo(current, i) },
          );
          return { ...side, picks };
        }),
      ),
    );
  }

  /* Points one pick at another side. Only a trade of three or more sides shows the To picker. */
  function pickDestination(index: number, playerId: string, toSide: number) {
    changeTrade((current) =>
      current.map((side, i) =>
        i === index ? { ...side, picks: side.picks.map((p) => (p.playerId === playerId ? { ...p, toSide } : p)) } : side,
      ),
    );
  }

  /* At two sides no destination is the reader's choice, so the move to three sides sets every pick to the default.
     At three or more sides the picks hold. */
  function addSide() {
    const id = nextSideId.current++;
    changeTrade((current) => withDestinations([...current, { id, rosterId: null, picks: [] }], current.length === 2));
  }

  /* A removed side takes its players out of the trade, and the players sent to it fall back to the default destination. */
  function removeSide(id: number) {
    changeTrade((current) => withDestinations(current.filter((side) => side.id !== id)));
  }

  /* A finder card opens its full result here, so the form shows the picks of the trade and the result matches them.
     The form already owns the grade, so the card reuses this submit and needs no query or route of its own. */
  function openTrade(trade: FinderTrade, tradeSeason: number) {
    const partner = trade.sides.find((side) => side.roster_id !== asker);
    const own = trade.sides.find((side) => side.roster_id === asker);
    if (asker === null || !own || !partner) return;
    // The finder shows only at two sides, so the card fills the two sides that are there.
    const [mine, theirs] = sides;
    const toPicks = (side: { gives: { player_id: string }[] }, toSide: number) =>
      side.gives.map((p) => ({ playerId: p.player_id, toSide }));
    const next: Sides = [
      { id: mine.id, rosterId: asker, picks: toPicks(own, theirs.id) },
      { id: theirs.id, rosterId: partner.roster_id, picks: toPicks(partner, mine.id) },
    ];
    setSides(next);
    // The new picks are not in state until the next render, so the submit gets them as an argument.
    // The season is the one of the finder document, so the grade matches the trade the card shows.
    submit({ sides: next, season: tradeSeason });
  }

  // The trade comes from the state by default. A finder card passes its own, because its picks land in state one render later.
  async function submit(trade?: TradeToGrade) {
    const toGrade = trade ?? { sides, season };
    const askerId = toGrade.sides[0].rosterId;
    if (askerId === null || !everySideTrades(toGrade.sides)) return;
    const id = ++runId.current;
    // Only a finder card passes a trade, and only that path scrolls to the result.
    scrollToResult.current = trade !== undefined;
    const controller = new AbortController();
    controllerRef.current = controller;
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, TIMEOUT_MS);
    setGrade({ status: "grading" });
    countEvent("analyze-grade");
    try {
      const doc = await postAnalyze(
        passphrase,
        {
          season: toGrade.season,
          asker: askerId,
          // everySideTrades holds, so every side has a team and every pick points at a side of the trade.
          sides: toGrade.sides.map((side) => ({
            roster_id: side.rosterId!,
            gives: side.picks.map((p) => ({
              player_id: p.playerId,
              to: toGrade.sides.find((other) => other.id === p.toSide)!.rosterId!,
            })),
          })),
        },
        controller.signal,
      );
      if (id === runId.current && !unmounted.current) setGrade({ status: "done", doc });
    } catch (error) {
      // An abort from unmount must not set state on a gone component.
      if (id !== runId.current || unmounted.current) return;
      if (error instanceof ApiError && error.status === 401) onUnauthorized();
      else setGrade({ status: "error", ...toErrorLine(error, timedOut, "The grade took too long.") });
      if (error instanceof ApiError && error.status === 422) onRostersStale?.();
    } finally {
      clearTimeout(timer);
    }
  }

  const form = (
    <>
      {/* From the tablet tier the form is a two-column grid, one side per cell, in document order. A third and a fourth
          side wrap to the next row. A phone and a screen reader get the same order as the one-column flow. The heading,
          the grade button, and the parts after it span both columns. relative holds a removed side that popLayout lifts out. */}
      <section
        aria-labelledby="pick-teams"
        className="relative flex flex-col gap-sp-5 tablet:grid tablet:grid-cols-2 tablet:items-start"
      >
        <h2 id="pick-teams" className="m-0 text-stat leading-stat font-black uppercase tablet:col-span-2">
          Pick the Teams
        </h2>
        {/* popLayout takes a removed side out of the flow at once, so the sides after it slide into place while it fades. */}
        <AnimatePresence initial={false} mode="popLayout">
          {sides.map((side, index) => (
            <motion.div
              key={side.id}
              layout={!off}
              className="min-w-0"
              {...enterExit(off)}
            >
              <TradeSide
                title={SIDE_TITLES[index]}
                // A team that another side holds is absent from this side's list, so one team cannot be two sides.
                teams={freeTeams(teams, sides, index)}
                team={teamOf(teams, side.rosterId)}
                picks={side.picks}
                // With two sides the destination is the other side, so no To picker shows.
                destinations={twoSides ? null : destinationsOf(teams, sides, side)}
                onPickTeam={(rosterId) => pickTeam(index, rosterId)}
                onPickPlayers={(ids) => pickPlayers(index, ids)}
                onPickDestination={(playerId, toSide) => pickDestination(index, playerId, toSide)}
                // Only the third and fourth sides can leave. A trade always has two sides.
                onRemove={index >= 2 ? () => removeSide(side.id) : undefined}
                locked={grading}
              />
            </motion.div>
          ))}
        </AnimatePresence>
        {canAdd && (
          // The button takes the next grid cell after the last side, so a new side appears where the button was.
          <div>
            <Button
              variant="ghost"
              className="press h-touch w-full justify-start gap-sp-2 rounded-card px-sp-3 text-row font-bold text-ink hover:bg-gry focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red focus-visible:ring-0 disabled:opacity-40"
              disabled={grading}
              onClick={addSide}
            >
              <PlusIcon aria-hidden="true" className="size-4" />
              Add a Team
            </Button>
          </div>
        )}
        <Button
          className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold tablet:col-span-2"
          disabled={!ready || grading}
          aria-busy={grading || undefined}
          // The arrow drops the click event, so submit reads the trade from the state.
          onClick={() => submit()}
        >
          {grading ? "Grading…" : "Grade the Trade"}
        </Button>
        {grading && (
          <div className="tablet:col-span-2">
            <GradingStatus />
          </div>
        )}
        {grade.status === "error" && (
          <div className="flex flex-col gap-sp-3 tablet:col-span-2">
            <ErrorLine>{grade.message}</ErrorLine>
            {grade.retry && (
              <Button className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold" onClick={() => submit()}>
                Try Again
              </Button>
            )}
          </div>
        )}
      </section>
      {/* The finder needs the asker, so it shows once the asker is picked. The key resets the partner and the cards when the asker changes.
          The finder grades two sides, so it hides at three or four. */}
      {/* The finder is off by default because the page felt crowded. */}
      {finderOn && myTeam && twoSides && (
        <div className="mt-sp-6">
          <TradeFinder
            key={myTeam.roster_id}
            teams={teams}
            season={season}
            asker={myTeam.roster_id}
            passphrase={passphrase}
            onUnauthorized={onUnauthorized}
            onRostersStale={onRostersStale}
            onOpen={openTrade}
            locked={grading}
          />
        </div>
      )}
    </>
  );

  const result = grade.status === "done" && (
    <div ref={resultRef}>
      <AnalyzeResult doc={grade.doc} />
    </div>
  );

  return children({ form, result });
}
