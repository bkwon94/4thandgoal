/**
 * The Finish list of The Race: one bar per Finish with its chance, its final record, and its odds of the Goal. A tap on a
 * Finish opens its Paths in place, with the copy of its case, and a second tap closes them. A tap on a Path opens its Week
 * plan in a sheet, and a Finish of a seed opens its own plan.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ChevronRight } from "lucide-react";
import { Fragment, useState } from "react";
import { Button } from "@cpc/design/ui/button";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import { BarChart, BarChartBar } from "@cpc/design/ui/bar-chart";
import type { Finish, SetResult, WeekPlan, WeekSim } from "../schema/sim-types";
import {
  conditionsText,
  finishLine,
  finishName,
  happensText,
  noneText,
  openText,
  sureText,
} from "./finish-copy";
import { LABEL, PRESS, oddsText, recordText } from "./format";
import { type GoalKey, goalName } from "./goals";
import { type OpenPlan, WeekPlanSheet } from "./week-plan";

/* --ease-smooth-out of transitions-dev. */
const EASE = [0.22, 1, 0.36, 1] as const;

/* The odds column is wider when a Finish reads "about 75%", so each row of one list keeps the same columns. */
const GRID = "grid grid-cols-[5.5rem_1fr_3.25rem] items-center gap-x-sp-3";
const GRID_ABOUT = "grid grid-cols-[5.5rem_1fr_5.75rem] items-center gap-x-sp-3";

const ROW = cn(
  PRESS,
  "min-h-touch rounded-report hover-fine:bg-raised aria-expanded:bg-raised px-sp-2 py-sp-2 w-full text-left",
  "transition-[background-color] duration-150 ease-out",
);

/* A bar that fills to its percent from the left. A Goal change or a What-if moves each bar with the stagger of 40 ms of
   transitions-dev. Reduced motion sets the fill at once. */
function FinishBar({ value, index, mine }: { value: number; index: number; mine: boolean }) {
  return (
    <span aria-hidden className="rounded-pill bg-bar-off h-sp-2 block overflow-hidden">
      <span
        className={cn(
          "rounded-pill block h-full origin-left transition-transform duration-400 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none",
          mine ? "bg-accent" : "bg-ink/80",
        )}
        style={{
          transform: `scaleX(${Math.min(100, Math.max(0, value)) / 100})`,
          transitionDelay: `${index * 40}ms`,
        }}
      />
    </span>
  );
}

/* `mine` is true for Your team: its bars take the accent and its copy says "you". Another team reads "they" in ink.
   `onTry` sets the results of a Week plan as a What-if. Only Your team has it, so only its plans show "Try it". */
export function FinishList({
  sim,
  finishes,
  winsLeft,
  goal,
  mine,
  onTry,
}: {
  sim: WeekSim;
  finishes: Finish[];
  winsLeft: number;
  goal: GoalKey;
  mine: boolean;
  onTry?: (set: SetResult[]) => void;
}) {
  const off = useMotionOff();
  const [open, setOpen] = useState<string | null>(null);
  const [plan, setPlan] = useState<OpenPlan>(null);
  const name = goalName(goal);
  const grid = finishes.some((finish) => finish.about) ? GRID_ABOUT : GRID;
  return (
    <div className="gap-sp-1 flex flex-col">
      <div aria-hidden className={cn(grid, "px-sp-2")}>
        <span className={cn(LABEL, "text-mute")}>Rest of season</span>
        <span className={cn(LABEL, "text-mute col-span-2")}>{`Odds of ${name}`}</span>
      </div>
      <BarChart
        aria-label={`Finish list for ${name}`}
        value={null}
        onValueChange={(value: string | null) =>
          setOpen((was) => (value === null || value === was ? null : value))
        }
        className="flex flex-col"
      >
        {finishes.map((finish, index) => {
          const key = finishName(finish, winsLeft);
          const expanded = open === key;
          return (
            <Fragment key={key}>
              <BarChartBar
                value={key}
                data-finish={key}
                data-odds={finish.odds}
                aria-expanded={expanded}
                aria-label={`${key}, ends ${recordText(finish.record)}, ${Math.round(finish.chance)}% likely: ${oddsText(finish.odds, finish.about)} odds of ${name}`}
                className={cn(ROW, grid)}
              >
                <span className="flex min-w-0 flex-col">
                  <span className="text-lead font-mono leading-snug font-bold tabular-nums">
                    {key}
                  </span>
                  <span className="text-meta text-mute leading-tight tabular-nums">
                    {`ends ${recordText(finish.record)}`}
                  </span>
                </span>
                <span className="gap-sp-1 flex min-w-0 flex-col">
                  <FinishBar value={finish.odds} index={index} mine={mine} />
                  <span className="text-meta text-mute leading-tight tabular-nums">
                    {`${Math.round(finish.chance)}% likely`}
                  </span>
                </span>
                <span className="text-lead text-right font-mono font-bold whitespace-nowrap tabular-nums">
                  {oddsText(finish.odds, finish.about)}
                </span>
              </BarChartBar>
              <AnimatePresence initial={false}>
                {expanded && (
                  <motion.section
                    key="paths"
                    aria-label={`Paths at ${key}`}
                    initial={off ? { opacity: 0 } : { opacity: 0, y: -4, filter: "blur(2px)" }}
                    animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                    exit={{ opacity: 0, transition: { duration: 0.15 } }}
                    transition={off ? { duration: 0.15 } : { duration: 0.25, ease: EASE }}
                    className="px-sp-2 pt-sp-1 pb-sp-3"
                  >
                    <Paths
                      sim={sim}
                      finish={finish}
                      winsLeft={winsLeft}
                      goal={goal}
                      mine={mine}
                      onPlan={(next) => setPlan({ finish, plan: next })}
                    />
                  </motion.section>
                )}
              </AnimatePresence>
            </Fragment>
          );
        })}
      </BarChart>
      <WeekPlanSheet
        sim={sim}
        open={plan}
        goal={goal}
        winsLeft={winsLeft}
        mine={mine}
        onClose={() => setPlan(null)}
        onTry={
          onTry &&
          ((set) => {
            setPlan(null);
            onTry(set);
          })
        }
      />
    </div>
  );
}

const PATH_ROW = cn(
  PRESS,
  "-mx-sp-2 gap-sp-2 rounded-report px-sp-2 py-sp-2 hover-fine:bg-raised min-h-touch flex items-center text-left",
  "transition-[background-color] duration-150 ease-out",
);

/* The Paths of one Finish under its line, or the one sentence of its case. Each Path with a Week plan is a row that opens
   it. A Finish of a seed has no Path, so its own plan shows as one row under its sentence. */
function Paths({
  sim,
  finish,
  winsLeft,
  goal,
  mine,
  onPlan,
}: {
  sim: WeekSim;
  finish: Finish;
  winsLeft: number;
  goal: GoalKey;
  mine: boolean;
  onPlan: (plan: WeekPlan) => void;
}) {
  const note =
    finish.case === "sure"
      ? sureText(goal, mine)
      : finish.case === "none"
        ? noneText(goal)
        : finish.paths.length === 0
          ? openText
          : null;
  return (
    <div className="gap-sp-2 border-rule pl-sp-3 flex flex-col border-l-2">
      <p className="text-row m-0 font-bold tabular-nums">{finishLine(finish, winsLeft)}</p>
      {note !== null ? (
        <>
          <p className="text-meta text-mute m-0 text-pretty">{note}</p>
          {finish.plan && finish.case !== "none" && (
            <Button
              variant="plain"
              type="button"
              aria-label={`Week plan: ${mine ? "your" : "their"} plan to ${recordText(finish.record)}`}
              onClick={() => onPlan(finish.plan!)}
              className={cn(PATH_ROW, "text-row font-bold")}
            >
              <span className="min-w-0 flex-1">{`See ${mine ? "your" : "their"} plan to ${recordText(finish.record)}`}</span>
              <ChevronRight aria-hidden className="text-mute size-4 flex-none" />
            </Button>
          )}
        </>
      ) : (
        <>
          {finish.case === "best" && <p className={cn(LABEL, "text-mute m-0")}>Best chance</p>}
          <ul className="gap-sp-2 m-0 flex list-none flex-col p-0">
            {finish.paths.map((path) => (
              <li
                key={path.conditions.map((c) => `${c.roster_id}:${c.record.join("-")}`).join(",")}
                className="gap-sp-0 flex flex-col"
              >
                {path.plan ? (
                  <Button
                    variant="plain"
                    type="button"
                    aria-label={`Week plan: ${conditionsText(sim, path)} ${happensText(path, goal, mine)}`}
                    onClick={() => onPlan(path.plan!)}
                    className={PATH_ROW}
                  >
                    <PathText sim={sim} path={path} goal={goal} mine={mine} />
                    <ChevronRight aria-hidden className="text-mute size-4 flex-none" />
                  </Button>
                ) : (
                  <PathText sim={sim} path={path} goal={goal} mine={mine} />
                )}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

function PathText({
  sim,
  path,
  goal,
  mine,
}: {
  sim: WeekSim;
  path: Finish["paths"][number];
  goal: GoalKey;
  mine: boolean;
}) {
  return (
    <span className="gap-sp-0 flex min-w-0 flex-1 flex-col">
      <span className="text-body leading-snug text-pretty">{conditionsText(sim, path)}</span>
      <span className="text-meta text-mute leading-tight tabular-nums">
        {happensText(path, goal, mine)}
      </span>
    </span>
  );
}
