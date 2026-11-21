/**
 * The trade form, the Stack: the hero, the teams row, one card for each side that says what it gets, the sheets, and the grade bar.
 * It owns the trade and the grade state, and it posts the trade to the analyze route. With the finder on, the switch of the
 * hero moves between Grade a trade and Find a trade, and Find mode takes the place of the hero and the form.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState, type ReactNode } from "react";
import AnalyzeResult from "./analyze-result";
import { ArrowLeftIcon, CircleAlertIcon } from "lucide-react";
import { Card } from "@cpc/design/parts/card";
import { ErrorLine } from "@cpc/design/parts/error-line";
import { Hero } from "@cpc/design/parts/hero";
import { HeroMesh } from "@cpc/design/parts/hero-mesh";
import { waitDrive } from "@cpc/design/parts/mesh-canvas";
import { Rise } from "@cpc/design/parts/rise";
import { GetCard, type GotRow } from "./get-card";
import { GradeBar } from "./grade-bar";
import { Sheet } from "./sheet";
import { StageLines } from "./stage-lines";
import { PlayerSheet } from "./player-sheet";
import { TeamSheet } from "./team-sheet";
import { TeamsRow } from "./teams-row";
import { ModeSwitch } from "./mode-switch";
import { TradeFinder } from "./trade-finder";
import { TradeOnStage, type StageSide } from "./trade-on-stage";
import { Button } from "@cpc/design/ui/button";
import { PendingButton } from "@cpc/design/ui/pending-button";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { useRequest } from "./use-request";
import { stageLines, type StageTrade } from "../lib/stage-lines";
import type { AnalyzeResponse, FindResponse, FinderTrade } from "../lib/analyze-types";
import { finderRead } from "../lib/finder-read";
import type { AnalyzerMode } from "../lib/mode";
import { ApiError, type ApiTarget, postAnalyze, toErrorLine, type Team } from "../lib/api";
import {
  analyzeRequest,
  dropStaleGets,
  EMPTY_SIDES,
  everySideTrades,
  type Get,
  haloLevel,
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
  // The sides of a link from the front door, such as a typed trade with an unsure player. Null keeps the empty Stack.
  prefill?: Sides | null;
  /* The page places the parts, so it can put its own lines, such as a failed fetch, between the hero and the form.
     The form keeps the grade state, so it hands the parts out and does not lift the state. */
  children?: (parts: FormParts) => ReactNode;
  // The half of the switch on the screen. The page owns it, because the address of the page names it. Find needs the
  // finder flag, so with the flag off the form shows Grade and no switch.
  mode?: AnalyzerMode;
  // A card that opens its Full Result asks for a "push", so the back gesture returns to the cards.
  onModeChange?: (mode: AnalyzerMode, how?: "push") => void;
  // The eyebrow of the hero in both modes, such as the countdown to the trade deadline. With none, it names the tool.
  eyebrow?: ReactNode;
};

/* The hero, the form, and the result of a done grade. In Find mode the hero holds Find and its cards, and the form hides. */
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

/* The hero while the grade runs, in the hero slots: the eyebrow and the locked switch of the page, the title, the line,
   and the wait as the feature. The Find wait shows the same eyebrow and switch, so the two waits read as one.
   The read that replaces it opens with a level-two heading, so this title is level two too. The stage lines run under
   the title, in a part of their own. A screen reader skips them. The page holds one status, the pending announcement
   "Grading the trade" of the grade button, so the hero holds none, and a screen reader hears one message. The trade stays
   on the stage, and the mesh weighs each side in turn under it, so the wait shows what the grade does. The drive starts
   with the hero, so the mesh moves on the first frame after the tap. The trade is read once, because the grade locks
   the form. With motion off, the mesh stays still and flat. */
function GradingHero({ trade, stage, eyebrow, toggle }: { trade: StageTrade; stage: StageSide[]; eyebrow: ReactNode; toggle?: ReactNode }) {
  const [lines] = useState(() => stageLines(trade));
  const [drive] = useState(() => waitDrive(performance.now()));
  return (
    <Hero
      label="Grading the Trade"
      art={<HeroMesh drive={drive} />}
      level={2}
      eyebrow={eyebrow}
      toggle={toggle}
      title="Grading the Trade"
      meta="This can take up to a minute."
      feature={
        // aria-busy marks the wait part as busy until the grade replaces it. It has no role, because the grade button
        // holds the one status of the wait.
        <div aria-busy="true">
          <div aria-hidden="true" className="flex flex-col gap-sp-5">
            <StageLines lines={lines} />
            {/* The headshots go up to the stage on the tap, so the trade on the scale is the one the reader built. */}
            <TradeOnStage sides={stage} show="tokens" rise />
          </div>
        </div>
      }
    />
  );
}

/* The hero of the page, in the hero slots: the name of the tool or the deadline as the eyebrow, the switch, the title, and the question of the Stack as the meta line.
   Its ground is the mesh, calm and flat in idle, with no scene. Once a player is in the Stack, the trade shows on the
   stage as the feature, one row per side with a count of its players. The cards of the Stack below show each player, so
   the stage waits for the grade to show the faces. The grading hero and the read take its place while a grade runs and under a result. */
function TitleHero({ stage, eyebrow, toggle }: { stage: StageSide[]; eyebrow: ReactNode; toggle?: ReactNode }) {
  const hasPlayer = stage.some((side) => side.players.length > 0);
  return (
    <Hero
      label="Trade Analyzer"
      art={<HeroMesh />}
      eyebrow={eyebrow}
      toggle={toggle}
      title="Trade Analyzer"
      meta={<Rise step={1}>Who gets what?</Rise>}
      feature={hasPlayer ? <TradeOnStage sides={stage} show="count" /> : undefined}
    />
  );
}

export function TradeForm({
  teams,
  target,
  finderOn,
  passphrase,
  onUnauthorized,
  onRostersStale,
  prefill = null,
  children = stackParts,
  mode = "grade",
  onModeChange,
  eyebrow = "Trade Analyzer",
}: TradeFormProps) {
  const [sides, setSides] = useState<Sides>(EMPTY_SIDES);
  // The id of the next added side. EMPTY_SIDES holds ids 0 and 1, and an id is never reused, so a key never repeats.
  const nextSideId = useRef(EMPTY_SIDES.length);
  const [sheet, setSheet] = useState<OpenSheet>(null);
  const [grade, setGrade] = useState<GradeState>({ status: "idle" });
  // A search of Find mode runs, so the switch stays on Find until it ends.
  const [finding, setFinding] = useState(false);
  // The mode of the last render. The switch of a new hero starts from it, so its pill slides from the old half.
  const shownMode = useRef(mode);
  useEffect(() => {
    shownMode.current = mode;
  }, [mode]);
  // The sheet edits a draft while the result stays in place. Cancel restores the trade that produced that result.
  const [editing, setEditing] = useState(false);
  const savedSides = useRef<Sides>(sides);
  // A late answer from an old trade must not overwrite the state of a new one.
  const request = useRequest();
  // A finder card asks for the full result, so the page scrolls the result into view when the grade ends.
  const resultRef = useRef<HTMLDivElement>(null);
  const scrollToResult = useRef(false);
  const off = useMotionOff();
  // The Full Result of a finder card shows a way back to the cards. A trade that the reader built or graded shows none.
  const [fromCard, setFromCard] = useState(false);
  // The offer of the card that opened, so the page returns to that card when the cards show again.
  const openedOffer = useRef<string | null>(null);
  const finderRef = useRef<HTMLDivElement>(null);
  // The finder mounts when Find first shows, and then stays mounted. Its cards and its near fold are state of the
  // finder, so a Full Result that unmounted it would lose them, and the back gesture would return to an empty finder.
  // Keeping it mounted and hidden is plainer than lifting its result up, and a plain switch keeps the cards too.
  const [finderKept, setFinderKept] = useState(false);

  // A link fills the Stack once, when the page reads its query. A later change of the trade is the reader's own.
  useEffect(() => {
    if (prefill) setSides(prefill);
  }, [prefill]);

  // The scroll waits for the result, because the result is not in the page until the grade ends.
  useEffect(() => {
    if (grade.status !== "done" || !scrollToResult.current) return;
    scrollToResult.current = false;
    resultRef.current?.scrollIntoView({ behavior: off ? "auto" : "smooth", block: "start" });
  }, [grade.status, off]);

  // The cards show again after a back from a Full Result, so the page goes to the card that opened.
  useEffect(() => {
    if (!(finderOn && mode === "find") || openedOffer.current === null) return;
    const offer = openedOffer.current;
    openedOffer.current = null;
    const card = [...(finderRef.current?.querySelectorAll<HTMLElement>("[data-offer-id]") ?? [])].find((el) => el.dataset.offerId === offer);
    card?.scrollIntoView({ behavior: off ? "auto" : "smooth", block: "start" });
  }, [finderOn, mode, off]);

  /* Edit keeps the result in place and saves the trade for each way out without a submit. */
  function edit() {
    savedSides.current = sides;
    setEditing(true);
  }

  function cancelEdit() {
    setSides(dropStaleGets(savedSides.current, teams));
    setSheet(null);
    setEditing(false);
  }

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
  // A link can fill a whole trade before the rosters arrive. The stage and the stage lines read the teams, so a grade
  // that starts before them shows an empty stage and names "Your Team" in place of a manager. The bar waits for the teams.
  const ready = teams.length > 0 && everySideTrades(sides);
  // The grade locks the form, so the result always matches the picks on the screen. A result or an error ends it.
  const grading = grade.status === "grading";
  const findMode = finderOn && mode === "find";
  if (findMode && !finderKept) setFinderKept(true);
  // The form hides while the grade runs, under a result, and in Find mode, so the hero and the read lead the page. The
  // stage of the hero shows the trade, so no line repeats it.
  const formHidden = grading || grade.status === "done" || findMode;
  // With no teams yet, no slot and no picker has anything to show.
  const locked = grading || teams.length === 0;
  const teamSheet = teamSheetOf(sheet);
  // The teams that another side holds. The team sheet of a slot leaves its own team on, so a tap on it changes nothing.
  const taken = sides.flatMap((side, i) => (side.rosterId === null || teamSheet?.slot === i ? [] : [side.rosterId]));

  /* A draft leaves the graded result in place until submit. A page edit clears it and drops a late answer. */
  function changeTrade(update: (current: Sides) => Sides) {
    request.drop();
    setSides(update);
    if (!editing) {
      setGrade({ status: "idle" });
      setFromCard(false);
    }
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
     The find sent the read of each pick, so the card shows that read with no second grade. A trade of a fallback has
     no read, so it reuses this submit and needs no query or route of its own. */
  function openTrade(trade: FinderTrade, find: FindResponse) {
    const partner = trade.sides.find((side) => side.roster_id !== asker);
    const own = trade.sides.find((side) => side.roster_id === asker);
    if (asker === null || !own || !partner) return;
    // A finder trade has two sides, so the card fills the first two sides, and a third side leaves the trade.
    const [mine, theirs] = sides;
    const toGets = (side: { gives: { player_id: string }[] }, fromSide: number) =>
      side.gives.map((p) => ({ playerId: p.player_id, fromSide }));
    const next: Sides = [
      { id: mine.id, rosterId: asker, gets: toGets(partner, theirs.id) },
      { id: theirs.id, rosterId: partner.roster_id, gets: toGets(own, mine.id) },
    ];
    setSides(next);
    // The grade of a card shows in Grade mode, so the address and the switch name the mode of the result. The push
    // gives the back gesture an entry to leave, and it returns to the cards.
    onModeChange?.("grade", "push");
    openedOffer.current = trade.offer_id;
    setFromCard(true);
    const read = finderRead(trade, find);
    if (read !== null) {
      // A late answer of an earlier grade must not replace the read of the card.
      request.drop();
      setEditing(false);
      setSheet(null);
      scrollToResult.current = true;
      setGrade({ status: "done", doc: read });
      return;
    }
    // The new picks are not in state until the next render, so the submit gets them as an argument.
    // The season is the one of the finder document, so the grade matches the trade the card shows.
    submit({ sides: next, season: find.season });
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
    // A grade that the reader starts is not the card any more, so the way back to the cards goes.
    if (trade === undefined) setFromCard(false);
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, TIMEOUT_MS);
    setGrade({ status: "grading" });
    setEditing(false);
    setSheet(null);
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

  const stack = (
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
  );

  // The picker sheets share the editor's Drawer context, so Escape and focus return to the editor first.
  const pickers = (
    <>
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
    </>
  );

  const gradeBar = <GradeBar ready={ready} grading={grading} level={haloLevel(sides)} onGrade={() => submit()} inEditSheet={editing} />;
  const form = (
    <>
      {/* The bar sticks inside this part, so it stays pinned at the bottom of the screen over the form and rests at the end
          of the form, above the finder. The part holds the form section and the bar, and nothing after them. */}
      {/* The page keeps its form while a grade runs, so the pending button stays mounted. */}
      <div>
        <div hidden={formHidden}>{!editing && stack}</div>
        {grade.status !== "done" && !findMode && gradeBar}
      </div>
      <div hidden={formHidden}>
        {!editing && pickers}
      </div>
      <Sheet
        open={editing}
        title="Edit the trade"
        onClose={cancelEdit}
        footer={
          <div className="flex items-center gap-sp-3">
            <button
              type="button"
              onClick={cancelEdit}
              className="press flex min-h-touch min-w-touch cursor-pointer items-center justify-center rounded-pill px-sp-2 text-meta font-bold text-accent-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              Cancel
            </button>
            {gradeBar}
          </div>
        }
      >
        {editing && stack}
        {editing && pickers}
      </Sheet>
    </>
  );

  /* The analyze document names each team but carries no avatar, so the result reads the avatars of the teams of the league. */
  const avatars = new Map(teams.map((team) => [team.roster_id, team.avatar]));

  // The result waits behind the cards, so a back from a Full Result shows the cards and no result under them.
  const result = grade.status === "done" && !findMode && (
    <div ref={resultRef}>
      {fromCard && (
        <PendingButton
          // The same step as the back gesture. The popstate of the browser returns the page to the cards.
          onClick={() => window.history.back()}
          pendingAnnouncement=""
          className="press mt-sp-4 flex min-h-touch cursor-pointer items-center gap-sp-2 rounded-pill px-sp-2 text-meta font-bold text-accent-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          <ArrowLeftIcon aria-hidden="true" className="size-sp-4" />
          Back to trade ideas
        </PendingButton>
      )}
      <AnalyzeResult doc={grade.doc} avatars={avatars} onEdit={edit} />
    </div>
  );

  // One pass over the sides gives the stage and the grading trade the same team and rows for each side.
  const sideViews = sides.map((side, index) => ({ side, index, team: teamOf(teams, side.rosterId), rows: rowsOf(index) }));

  /* The trade on the stage: one row for each side with a team, and the players it gets with their headshots. */
  const stage: StageSide[] = sideViews.flatMap(({ side, team, rows }) => {
    if (!team) return [];
    const players = rows.map(({ player }) => ({ id: player.player_id, name: player.name, headshot: player.headshot }));
    return [{ id: side.id, team: team.team, avatar: team.avatar, players }];
  });

  // The switch shows only with the finder on. A wait locks it, so a wait always ends in the mode that started it.
  const toggle = finderOn ? (
    <ModeSwitch value={mode} from={shownMode.current} onChange={(next) => onModeChange?.(next)} disabled={grading || finding} />
  ) : undefined;

  // Under a result the read is the hero, so the form puts no hero of its own above it. In Find mode the finder is the hero.
  const gradeHero = findMode ? null : grading ? (
    <GradingHero
      trade={sideViews.map(({ index, team, rows }) => ({
        team: team?.team ?? SIDE_TITLES[index],
        manager: team?.manager ?? SIDE_TITLES[index],
        gets: rows.map((row) => ({ name: row.player.name, position: row.player.position })),
      }))}
      stage={stage}
      eyebrow={eyebrow}
      toggle={toggle}
    />
  ) : formHidden ? null : (
    <TitleHero stage={stage} eyebrow={eyebrow} toggle={toggle} />
  );

  const hero = (
    <>
      {finderKept && (
        <div ref={finderRef} hidden={!findMode}>
          {/* The key resets the partner, the chip, and the cards when the asker changes. */}
          <TradeFinder
            key={myTeam?.roster_id ?? "none"}
            teams={teams}
            target={target}
            asker={myTeam?.roster_id ?? null}
            onAsker={(rosterId) => pickTeam(0, rosterId)}
            passphrase={passphrase}
            onUnauthorized={onUnauthorized}
            onRostersStale={onRostersStale}
            onOpen={openTrade}
            onFindingChange={setFinding}
            eyebrow={eyebrow}
            toggle={toggle}
          />
        </div>
      )}
      {gradeHero}
    </>
  );

  return children({ hero, form, result });
}
