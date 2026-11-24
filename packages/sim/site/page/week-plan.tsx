/**
 * The Week plan of a Path, or of a Finish of a seed, in a sheet: the header with the odds of "Try it", the order line, and
 * one row per week left with the result, the Score to beat, and the games to root for. Your team's plan ends on "Try it".
 */
"use client";

import { XIcon } from "lucide-react";
import { useState } from "react";
import { Button } from "@cpc/design/ui/button";
import { cn } from "@cpc/design/lib/utils";
import {
  Sheet,
  SheetBackdrop,
  SheetClose,
  SheetContent,
  SheetGrip,
  SheetTitle,
} from "@cpc/design/ui/sheet";
import type { Finish, ScoreToBeat, SetResult, WeekPlan, WeekSim } from "../schema/sim-types";
import { orderLine, planHeader, planResult, planRootFor, planScores } from "./finish-copy";
import { PRESS, nameOf } from "./format";
import type { GoalKey } from "./goals";

/* The plan that the sheet shows, with the Finish it ends at. Null while the sheet is closed. */
export type OpenPlan = { finish: Finish; plan: WeekPlan } | null;

/* The text of the "Try it" button, such as "Try it: you're in 81%". */
const tryText = (header: string) => `Try it: ${header.split(" · ")[1]}`;

export function WeekPlanSheet({
  sim,
  open,
  goal,
  winsLeft,
  mine,
  scoreToBeat,
  onClose,
  onTry,
}: {
  sim: WeekSim;
  open: OpenPlan;
  goal: GoalKey;
  winsLeft: number;
  mine: boolean;
  scoreToBeat: ScoreToBeat[];
  onClose: () => void;
  onTry?: (set: SetResult[]) => void;
}) {
  // The sheet keeps the last plan while it slides out, so its content never goes blank.
  const [kept, setKept] = useState<OpenPlan>(open);
  if (open !== null && open !== kept) setKept(open);
  const shown = open ?? kept;
  const header = shown ? planHeader(shown.finish, shown.plan, goal, mine) : "";
  const order = shown ? orderLine(shown.finish, shown.plan, winsLeft, mine) : null;
  const beat = (week: number) => scoreToBeat.find((entry) => entry.week === week);
  return (
    <Sheet
      side="bottom"
      open={open !== null}
      onOpenChange={(next: boolean) => {
        if (!next) onClose();
      }}
      container={typeof document === "undefined" ? undefined : document.body}
    >
      <SheetBackdrop />
      <SheetContent className="max-w-sheet rounded-t-report border-rule bg-card shadow-sheet mx-auto flex max-h-[88dvh] w-full flex-col border border-b-0">
        <SheetGrip className="mt-sp-2 h-sp-1 w-sp-6" />
        <div className="gap-sp-2 px-sp-4 pt-sp-3 flex flex-none items-start justify-between">
          <div className="min-w-0">
            <SheetTitle className="text-stat m-0 leading-tight font-bold text-balance tabular-nums">
              {header}
            </SheetTitle>
            {order !== null && (
              <p className="pt-sp-1 text-meta text-mute m-0 text-pretty">{order}</p>
            )}
          </div>
          <SheetClose
            aria-label="Close"
            className={cn(
              PRESS,
              "-mt-sp-2 -mr-sp-2 size-touch rounded-report text-mute hover-fine:text-ink flex flex-none items-center justify-center",
            )}
          >
            <XIcon aria-hidden className="size-5" />
          </SheetClose>
        </div>
        {/* oxlint-disable-next-line design/no-arbitrary-value -- the home bar of an iPhone needs the safe-area inset, which no token adds to a step */}
        <div className="gap-sp-3 px-sp-4 pt-sp-3 flex min-h-0 flex-col overflow-y-auto overscroll-contain pb-[calc(var(--spacing-sp-4)+env(safe-area-inset-bottom))]">
          {shown && (
            <ol aria-label="Weeks of the plan" className="gap-sp-2 m-0 flex list-none flex-col p-0">
              {shown.plan.weeks.map((week) => {
                const scores = planScores(week, beat(week.week));
                const roots = planRootFor(sim, week);
                return (
                  <li
                    key={week.week}
                    className="rounded-report border-rule bg-page p-sp-3 gap-sp-1 flex flex-col border"
                  >
                    <span className="text-row leading-snug font-bold text-pretty">
                      {`Week ${week.week} · vs ${nameOf(sim, week.opponent)}`}
                    </span>
                    <span className="text-body leading-snug text-pretty">{planResult(week)}</span>
                    {scores !== null && (
                      <span className="text-meta leading-snug text-pretty tabular-nums">
                        {scores}
                      </span>
                    )}
                    {roots !== null && (
                      <span className="text-meta text-mute leading-snug text-pretty">
                        <span className="text-ink font-bold">Root for: </span>
                        {roots}
                      </span>
                    )}
                  </li>
                );
              })}
            </ol>
          )}
          {shown && onTry && (
            <Button
              variant="plain"
              type="button"
              onClick={() =>
                onTry(
                  shown.plan.weeks.map((week) => ({
                    week: week.week,
                    game: week.game,
                    median: week.median,
                  })),
                )
              }
              className={cn(
                PRESS,
                "min-h-touch rounded-report bg-accent text-on-dark px-sp-3 text-body hover-fine:opacity-90 flex w-full flex-none items-center justify-center font-bold tabular-nums",
                "transition-opacity duration-150 ease-out",
              )}
            >
              {tryText(header)}
            </Button>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
