/**
 * The trade form, the Stack: the hero, the teams row, one card for each side that says what it gets, the sheets, and the grade bar.
 * It owns the trade and the grade state, and it posts the trade to the analyze route with the finder and the result after it.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState, type ReactNode } from "react";
import AnalyzeResult from "./analyze-result";
import { CircleAlertIcon } from "lucide-react";
import { Card } from "@cpc/design/parts/card";
import { ErrorLine } from "@cpc/design/parts/error-line";
import { FoldLine } from "./fold-line";
import { Hero } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { GetCard, type GotRow } from "./get-card";
import { GradeBar } from "./grade-bar";
import { Sweep } from "./sweep";
import { PlayerSheet } from "./player-sheet";
import { TeamSheet } from "./team-sheet";
import { TeamsRow } from "./teams-row";
import { TradeFinder } from "./trade-finder";
import { Button } from "@cpc/design/ui/button";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { useRequest } from "./use-request";
import type { AnalyzeResponse, FinderTrade } from "../lib/analyze-types";
import { ApiError, type ApiTarget, postAnalyze, toErrorLine, type Team } from "../lib/api";
import {
  analyzeRequest,
  dropStaleGets,
  EMPTY_SIDES,
  everySideTrades,
  type Get,
  MAX_SIDES,
  SIDE_TITLES,
  type Sides,
  teamOf,
} from "../lib/trade";
import { enterExit } from "@cpc/design/lib/motion";
import { countEvent } from "@cpc/design/lib/usage";

// A cold grade takes about 30 seconds and the server caches the result, so a long wait beats a retry.
const TIMEOUT_MS = 60_000;

type GradeState =
  | { status: "idle" }
  | { status: "grading" }
  | { status: "done"; doc: AnalyzeResponse }
  | { status: "error"; message: string };

type TradeFormProps = {
  // The teams of the league. The list is empty until the teams arrive, and the empty Stack shows with each control off.
  teams: Team[];
  // The API of the client and the league season the analyze body sends, and the build flag that shows the finder.
  // The page reads them from the config, so the form imports no config.
  target: ApiTarget;
  finderOn: boolean;
  passphrase: string;
  // The passphrase is wrong, so the page clears it and asks again.
  onUnauthorized: () => void;
  // Analyze answered 422, so the page fetches the current rosters.
  onRostersStale?: () => void;
  /* The page places the parts, so it can put its own lines, such as a failed fetch, between the hero and the form.
     The form keeps the grade state, so it hands the parts out and does not lift the state. */
  children?: (parts: FormParts) => ReactNode;
};

/* The hero, the form with the finder, and the result of a done grade. */
type FormParts = { hero: ReactNode; form: ReactNode; result: ReactNode };

/* With no layout from the page, the parts follow in order. */
const stackParts = ({ hero, form, result }: FormParts) => (
  <>
    {hero}
    {form}
    {result}
  </>
);

/* A trade to grade: the sides and the season of the data they come from. */
type TradeToGrade = { sides: Sides; season: number };

/* The sheet that is open, if any: the team sheet of a slot, the team sheet of "+" for a new side, or the picker of one side. */
type OpenSheet = { kind: "team"; slot: number } | { kind: "add" } | { kind: "players"; side: number } | null;

/* The hero while the grade runs, in the hero slots: Live, the title, the line, and the loading state as the feature.
   The bars and the sweep sit where the verdict lands. With motion off, the bars hold still. The verdict that replaces
   it opens with a level-two heading, so this title is level two too. */
function GradingHero() {
  const off = useMotionOff();
  const pulse = off ? "" : "animate-pulse";
  return (
    <Hero
      label="Grading the Trade"
      level={2}
      eyebrow="Live"
      title="Grading the Trade"
      meta="This can take up to a minute."
      feature={
        <div role="status" aria-busy="true" aria-label="Grading the Trade">
          <div aria-hidden="true" className="flex flex-col gap-sp-3">
            <div className={`h-sp-6 w-3/4 rounded-tile bg-rule-dark ${pulse}`} />
            <div className={`h-sp-4 w-11/12 rounded-tile bg-rule-dark ${pulse}`} />
            <Sweep track="bg-rule-dark" />
          </div>
        </div>
      }
    />
  );
}

/* The hero of the page, in the hero slots: the title and the question of the Stack as the meta line. */
function TitleHero() {
  return <Hero label="Trade Analyzer" title="Trade Analyzer" meta={<Rise step={1}>Who gets what?</Rise>} />;
}

export function TradeForm({ teams, target, finderOn, passphrase, onUnauthorized, onRostersStale, children = stackParts }: TradeFormProps) {
  const [sides, setSides] = useState<Sides>(EMPTY_SIDES);
  // The id of the next added side. EMPTY_SIDES holds ids 0 and 1, and an id is never reused, so a key never repeats.
  const nextSideId = useRef(EMPTY_SIDES.length);
  const [sheet, setSheet] = useState<OpenSheet>(null);
  const [grade, setGrade] = useState<GradeState>({ status: "idle" });
  // Edit opens the folded form under a result, so the reader can change the trade and keep the result on the screen.
  const [editing, setEditing] = useState(false);
  // A late answer from an old trade must not overwrite the state of a new one.
  const request = useRequest();
  // A finder card asks for the full result, so the page scrolls the result into view when the grade ends.
  const resultRef = useRef<HTMLDivElement>(null);
  const scrollToResult = useRef(false);
  const off = useMotionOff();

  // The scroll waits for the result, because the result is not in the page until the grade ends.
  useEffect(() => {
    if (grade.status !== "done" || !scrollToResult.current) return;
    scrollToResult.current = false;
    resultRef.current?.scrollIntoView({ behavior: off ? "auto" : "smooth", block: "start" });
  }, [grade.status, off]);

  // The page can swap a stored list for the fresh one while the form shows, so a pick of a traded player drops.
  // The check runs in the render, not in an effect, so no render ever shows a stale pick with the grade bar on.
  const [seenTeams, setSeenTeams] = useState(teams);
  if (teams !== seenTeams) {
    setSeenTeams(teams);
    const fresh = dropStaleGets(sides, teams);
    if (fresh !== sides) setSides(fresh);
  }

  const asker = sides[0].rosterId;
  const myTeam = teamOf(teams, asker);
  const ready = everySideTrades(sides);
  // The finder grades two sides, so it hides once the trade has a third side.
  const twoSides = sides.length === 2;
  // The grade locks the form, so the result always matches the picks on the screen. A result or an error ends it.
  const grading = grade.status === "grading";
  // The form folds to one line while the grade runs and under a result, so the hero and the verdict lead the page.
  const folded = grading || (grade.status === "done" && !editing);
  // With no teams yet, no slot and no picker has anything to show.
  const locked = grading || teams.length === 0;
  const teamSheet = teamSheetOf(sheet);
  // The teams that another side holds. The team sheet of a slot leaves its own team on, so a tap on it changes nothing.
  const taken = sides.flatMap((side, i) => (side.rosterId === null || teamSheet?.slot === i ? [] : [side.rosterId]));

  /* A change to the trade makes the old result stale, so it clears the result and drops a late answer to the old trade. */
  function changeTrade(update: (current: Sides) => Sides) {
    request.drop();
    setSides(update);
    setGrade({ status: "idle" });
  }

  /* A new team for a side takes the old roster out of the trade, so each get from that side drops. The players the side
     gets come from other teams, so they stay. */
  function pickTeam(index: number, rosterId: number) {
    changeTrade((current) => {
      const id = current[index].id;
      return current.map((side, i) => ({
        ...side,
        rosterId: i === index ? rosterId : side.rosterId,
        gets: side.gets.filter((get) => get.fromSide !== id),
      }));
    });
  }

  /* "+" adds a side with the team that the reader taps, so a new side is never empty. */
  function addSide(rosterId: number) {
    const id = nextSideId.current++;
    changeTrade((current) => [...current, { id, rosterId, gets: [] }]);
  }

  /* The team sheet that is open, if any: its title, the slot whose team it changes, and the action of a tap on a team.
     The sheet of a slot changes the team of that side. The sheet of "+" has no slot, and a tap adds a side. */
  function teamSheetOf(open: OpenSheet) {
    if (open?.kind === "team") {
      const index = open.slot;
      return { title: `Pick ${SIDE_TITLES[index]}`, slot: index, pick: (rosterId: number) => pickTeam(index, rosterId) };
    }
    if (open?.kind === "add") {
      return {
        title: `Pick ${SIDE_TITLES[sides.length] ?? "a Team"}`,
        slot: null,
        pick: (rosterId: number) => {
          if (sides.length < MAX_SIDES) addSide(rosterId);
        },
      };
    }
    return null;
  }

  /* A removed side takes its card out, and each player it gives leaves the other cards. */
  function removeSide(id: number) {
    changeTrade((current) =>
      current.filter((side) => side.id !== id).map((side) => ({ ...side, gets: side.gets.filter((get) => get.fromSide !== id) })),
    );
  }

  /* A tap on a row of the picker checks or unchecks the player for the side of the sheet. */
  function toggleGet(index: number, get: Get) {
    changeTrade((current) =>
      current.map((side, i) => {
        if (i !== index) return side;
        const has = side.gets.some((g) => g.playerId === get.playerId && g.fromSide === get.fromSide);
        return { ...side, gets: has ? side.gets.filter((g) => g.playerId !== get.playerId) : [...side.gets, get] };
      }),
    );
  }

  function removeGet(index: number, playerId: string) {
    changeTrade((current) =>
      current.map((side, i) => (i === index ? { ...side, gets: side.gets.filter((g) => g.playerId !== playerId) } : side)),
    );
  }

  /* A finder card opens its full result here, so the form shows the picks of the trade and the result matches them.
     The form already owns the grade, so the card reuses this submit and needs no query or route of its own. */
  function openTrade(trade: FinderTrade, tradeSeason: number) {
    const partner = trade.sides.find((side) => side.roster_id !== asker);
    const own = trade.sides.find((side) => side.roster_id === asker);
    if (asker === null || !own || !partner) return;
    // The finder shows only at two sides, so the card fills the two sides that are there.
    const [mine, theirs] = sides;
    const toGets = (side: { gives: { player_id: string }[] }, fromSide: number) =>
      side.gives.map((p) => ({ playerId: p.player_id, fromSide }));
    const next: Sides = [
      { id: mine.id, rosterId: asker, gets: toGets(partner, theirs.id) },
      { id: theirs.id, rosterId: partner.roster_id, gets: toGets(own, mine.id) },
    ];
    setSides(next);
    // The new picks are not in state until the next render, so the submit gets them as an argument.
    // The season is the one of the finder document, so the grade matches the trade the card shows.
    submit({ sides: next, season: tradeSeason });
  }

  // The trade comes from the state by default. A finder card passes its own, because its picks land in state one render later.
  async function submit(trade?: TradeToGrade) {
    const toGrade = trade ?? { sides, season: target.season };
    const body = analyzeRequest(toGrade.sides, toGrade.season);
    if (body === null || !everySideTrades(toGrade.sides)) return;
    const run = request.start();
    const { controller } = run;
    // Only a finder card passes a trade, and only that path scrolls to the result.
    scrollToResult.current = trade !== undefined;
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, TIMEOUT_MS);
    setGrade({ status: "grading" });
    setEditing(false);
    countEvent("analyze-grade");
    try {
      const doc = await postAnalyze(target, passphrase, body, controller.signal);
      if (run.isCurrent()) setGrade({ status: "done", doc });
    } catch (error) {
      // An abort from unmount must not set state on a gone component.
      if (!run.isCurrent()) return;
      if (error instanceof ApiError && error.status === 401) onUnauthorized();
      else setGrade({ status: "error", ...toErrorLine(error, timedOut, "The grade took too long.") });
      if (error instanceof ApiError && error.status === 422) onRostersStale?.();
    } finally {
      clearTimeout(timer);
    }
  }

  /* The players a side gets, each with the team that gives him. A get of a player who left the roster shows no row. */
  function rowsOf(index: number): GotRow[] {
    return sides[index].gets.flatMap((get) => {
      const from = teamOf(teams, sides.find((side) => side.id === get.fromSide)?.rosterId ?? null);
      const player = from?.players.find((p) => p.player_id === get.playerId);
      return from && player ? [{ player, from }] : [];
    });
  }

  /* The other sides with a team: the tabs of the picker of one side. */
  function sourcesOf(index: number) {
    return sides.flatMap((side, i) => {
      const team = teamOf(teams, side.rosterId);
      return i !== index && team ? [{ sideId: side.id, team }] : [];
    });
  }

  /* Each player that a side other than this one gets, with the name of that team. */
  function elsewhereOf(index: number): Map<string, string> {
    return new Map(
      sides.flatMap((side, i) => (i === index ? [] : side.gets.map((get) => [get.playerId, teamOf(teams, side.rosterId)?.team ?? SIDE_TITLES[i]] as const))),
    );
  }

  const playerSide = sheet?.kind === "players" ? sheet.side : null;

  /* The players a side of another team gets from Your Team. */
  const askerGives = sides.slice(1).flatMap((_, i) => rowsOf(i + 1).filter((row) => row.from.roster_id === asker));

  const form = (
    <>
      {/* The folded form stays in the page, so the picks, the sheets, and the finder cards keep their state for Edit. */}
      <div hidden={folded}>
        <section aria-label="Who gets what" className="mt-sp-5 flex flex-col gap-sp-4">
          <TeamsRow
            slots={sides.map((side, index) => ({ id: side.id, title: SIDE_TITLES[index], team: teamOf(teams, side.rosterId) }))}
            onPickSlot={(slot) => setSheet({ kind: "team", slot })}
            onAdd={() => setSheet({ kind: "add" })}
            locked={locked}
          />
          {/* From the tablet tier the cards are a two-column grid, one side per cell, in document order. A third and a fourth
              side wrap to the next row. relative holds a removed card that popLayout lifts out. */}
          <div className="relative flex flex-col gap-sp-3 tablet:grid tablet:grid-cols-2 tablet:items-start">
            {/* popLayout takes a removed card out of the flow at once, so the cards after it slide into place while it fades. */}
            <AnimatePresence initial={false} mode="popLayout">
              {sides.map((side, index) => (
                <motion.div key={side.id} layout={!off} className="min-w-0" {...enterExit(off)}>
                  <GetCard
                    title={SIDE_TITLES[index]}
                    team={teamOf(teams, side.rosterId)}
                    rows={rowsOf(index)}
                    canAdd={side.rosterId !== null && sourcesOf(index).length > 0}
                    onAdd={() => setSheet({ kind: "players", side: index })}
                    onRemovePlayer={(playerId) => removeGet(index, playerId)}
                    // Only the third and fourth sides can leave. A trade always has two sides.
                    onRemove={index >= 2 ? () => removeSide(side.id) : undefined}
                    locked={locked}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
          <p className="m-0 text-lead text-mute">Each team gives and gets at least one player.</p>
          {/* The error box is the last part of the form, so it sits right above the bar. */}
          {grade.status === "error" && (
            <div role="group" aria-label="The grade failed">
              <Card edge className="flex flex-col gap-sp-3">
                <div className="flex items-start gap-sp-2">
                  <CircleAlertIcon aria-hidden="true" className="mt-sp-0 size-sp-5 flex-none text-accent-ink" />
                  <ErrorLine>{grade.message}</ErrorLine>
                </div>
                {/* Every error shows Try Again, so the reader has one next step after a fix to the trade or a wait. */}
                <Button className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold" onClick={() => submit()}>
                  Try Again
                </Button>
              </Card>
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
              target={target}
              asker={myTeam.roster_id}
              passphrase={passphrase}
              onUnauthorized={onUnauthorized}
              onRostersStale={onRostersStale}
              onOpen={openTrade}
              locked={grading}
            />
          </div>
        )}
        <TeamSheet
          open={teamSheet !== null}
          title={teamSheet?.title ?? ""}
          teams={teams}
          taken={taken}
          onPick={(rosterId) => {
            teamSheet?.pick(rosterId);
            setSheet(null);
          }}
          onClose={() => setSheet(null)}
        />
        <PlayerSheet
          // The key gives each side a fresh tab, search, and chip.
          key={playerSide === null ? "closed" : sides[playerSide]?.id}
          open={playerSide !== null && sides[playerSide] !== undefined}
          title={playerSide === null ? "" : SIDE_TITLES[playerSide]}
          sources={playerSide === null ? [] : sourcesOf(playerSide)}
          gets={playerSide === null ? [] : (sides[playerSide]?.gets ?? [])}
          elsewhere={playerSide === null ? new Map() : elsewhereOf(playerSide)}
          onToggle={(get) => playerSide !== null && toggleGet(playerSide, get)}
          onClose={() => setSheet(null)}
        />
      </div>
      {/* Under a folded result the bar has no trade to grade again, so it hides until Edit. */}
      {!(folded && grade.status === "done") && <GradeBar ready={ready} grading={grading} onGrade={() => submit()} />}
    </>
  );

  const result = grade.status === "done" && (
    <div ref={resultRef}>
      <AnalyzeResult doc={grade.doc} />
    </div>
  );

  const hero = folded ? (
    <>
      <FoldLine
        asker={myTeam}
        others={sides.slice(1).flatMap((side) => teamOf(teams, side.rosterId) ?? [])}
        gives={askerGives.map((row) => row.player.name)}
        gets={rowsOf(0).map((row) => row.player.name)}
        onEdit={grade.status === "done" ? () => setEditing(true) : undefined}
      />
      {grading && <GradingHero />}
    </>
  ) : (
    <TitleHero />
  );

  return children({ hero, form, result });
}
