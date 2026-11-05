/**
 * The chosen week of the power rankings page, shared by the masthead week line and the rankings table.
 * The URL hash carries the week as "#week-5", so a link opens that week. The state is client state, so this file is a client component.
 */
"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { WeekLine } from "@cpc/design/parts/week-line";
import type { RankingsWeek } from "../schema/rankings-types";

export type WeekChoice = { week: RankingsWeek; choose: (week: number) => void };

const HASH = /^#week-(\d+)$/;

/* The week that the hash names, or null when the hash names no week in the file. */
function weekFromHash(weeks: RankingsWeek[]): number | null {
  const match = HASH.exec(window.location.hash);
  if (!match) return null;
  const week = Number(match[1]);
  return weeks.some((entry) => entry.week === week) ? week : null;
}

/* The chosen week starts as the last week, so the static HTML shows the latest rankings.
   After hydration, a valid hash picks its week. The export is static, so the hook reads window.location and not next/navigation. */
export function useWeekChoice(weeks: RankingsWeek[]): WeekChoice {
  const last = weeks.at(-1)!;
  const [chosen, setChosen] = useState(last.week);

  useEffect(() => {
    const week = weekFromHash(weeks);
    if (week !== null) setChosen(week);
  }, [weeks]);

  function choose(week: number) {
    setChosen(week);
    // replaceState sets the hash with no scroll jump and no new history entry for each chip tap.
    window.history.replaceState(null, "", `#week-${week}`);
  }

  return { week: weeks.find((entry) => entry.week === chosen) ?? last, choose };
}

const WeekChoiceContext = createContext<WeekChoice | null>(null);

/* The shared choice of the page. The masthead is a server component, so it sits inside as a child and keeps its build-time reads. */
export function WeekChoiceProvider({ weeks, children }: { weeks: RankingsWeek[]; children: ReactNode }) {
  const choice = useWeekChoice(weeks);
  return <WeekChoiceContext.Provider value={choice}>{children}</WeekChoiceContext.Provider>;
}

/* The shared choice, or null outside the provider. A table outside the provider keeps a choice of its own. */
export function useSharedWeekChoice(): WeekChoice | null {
  return useContext(WeekChoiceContext);
}

/* The masthead week line of the chosen week. */
export function ChosenWeekLine() {
  const choice = useSharedWeekChoice();
  return choice && <WeekLine label="WEEK" number={choice.week.week} />;
}
