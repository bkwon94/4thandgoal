/**
 * The sheet of another team of the League board: its record, its odds of the Goal, each way of its Clinch lines this week,
 * its Finish list with the Paths of each Finish, and "Make this Your team". It keeps the last team while it slides out, so its content never goes blank.
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
import type { ClinchLine, WeekSim } from "../schema/sim-types";
import { clinchLinesOf, clinchWayTexts } from "./clinch-copy";
import { FinishList } from "./finish-list";
import { LABEL, PRESS, chanceText, nameOf, oddsText, recordText } from "./format";
import { type GoalKey, goalName, pageGoals } from "./goals";

/* Each stored way of the Clinch lines of the team for the Goal, most likely first, with its chance. The board shows only the
   first way of a line, so the sheet lists them all (decision 06). A line that clinches takes the second ink. */
function ClinchWays({ sim, lines }: { sim: WeekSim; lines: ClinchLine[] }) {
  if (lines.length === 0) return null;
  return (
    <section aria-label="This week" className="gap-sp-2 px-sp-2 flex flex-col">
      <h3 className={cn(LABEL, "text-mute m-0")}>This week</h3>
      {lines.map((line) => {
        const texts = clinchWayTexts(sim, line);
        return (
          <ul
            key={`${line.goal}-${line.status}`}
            data-clinch-line={line.status}
            className="gap-sp-2 m-0 flex list-none flex-col p-0"
          >
            {line.ways.map((way, index) => (
              <li
                key={texts[index]}
                data-clinch-way={line.status}
                className="gap-x-sp-3 grid grid-cols-[1fr_auto] items-baseline"
              >
                <span
                  className={cn(
                    "text-meta min-w-0 leading-snug text-pretty",
                    line.status === "in" ? "text-ink-2" : "text-ink",
                  )}
                >
                  {texts[index]}
                </span>
                <span className="text-meta text-mute leading-snug whitespace-nowrap tabular-nums">
                  {chanceText(way.chance)}
                </span>
              </li>
            ))}
          </ul>
        );
      })}
    </section>
  );
}

export function TeamSheet({
  sim,
  team,
  goal,
  onClose,
  onYou,
}: {
  sim: WeekSim;
  team: number | null;
  goal: GoalKey;
  onClose: () => void;
  onYou?: (id: number) => void;
}) {
  const [kept, setKept] = useState<number | null>(team);
  if (team !== null && team !== kept) setKept(team);
  const shown = team ?? kept;
  const page = shown === null ? undefined : sim.pages[shown];
  const name = shown === null ? "" : nameOf(sim, shown);
  const odds = page ? (pageGoals(page)[goal]?.odds ?? null) : null;
  const clinch = sim.board.find((row) => row.roster_id === shown)?.clinch ?? [];
  return (
    <Sheet
      side="bottom"
      open={team !== null}
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
            <SheetTitle className="text-stat m-0 leading-tight font-bold text-balance">
              {name}
            </SheetTitle>
            {page && (
              <p className="pt-sp-1 text-meta text-mute m-0 text-pretty tabular-nums">
                {`${recordText(page.record)} · ${oddsText(odds)} odds of ${goalName(goal)}`}
              </p>
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
        <div className="gap-sp-4 px-sp-2 pt-sp-3 flex min-h-0 flex-col overflow-y-auto overscroll-contain pb-[calc(var(--spacing-sp-4)+env(safe-area-inset-bottom))]">
          {page && shown !== null && (
            <>
              <ClinchWays sim={sim} lines={clinchLinesOf(clinch, goal)} />
              <FinishList
                key={`${shown}-${goal}`}
                sim={sim}
                finishes={page.finishes[goal] ?? []}
                winsLeft={page.wins_left}
                goal={goal}
                mine={false}
                scoreToBeat={page.score_to_beat}
              />
              {onYou && (
                <Button
                  variant="plain"
                  type="button"
                  onClick={() => onYou(shown)}
                  className={cn(
                    PRESS,
                    "min-h-touch rounded-report border-ink text-row text-ink hover-fine:bg-raised mx-sp-2 border font-bold",
                    "transition-[background-color] duration-150 ease-out",
                  )}
                >
                  Make this Your team
                </Button>
              )}
            </>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
