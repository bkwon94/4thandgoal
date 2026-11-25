/**
 * The sim page of Your team. In the regular season it is The Race, variant D of decision 04 of playoff-paths: the title, the Goal
 * switch, the Your team card that opens in place with the Finish list, the week card, and the replay, then the League board.
 * A tap on another team of the board opens its Finish list in a sheet.
 */
"use client";

import { Button } from "@cpc/design/ui/button";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, Play, RotateCcw, Shuffle } from "lucide-react";
import { useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import { Collapsible, CollapsiblePanel, CollapsibleTrigger } from "@cpc/design/ui/collapsible";
import { cn } from "@cpc/design/lib/utils";
import type { SetResult, WeekSim } from "../schema/sim-types";
import type { WhatIfApi } from "../lib/what-if-api";
import { SimStage, type StageAsk } from "../stage/sim-stage";
import { LABEL, PRESS, nameOf, oddsText, recordText, resultName } from "./format";
import { GoalSwitch } from "./goal-switch";
import { type GoalKey, goalName, goalShort, hasBye, openGoal, pageGoals } from "./goals";
import { FinishList } from "./finish-list";
import { InPlayoffs, seasonLine } from "./in-playoffs";
import { LeagueBoard } from "./league-board";
import { SoftText } from "./parts";
import { TeamSheet } from "./team-sheet";
import { useWhatIf } from "./use-what-if";
import { WeekCard } from "./week-card";

/* The avatar src of each team by roster id, with the base path, from the latest week. */
export type Avatars = Record<string, string>;

/* The line of the set results, such as "Wk 11 win, beat median · Wk 12 lose". */
const setText = (set: SetResult[]) =>
  set.map((result) => `Wk ${result.week} ${resultName(result).toLowerCase()}`).join(" · ");

/* `random` gives a number in [0, 1), as Math.random does. The replay draws its run with it, so a test can set it.
   `onYou` makes another team Your team, from its sheet. The app keeps the choice. */
export function SimPage({
  sim,
  you,
  avatars = {},
  whatIf,
  random = Math.random,
  onYou,
}: {
  sim: WeekSim;
  you: number;
  avatars?: Avatars;
  whatIf?: WhatIfApi;
  random?: () => number;
  onYou?: (id: number) => void;
}) {
  if (sim.pages[you].playoffs)
    return <PlayoffSimPage sim={sim} you={you} avatars={avatars} whatIf={whatIf} random={random} />;
  return (
    <RegularSimPage
      sim={sim}
      you={you}
      avatars={avatars}
      whatIf={whatIf}
      random={random}
      onYou={onYou}
    />
  );
}

/* The sim page with no regular week left: Your team with its title odds, then the playoff cards. No week switch and no
   ladder, because no regular week is left to win. A tap on a tile of the bracket game of Your team sets a What-if, with
   the set line and the line of a failed call of the regular weeks. Before the final, "Sim the season" replays the
   playoffs. After the final, no replay is left to play. */
function PlayoffSimPage({
  sim,
  you,
  avatars,
  whatIf,
  random,
}: {
  sim: WeekSim;
  you: number;
  avatars: Avatars;
  whatIf?: WhatIfApi;
  random: () => number;
}) {
  const file = sim.pages[you];
  const playoffs = file.playoffs!;
  const what = useWhatIf(file, whatIf);
  const shown = what.page.playoffs ?? playoffs;
  const name = nameOf(sim, you);
  const live = playoffs.alive && playoffs.champion === null;
  const game = playoffs.game;
  const chosen =
    game === null ? null : (what.set.find((result) => result.week === game.week) ?? null);
  const [replay, setReplay] = useState<StageAsk | null>(null);
  return (
    <div className="gap-sp-3 px-gutter pt-sp-4 pb-sp-6 tablet:px-0 flex flex-col">
      <section
        aria-label="Your team"
        aria-busy={what.pending}
        className="gap-sp-3 flex w-full flex-col"
      >
        <div className="gap-sp-3 flex items-center">
          <PhotoFrame src={avatars[String(you)] ?? null} name={name} size="md" decorative />
          <div className="min-w-0 flex-1">
            <h1 className="text-stat m-0 leading-tight font-bold text-balance">{name}</h1>
            <p className="text-meta text-mute m-0 text-pretty tabular-nums">{`${recordText(file.record)} · ${seasonLine(playoffs, you)}`}</p>
          </div>
          {live && (
            <div className="flex flex-none flex-col items-end">
              <SoftText
                text={oddsText(shown.title)}
                className={cn(
                  "text-score justify-items-end font-mono leading-none font-bold tabular-nums transition-opacity duration-150 ease-out",
                  what.pending && "opacity-50",
                )}
              />
              <span className={cn(LABEL, "pt-sp-1 text-mute")}>Title odds</span>
            </div>
          )}
        </div>
        <SetLine set={what.set} onReset={what.reset} />
        {what.down && (
          <p role="status" className="text-meta text-mute m-0 text-pretty">
            The What-if is not available now.
          </p>
        )}
      </section>
      <InPlayoffs
        sim={sim}
        you={you}
        avatars={avatars}
        shown={shown}
        whatIf={{
          chosen,
          title: what.runs === null ? null : shown.title,
          onChoose: (choice) => game !== null && what.choose(game.week, choice),
        }}
      />
      {playoffs.champion === null && (
        <SimButtons week={null} waiting={what.pending} onAsk={setReplay} />
      )}
      {replay !== null && (
        <SimStage
          sim={sim}
          runs={what.runs ?? sim}
          avatars={avatars}
          yourTeam={you}
          ask={replay}
          random={random}
          onDone={() => setReplay(null)}
        />
      )}
    </div>
  );
}

function RegularSimPage({
  sim,
  you,
  avatars,
  whatIf,
  random,
  onYou,
}: {
  sim: WeekSim;
  you: number;
  avatars: Avatars;
  whatIf?: WhatIfApi;
  random: () => number;
  onYou?: (id: number) => void;
}) {
  const file = sim.pages[you];
  const name = nameOf(sim, you);
  const what = useWhatIf(file, whatIf);
  const page = what.page;
  const [goal, setGoal] = useState<GoalKey>(() => openGoal(file));
  const [cardOpen, setCardOpen] = useState(true);
  const off = useMotionOff();
  const [replay, setReplay] = useState<StageAsk | null>(null);
  const [other, setOther] = useState<number | null>(null);
  // The Finish list follows the page of a What-if answer, and the file when the answer holds none.
  const finishes = page.finishes[goal] ?? file.finishes[goal] ?? [];

  const card = what.card;
  const nextWeek = file.week_card?.week ?? null;
  // The spot odds follow the What-if through the playoff odds of the page. Another Goal reads the Goals of the page, and
  // the file when the answer holds none.
  const goalOdds =
    goal === "spot"
      ? page.playoff
      : ((pageGoals(page)[goal] ?? pageGoals(file)[goal])?.odds ?? null);
  const openCard = () => {
    setCardOpen(true);
    document
      .getElementById("race-you")
      ?.scrollIntoView({ behavior: off ? "auto" : "smooth", block: "start" });
  };

  return (
    <div className="gap-sp-4 px-gutter pt-sp-4 pb-sp-6 tablet:px-0 flex flex-col">
      <header className="gap-sp-1 flex flex-col">
        <h1 className="text-headline m-0 leading-none font-bold tracking-tight text-balance">
          The Race
        </h1>
        <p className="text-meta text-mute m-0 tabular-nums">
          {`After week ${sim.week} · ${file.weeks_left} weeks left`}
        </p>
      </header>
      <GoalSwitch
        goal={goal}
        onGoal={setGoal}
        spots={sim.parameters.playoff_spots}
        bye={hasBye(sim)}
      />
      <section
        id="race-you"
        aria-label="Your team"
        aria-busy={what.pending}
        className="gap-sp-3 flex w-full scroll-mt-24 flex-col"
      >
        <Collapsible
          open={cardOpen}
          onOpenChange={setCardOpen}
          className="rounded-card border-ink bg-card flex min-w-0 flex-col border-2"
        >
          <CollapsibleTrigger
            className={cn(
              PRESS,
              "group rounded-card px-sp-3 py-sp-3 gap-sp-3 flex w-full items-center text-left",
            )}
          >
            <PhotoFrame src={avatars[String(you)] ?? null} name={name} size="md" decorative />
            <span className="gap-sp-1 flex min-w-0 flex-1 flex-col">
              <span className={cn(LABEL, "text-mute")}>Your team</span>
              <span className="text-lead leading-tight font-bold text-pretty">{name}</span>
              <span className="text-meta text-mute tabular-nums">{recordText(file.record)}</span>
            </span>
            <span className="flex flex-none flex-col items-end">
              <span data-goal-odds={oddsText(goalOdds)} className="flex">
                <SoftText
                  text={oddsText(goalOdds)}
                  className={cn(
                    "text-score text-accent-ink justify-items-end font-mono leading-none font-bold tabular-nums transition-opacity duration-150 ease-out",
                    what.pending && "opacity-50",
                  )}
                />
              </span>
              <span className={cn(LABEL, "pt-sp-1 text-mute")}>{`${goalShort(goal)} odds`}</span>
            </span>
            <ChevronDown
              aria-hidden
              className="text-mute size-5 flex-none transition-transform duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] group-data-[open]:-scale-y-100 motion-reduce:transition-none"
            />
          </CollapsibleTrigger>
          <CollapsiblePanel>
            <div className="gap-sp-3 px-sp-3 pb-sp-4 flex flex-col">
              <section aria-labelledby="race-finish-title" className="gap-sp-2 flex flex-col">
                <div className="gap-sp-1 flex flex-col">
                  <h2
                    id="race-finish-title"
                    className="text-lead m-0 leading-tight font-bold text-balance"
                  >
                    {`Your odds of ${goalName(goal)} by final record`}
                  </h2>
                  {goal === "spot" && (
                    <SoftText
                      text={page.sentence}
                      className={cn(
                        "text-body transition-opacity duration-150 ease-out",
                        what.pending && "opacity-50",
                      )}
                    />
                  )}
                  <p className="text-meta text-mute m-0 text-pretty">
                    {sim.parameters.median_game
                      ? "Your game and the median each count. Tap a record to see what you need."
                      : "Tap a record to see what you need."}
                  </p>
                </div>
                <div
                  className={cn(
                    "-mx-sp-2 transition-opacity duration-150 ease-out",
                    what.pending && "opacity-50",
                  )}
                >
                  <FinishList
                    key={goal}
                    sim={sim}
                    finishes={finishes}
                    winsLeft={page.wins_left}
                    goal={goal}
                    mine
                    scoreToBeat={page.score_to_beat}
                    onTry={what.chooseAll}
                  />
                </div>
              </section>
              {card !== null && (
                <WeekCard
                  sim={sim}
                  card={card}
                  goal={goal}
                  status={(pageGoals(page)[goal] ?? pageGoals(file)[goal])?.status ?? "open"}
                  scoreToBeat={page.score_to_beat.find((beat) => beat.week === card.week)}
                  set={what.set}
                  pending={what.pending}
                  onChoose={(choice) => what.choose(card.week, choice)}
                />
              )}

              <SimButtons week={nextWeek} waiting={what.pending} onAsk={setReplay} />
            </div>
          </CollapsiblePanel>
        </Collapsible>
        <SetLine set={what.set} onReset={what.reset} />
        {what.down && (
          <p role="status" className="text-meta text-mute m-0 text-pretty">
            The What-if is not available now.
          </p>
        )}
      </section>

      <LeagueBoard
        sim={sim}
        board={what.board ?? undefined}
        you={you}
        goal={goal}
        onYou={openCard}
        onOther={setOther}
      />
      <TeamSheet
        sim={sim}
        team={other}
        goal={goal}
        onClose={() => setOther(null)}
        onYou={
          onYou &&
          ((id) => {
            setOther(null);
            onYou(id);
          })
        }
      />

      {replay !== null && (
        <SimStage
          sim={sim}
          runs={what.runs ?? sim}
          avatars={avatars}
          yourTeam={you}
          ask={replay}
          random={random}
          onDone={() => setReplay(null)}
        />
      )}
    </div>
  );
}

/* The two buttons of the replay, in the flow under the week card and never fixed over content. The playoff weeks have
   only "Sim the season". While a What-if call runs, they wait, so the replay always plays a run of the set line. */
function SimButtons({
  week,
  waiting,
  onAsk,
}: {
  week: number | null;
  waiting: boolean;
  onAsk: (ask: StageAsk) => void;
}) {
  const base = cn(
    PRESS,
    "min-h-touch gap-sp-2 rounded-report px-sp-3 text-body flex flex-1 items-center justify-center font-bold",
    "transition-opacity duration-150 ease-out disabled:opacity-50",
  );
  return (
    <div className="gap-sp-2 flex w-full">
      {week !== null && (
        <Button
          variant="plain"
          type="button"
          disabled={waiting}
          onClick={() => onAsk({ mode: "week", week })}
          className={cn(base, "border-ink bg-page text-ink hover-fine:bg-card border")}
        >
          <Play aria-hidden className="size-4" />
          {`Sim week ${week}`}
        </Button>
      )}
      <Button
        variant="plain"
        type="button"
        disabled={waiting}
        onClick={() => onAsk({ mode: "season" })}
        className={cn(base, "bg-accent text-on-dark hover-fine:opacity-90")}
      >
        <Shuffle aria-hidden className="size-4" />
        Sim the season
      </Button>
    </div>
  );
}

/* The line at the top that lists each set result, with a Reset back to the numbers of the file. It grows from no
   height with the accordion of transitions-dev, so the page below moves down and does not jump. */
function SetLine({ set, onReset }: { set: SetResult[]; onReset: () => void }) {
  const off = useMotionOff();
  return (
    <AnimatePresence initial={false}>
      {set.length > 0 && (
        <motion.section
          aria-label="What-if"
          initial={off ? { opacity: 0 } : { opacity: 0, height: 0 }}
          animate={off ? { opacity: 1 } : { opacity: 1, height: "auto" }}
          exit={
            off
              ? { opacity: 0, transition: { duration: 0.1 } }
              : { opacity: 0, height: 0, transition: { duration: 0.15, ease: [0.22, 1, 0.36, 1] } }
          }
          transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
          className="overflow-hidden"
        >
          <div className="min-h-touch gap-sp-2 rounded-report bg-card pl-sp-3 flex items-center">
            <p className="py-sp-2 text-meta m-0 min-w-0 flex-1 text-pretty">
              <span className="font-bold">What-if: </span>
              {setText(set)}
            </p>
            <Button
              variant="plain"
              type="button"
              onClick={onReset}
              className={cn(
                PRESS,
                "min-h-touch gap-sp-1 rounded-report px-sp-3 text-meta text-ink hover-fine:text-accent-ink flex flex-none items-center font-bold",
              )}
            >
              <RotateCcw aria-hidden className="size-4" />
              Reset
            </Button>
          </div>
        </motion.section>
      )}
    </AnimatePresence>
  );
}
