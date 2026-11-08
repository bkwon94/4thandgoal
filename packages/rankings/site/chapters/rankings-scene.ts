/**
 * The data of the rankings scene of the hero: one light per team in the order of the power rank, each at the height of
 * its playoff odds, with the rank-1 team as the flare and its label at rest (decision 07).
 */
import type { HeroScene, SceneLight } from "@cpc/design/parts/scene-math";
import type { Odds, RankingsRow, RankingsWeek } from "../schema/rankings-types";

/* The height of a light: the playoff percent while the race is open, 100 for a clinched team, 0 for a team that is out. */
function heightOf(odds: Odds): number {
  if (odds.status === "in") return 100;
  if (odds.status === "out") return 0;
  return odds.playoff;
}

/* The odds as text, read the same on the Ladder and in a label: "97%", or "In" and "Out" once the race is over for the team. */
export function oddsText(odds: Odds): string {
  if (odds.status === "in") return "In";
  if (odds.status === "out") return "Out";
  return `${odds.playoff}%`;
}

/* A type guard, so the rows that pass the filter carry their odds in the type. */
function hasOdds(row: RankingsRow): row is RankingsRow & { odds: Odds } {
  return row.odds !== undefined;
}

/*
 * The scene of one week of the rankings file. The rows are in rank order, so rank 1 sits on the left. A week from
 * before the odds engine ran has no odds, so it gets no scene and the hero keeps its static grid.
 */
export function rankingsScene(week: RankingsWeek): HeroScene | undefined {
  const rows = week.rows.filter(hasOdds);
  if (rows.length < week.rows.length) return undefined;
  const lights: SceneLight[] = rows.map((row, index) => ({
    x: index,
    y: heightOf(row.odds),
    label: `${row.name} · ${oddsText(row.odds)}`,
    tone: index === 0 ? "flare" : "bright",
  }));
  return { lights, guides: [], margin: null, restIndex: 0, mode: "settle" };
}
