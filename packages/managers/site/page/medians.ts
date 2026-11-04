/**
 * The median of each week of a manager entry, for the points line and the record against the median.
 * The module is no client module, so the server chapter and the client chart both call it.
 */
import type { SeasonWeek } from "../schema/manager-types";

/* The median of each week, or null for a league with no median game. The pipeline writes a median for every week or for none. */
export function mediansOf(weeks: SeasonWeek[]): number[] | null {
  const medians = weeks.map((week) => week.median);
  return medians.every((median): median is number => median !== null) ? medians : null;
}
