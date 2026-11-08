/**
 * The four numbers under the hero of the week page: the top score, the median, the closest margin, and the Game Changer gap.
 * Each number is a tile, so the week reads at a glance before the games.
 */
import { gap, num } from "@cpc/design/format/format";
import { Rise } from "@cpc/design/parts/rise";
import { Tile, type TileTrend, type TrendPoint } from "@cpc/design/parts/tile";
import type { GameChanger, Matchup, Median } from "../schema/week-types";
import { stableId } from "@cpc/design/lib/stable-id";
import { medianOf, trendText, type WeekTrends } from "./week-trends";

/* A name suffix is no surname, so "Harold Fannin Jr." gives "Fannin". */
const SUFFIXES = new Set(["Jr.", "Sr.", "II", "III", "IV", "V"]);

/* The surname of a player: the last word of the name that is no suffix. */
function surname(name: string): string {
  const words = name.trim().split(/\s+/);
  return [...words].reverse().find((word) => !SUFFIXES.has(word)) ?? name;
}

type WeekNumber = { label: string; value: string; note: string; trend?: TileTrend };

/* The trend of one tile, from week 1 to the page week, with one sentence of it. */
function trendOf(points: TrendPoint[], week: number, kind: TileTrend["kind"]): TileTrend {
  return { points, week, kind, text: trendText(points, week) };
}

/* The numbers of the week, in the order of the page. A week with no Game Changer, or one with no projection, has three.
   With the trends of the season, Top Score and Median are Trend tiles. Closest and Game Changer stay plain, because
   the managers file has no pairs and no projections to give them a series. */
function numbersOf(
  matchups: Matchup[],
  median: Median | null,
  gameChanger: GameChanger | null,
  trends: WeekTrends | null,
): WeekNumber[] {
  const sides = matchups.flatMap((matchup) => matchup.sides);
  const top = sides.reduce((best, side) => (side.score > best.score ? side : best), sides[0]);
  const scores = sides.map((side) => side.score);
  const line = median?.value ?? medianOf(scores);
  const above = scores.filter((score) => score > line).length;
  const below = scores.filter((score) => score < line).length;
  // The JSON puts the winner first, so the margin of a game is the first score less the second.
  const margin = (matchup: Matchup) => matchup.sides[0].score - matchup.sides[1].score;
  const closest = matchups.reduce((best, matchup) => (margin(matchup) < margin(best) ? matchup : best), matchups[0]);
  const numbers: WeekNumber[] = [
    {
      label: "Top Score",
      value: num(top.score),
      note: top.team.name,
      ...(trends && { trend: trendOf(trends.top, trends.week, "bars") }),
    },
    {
      label: "Median",
      value: num(line),
      note: `${above} above, ${below} below`,
      ...(trends && { trend: trendOf(trends.median, trends.week, "step") }),
    },
    {
      label: "Closest",
      value: num(margin(closest)),
      note: `${closest.sides[0].team.name} over ${closest.sides[1].team.name}`,
    },
  ];
  const changer = gameChanger?.award.line;
  if (changer && changer.projection !== null) {
    numbers.push({
      label: "Game Changer",
      value: gap(changer.points - changer.projection),
      note: `${surname(changer.name)} over projection`,
    });
  }
  return numbers;
}

export function WeekNumbers({
  matchups,
  median,
  gameChanger,
  trends = null,
}: {
  matchups: Matchup[];
  median: Median | null;
  gameChanger: GameChanger | null;
  // The series of the season from the managers file. A page with no managers file has plain tiles.
  trends?: WeekTrends | null;
}) {
  if (matchups.length === 0) return null;
  return (
    <section aria-label="The week in numbers">
      {/* Two tiles per row on a phone and four from the tablet tier, so the four numbers fill one row there. */}
      <ul className="m-0 grid list-none grid-cols-2 gap-sp-2 p-0 tablet:grid-cols-4">
        {numbersOf(matchups, median, gameChanger, trends).map((item, index) => (
          // The hero takes the first four steps of the stagger, so the tiles rise after it.
          <li key={item.label} className="min-w-0" {...stableId("number", item.label)}>
            <Rise step={index + 4} className="h-full">
              <Tile label={item.label} value={item.value} note={item.note} trend={item.trend} className="h-full" />
            </Rise>
          </li>
        ))}
      </ul>
    </section>
  );
}
