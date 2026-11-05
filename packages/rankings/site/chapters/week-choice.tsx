/**
 * The chosen week of the power rankings page, which the hero and the cards of the Ladder read.
 * The URL hash carries the week as "#week-5", so a link opens that week. The state is client state, so this file is a client component.
 */
"use client";

import { useEffect, useState } from "react";
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
