/**
 * The data of the manager scene of the hero: one light per played week at its points, bright for a win and dim for a
 * loss, against the dashed median of each week, with the latest week as the label at rest (decision 07).
 */
import type { HeroScene, SceneGuide, SceneLight } from "@cpc/design/parts/scene-math";
import type { ManagerEntry } from "../schema/manager-types";
import { mediansOf } from "./medians";

/* The result of a week in one letter. A bye or a tie has no result, so it takes a dash, as the week chip does. */
function resultOf(won: boolean | null): string {
  return won === null ? "—" : won ? "W" : "L";
}

/* The scene of one manager from the weeks of its entry in the managers file. */
export function managerScene(manager: Pick<ManagerEntry, "weeks">): HeroScene {
  const { weeks } = manager;
  const lights: SceneLight[] = weeks.map((week) => ({
    x: week.week,
    y: week.points,
    // Two decimals on every score, as "96.10", so the labels of the scene line up as a set.
    label: `Week ${week.week} · ${week.points.toFixed(2)} · ${resultOf(week.won)}`,
    // A week with no result reads as no win, so only a win is bright.
    tone: week.won ? "bright" : "dim",
  }));

  // A league with no median game publishes no median, so its scene has no guide.
  const medians = weeks.length > 0 ? mediansOf(weeks) : null;
  const guides: SceneGuide[] = medians
    ? [{ label: "WEEK MEDIAN", points: weeks.map((week, index) => ({ x: week.week, y: medians[index] })) }]
    : [];

  return {
    lights,
    guides,
    margin: null,
    restIndex: lights.length > 0 ? lights.length - 1 : null,
    mode: "settle",
  };
}
