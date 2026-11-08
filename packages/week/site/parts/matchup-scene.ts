/**
 * The data of the Matchup scene of the hero: one light per team at its points of the week, the league median, and
 * the two teams of the Matchup of the Week as the flare with the margin mark between them (decision 07).
 */
import { gap } from "@cpc/design/format/format";
import type { HeroScene, SceneLight } from "@cpc/design/parts/scene-math";
import type { Matchup, Median, Pick } from "../schema/week-types";

/* Two decimals on every score, as "99.60", so the labels of the scene line up as a set. */
function points(score: number): string {
  return score.toFixed(2);
}

/*
 * The scene of the week from the parts of the week page that the hero already loads. The lights run from the low
 * score to the high score. The winner of the Matchup shows its label at rest, and the margin runs from it to the loser.
 */
export function matchupScene(week: { matchups: Matchup[]; median: Median | null; pick: Pick }): HeroScene {
  const [first, second] = week.pick.sides;
  // A tie has no winner, so the first side of the pick stands in as the winner.
  const [winner, loser] = second.winner ? [second, first] : [first, second];
  const pickIds = new Set([winner.team.roster_id, loser.team.roster_id]);

  const sides = week.matchups.flatMap((matchup) => matchup.sides).sort((a, b) => a.score - b.score);
  const lights: SceneLight[] = sides.map((side, index) => ({
    x: index,
    y: side.score,
    label: `${side.team.name} · ${points(side.score)}`,
    tone: pickIds.has(side.team.roster_id) ? "flare" : "bright",
  }));
  const indexOf = (rosterId: number) => sides.findIndex((side) => side.team.roster_id === rosterId);
  const winnerIndex = indexOf(winner.team.roster_id);

  // A league with no median game publishes no median, so its scene has no guide.
  const median = week.median?.value;
  const guides =
    median === undefined
      ? []
      : [
          {
            label: `MEDIAN ${points(median)}`,
            points: [
              { x: 0, y: median },
              { x: lights.length - 1, y: median },
            ],
          },
        ];

  return {
    lights,
    guides,
    margin: { from: winnerIndex, to: indexOf(loser.team.roster_id), text: gap(winner.score - loser.score) },
    restIndex: winnerIndex,
    mode: "settle",
  };
}
