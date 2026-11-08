/**
 * The two week series of the Trend tiles of the week numbers: the top score and the median of each week.
 * Each series runs from week 1 to the page week, from the saved weeks of every team, so an older page shows no later week.
 */
import { num } from "@cpc/design/format/format";
import type { TrendPoint } from "@cpc/design/parts/tile";

/* One saved week of one team, as the managers file holds it. The median is null for a league with no median game. */
export type TeamWeek = { week: number; points: number; median: number | null };

/* The page week and its two series. */
export type WeekTrends = { week: number; top: TrendPoint[]; median: TrendPoint[] };

/* The median of the scores of the week, in whole cents first, so an even count rounds its middle pair the same way
   each time: 100.31 and 98.88 give 99.6. A league with a median game has it in the JSON, and the page reads that. */
export function medianOf(scores: number[]): number {
  const cents = scores.map((score) => Math.round(score * 100)).sort((a, b) => a - b);
  const middle = Math.floor(cents.length / 2);
  const value = cents.length % 2 === 1 ? cents[middle] : Math.round((cents[middle - 1] + cents[middle]) / 2);
  return value / 100;
}

/* The top score and the median of each week from week 1 to the page week. The median is the published median of
   the week, or else the median of the points of every team, so the point of the page week equals the number on its tile.
   A week that no team saved has no point. */
export function weekTrends(teams: TeamWeek[][], pageWeek: number): WeekTrends {
  const top: TrendPoint[] = [];
  const median: TrendPoint[] = [];
  for (let week = 1; week <= pageWeek; week++) {
    const saved = teams.flatMap((weeks) => weeks.filter((item) => item.week === week));
    if (saved.length === 0) continue;
    const points = saved.map((item) => item.points);
    const published = saved.find((item) => item.median !== null)?.median ?? null;
    top.push({ week, value: Math.max(...points) });
    median.push({ week, value: published ?? medianOf(points) });
  }
  return { week: pageWeek, top, median };
}

/* One sentence of a trend at the page week, the text alternative of a Trend tile. A high or a low of the season so far
   is the news, so it comes first. Else the sentence compares the page week to the week before it. */
export function trendText(points: TrendPoint[], week: number): string {
  const season = points.filter((point) => point.week <= week);
  const current = season.at(-1);
  const prior = season.at(-2);
  if (!current || !prior) return "The first week of the season.";
  const values = season.map((point) => point.value);
  if (current.value === Math.max(...values) && current.value > prior.value) return "The highest of the season so far.";
  if (current.value === Math.min(...values) && current.value < prior.value) return "The lowest of the season so far.";
  if (current.value === prior.value) return `Level with week ${prior.week}.`;
  const way = current.value > prior.value ? "Up" : "Down";
  return `${way} from ${num(prior.value)} in week ${prior.week}.`;
}
