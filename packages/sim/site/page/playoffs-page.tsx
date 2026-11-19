/**
 * The Playoffs page of the sim page before the playoffs start: the odds of Your team to make the playoffs, to get a bye,
 * and to win the title, then each week left with its opponent, which opens that week.
 */
"use client";

import { ChevronRight } from "lucide-react";
import { useId } from "react";
import { cn } from "@cpc/design/lib/utils";
import type { WeekSim } from "../schema/sim-types";
import { CARD, PRESS, nameOf, oddsText } from "./format";

export function PlayoffsPage({ sim, you, onOpen }: { sim: WeekSim; you: number; onOpen: (week: number) => void }) {
  const page = sim.pages[you];
  const team = sim.teams[you];
  const odds = useId();
  const weeks = useId();
  // The title odds have one decimal in the file. The page shows whole percent, as the other odds.
  const stats = [
    { label: "Make the playoffs", value: page.playoff },
    { label: "Get a bye", value: Math.round(team.bye) },
    { label: "Win the title", value: Math.round(team.title) },
  ];
  return (
    <div className="grid w-full grid-cols-1 items-start gap-sp-3 desktop:grid-cols-2">
      <article className={CARD} aria-labelledby={odds}>
        <h2 id={odds} className="m-0 text-lead leading-tight font-bold">Your playoff odds</h2>
        <dl className="m-0 grid grid-cols-3 gap-sp-2">
          {stats.map((stat) => (
            <div key={stat.label} className="flex min-w-0 flex-col-reverse justify-end gap-sp-1 rounded-report bg-page p-sp-3">
              <dt className="text-meta leading-tight text-pretty text-mute">{stat.label}</dt>
              <dd className="m-0 font-mono text-stat leading-none font-bold tabular-nums">{oddsText(stat.value)}</dd>
            </div>
          ))}
        </dl>
      </article>
      <article className={CARD} aria-labelledby={weeks}>
        <h2 id={weeks} className="m-0 text-lead leading-tight font-bold">Your weeks left</h2>
        <ul className="m-0 list-none p-0">
          {page.weeks.map((week) => (
            <li key={week.week} className="border-t border-rule first:border-t-0">
              <button
                type="button"
                onClick={() => onOpen(week.week)}
                className={cn(PRESS, "flex min-h-touch w-full items-center gap-sp-2 py-sp-1 text-left hover-fine:text-accent-ink")}
              >
                <span className="flex-none text-body font-bold tabular-nums">{`Week ${week.week}`}</span>
                <span className="min-w-0 flex-1 text-meta text-pretty text-mute">{`vs ${nameOf(sim, week.opponent)}`}</span>
                <ChevronRight aria-hidden className="size-4 flex-none text-mute" />
              </button>
            </li>
          ))}
        </ul>
      </article>
    </div>
  );
}
