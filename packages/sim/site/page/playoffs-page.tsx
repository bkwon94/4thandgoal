/**
 * The Playoffs page of the sim page before the playoffs start: the odds of Your team to make the playoffs, to get a bye, and to win
 * the title, from the What-if answer when one is set and from the file otherwise, then each week left, which opens that week.
 */
"use client";

import { Button } from "@cpc/design/ui/button";
import { ChevronRight } from "lucide-react";
import { useId } from "react";
import { cn } from "@cpc/design/lib/utils";
import type { SimPage, TeamSim, WeekSim } from "../schema/sim-types";
import { CARD, PRESS, nameOf, oddsText } from "./format";
import { SoftText } from "./parts";

/* `page` and `team` are the page block and the team odds that the page shows: those of the What-if answer, or the file. */
export function PlayoffsPage({
  sim,
  page,
  team,
  onOpen,
}: {
  sim: WeekSim;
  page: SimPage;
  team: TeamSim;
  onOpen: (week: number) => void;
}) {
  const odds = useId();
  const weeks = useId();
  // The title odds have one decimal in the file. The page shows whole percent, as the other odds.
  const stats = [
    { label: "Make the playoffs", value: page.playoff },
    { label: "Get a bye", value: Math.round(team.bye) },
    { label: "Win the title", value: Math.round(team.title) },
  ];
  return (
    <div className="gap-sp-3 desktop:grid-cols-2 grid w-full grid-cols-1 items-start">
      <article className={CARD} aria-labelledby={odds}>
        <h2 id={odds} className="text-lead m-0 leading-tight font-bold">
          Your playoff odds
        </h2>
        <dl className="gap-sp-2 m-0 grid grid-cols-3">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="gap-sp-1 rounded-report bg-page p-sp-3 flex min-w-0 flex-col-reverse justify-end"
            >
              <dt className="text-meta text-mute leading-tight text-pretty">{stat.label}</dt>
              <dd className="text-stat m-0 font-mono leading-none font-bold tabular-nums">
                <SoftText text={oddsText(stat.value)} />
              </dd>
            </div>
          ))}
        </dl>
      </article>
      <article className={CARD} aria-labelledby={weeks}>
        <h2 id={weeks} className="text-lead m-0 leading-tight font-bold">
          Your weeks left
        </h2>
        <ul className="m-0 list-none p-0">
          {page.weeks.map((week) => (
            <li key={week.week} className="border-rule border-t first:border-t-0">
              <Button
                variant="plain"
                type="button"
                onClick={() => onOpen(week.week)}
                className={cn(
                  PRESS,
                  "min-h-touch gap-sp-2 py-sp-1 hover-fine:text-accent-ink flex w-full items-center text-left",
                )}
              >
                <span className="text-body flex-none font-bold tabular-nums">{`Week ${week.week}`}</span>
                <span className="text-meta text-mute min-w-0 flex-1 text-pretty">{`vs ${nameOf(sim, week.opponent)}`}</span>
                <ChevronRight aria-hidden className="text-mute size-4 flex-none" />
              </Button>
            </li>
          ))}
        </ul>
      </article>
    </div>
  );
}
