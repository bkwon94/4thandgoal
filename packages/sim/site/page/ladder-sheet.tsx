/**
 * The sentence of more wins and the ladder sheet it opens: each count of more wins, its playoff odds, and how likely it is.
 * The sentence comes from the build as it is, and the line under the row of `need` marks odds of 90% or more.
 */
"use client";

import { ChevronRight, XIcon } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@cpc/design/lib/utils";
import {
  Sheet,
  SheetBackdrop,
  SheetClose,
  SheetContent,
  SheetGrip,
  SheetTitle,
  SheetTrigger,
} from "@cpc/design/ui/sheet";
import type { SimPage } from "../schema/sim-types";
import { LABEL, PRESS, oddsText } from "./format";
import { Bar } from "./parts";

const ROW =
  "grid min-h-touch grid-cols-[3.75rem_1fr_4.75rem_3.5rem] items-center gap-x-sp-2 tablet:gap-x-sp-3";

/* `sentence` shows the sentence of the page, so the sim page can swap it softly when a What-if changes it. */
export function LadderSheet({
  page,
  medianGame,
  sentence,
}: {
  page: SimPage;
  medianGame: boolean;
  sentence?: ReactNode;
}) {
  const perWeek = medianGame
    ? "Each week gives 2 wins: one for your game, one for the median."
    : "Each week gives 1 win, for your game.";
  return (
    <Sheet side="bottom" container={typeof document === "undefined" ? undefined : document.body}>
      <SheetTrigger
        className={cn(
          PRESS,
          "min-h-touch gap-sp-2 rounded-report border-rule bg-page px-sp-3 py-sp-2 hover-fine:border-ink-2 flex w-full items-center border text-left",
        )}
      >
        <span className="min-w-0 flex-1">
          <span className="text-lead block leading-tight font-bold text-balance">
            {sentence ?? page.sentence}
          </span>
          <span className="pt-sp-0 text-meta text-mute block">
            {medianGame ? "Game wins and median wins both count. Tap for all." : "Tap for all."}
          </span>
        </span>
        <ChevronRight aria-hidden className="text-mute size-5 flex-none" />
      </SheetTrigger>
      <SheetBackdrop />
      <SheetContent className="max-w-sheet rounded-t-report border-rule bg-card shadow-sheet mx-auto flex max-h-[88dvh] w-full flex-col border border-b-0">
        <SheetGrip className="mt-sp-2 h-sp-1 w-sp-6" />
        <div className="gap-sp-2 px-sp-4 pt-sp-3 flex flex-none items-start justify-between">
          <div className="min-w-0">
            <SheetTitle className="text-stat m-0 leading-tight font-bold text-balance">
              Wins left and your odds
            </SheetTitle>
            <p className="pt-sp-1 text-meta text-mute m-0 text-pretty">{`${perWeek} ${page.wins_left} are left.`}</p>
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
        <div aria-hidden className={cn(ROW, "px-sp-4 pt-sp-3 pb-sp-1 min-h-0")}>
          <span className={cn(LABEL, "text-mute")}>Wins</span>
          <span className={cn(LABEL, "text-mute")}>Playoff odds</span>
          <span />
          <span className={cn(LABEL, "text-mute text-right")}>Likely</span>
        </div>
        <ol className="px-sp-4 m-0 min-h-0 list-none overflow-y-auto overscroll-contain pb-[calc(var(--spacing-sp-4)+env(safe-area-inset-bottom))]">
          {[...page.ladder].reverse().map((step) => {
            const inZone = page.need !== null && step.more_wins >= page.need;
            return (
              <li key={step.more_wins}>
                <span className={cn(ROW, step.chance === 0 && "opacity-50")}>
                  <span
                    className={cn("text-body font-bold tabular-nums", inZone && "text-accent-ink")}
                  >
                    {`${step.more_wins} of ${page.wins_left}`}
                  </span>
                  <Bar value={step.playoff} />
                  <span className="text-body text-right font-bold tabular-nums">
                    {oddsText(step.playoff, step.about)}
                  </span>
                  <span className="text-meta text-mute text-right tabular-nums">{`${step.chance}%`}</span>
                </span>
                {step.more_wins === page.need && (
                  <span className="gap-sp-2 py-sp-1 flex items-center">
                    <span className={cn(LABEL, "text-accent-ink flex-none")}>
                      90% odds or more above
                    </span>
                    <span aria-hidden className="bg-accent h-px flex-1" />
                  </span>
                )}
              </li>
            );
          })}
        </ol>
      </SheetContent>
    </Sheet>
  );
}
