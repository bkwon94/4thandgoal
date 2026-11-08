/**
 * The data of the midseason scene of the opener and of the takeover: one light per team at its season total points,
 * in the order of the standings, with the leader as the flare and its label at rest (decision 07).
 */
import type { HeroScene, SceneLight } from "@cpc/design/parts/scene-math";
import type { Midseason, StateChapter } from "../schema/midseason-types";

/*
 * The scene of the report from its state chapter, which holds the teams in standings order. The leader sits on the
 * left. A report with no state chapter has no standings, so it gets no scene and the hero keeps its static grid.
 */
export function midseasonScene(report: Midseason): HeroScene | undefined {
  const state = report.acts
    .flatMap((act) => act.chapters)
    .find((chapter): chapter is StateChapter => chapter.key === "state");
  if (!state || state.facts.teams.length === 0) return undefined;
  const lights: SceneLight[] = state.facts.teams.map((team, index) => ({
    x: index,
    y: team.points_for,
    // Two decimals on every total, as "850.17", so the labels of the scene read as a set.
    label: `${team.name} · ${team.points_for.toFixed(2)}`,
    tone: index === 0 ? "flare" : "bright",
  }));
  return { lights, guides: [], margin: null, restIndex: 0, mode: "settle" };
}
