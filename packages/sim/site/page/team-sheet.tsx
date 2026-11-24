/**
 * The sheet of another team of the League board: its record, its odds of the Goal, its Finish list with the Paths of each
 * Finish, and "Make this Your team". It keeps the last team while it slides out, so its content never goes blank.
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
import type { WeekSim } from "../schema/sim-types";
import { FinishList } from "./finish-list";
import { PRESS, nameOf, oddsText, recordText } from "./format";
import { type GoalKey, goalName, pageGoals } from "./goals";

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
              <FinishList
                key={`${shown}-${goal}`}
                sim={sim}
                finishes={page.finishes[goal] ?? []}
                winsLeft={page.wins_left}
                goal={goal}
                mine={false}
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
