/**
 * The data of the analyzer scenes: a drift of lights in the title hero, and one group of lights per side in the verdict hero.
 * The verdict scene comes from the answer of the API, so the bigger group sits on the side that gets more (decision 07).
 */
import type { HeroScene, SceneLight } from "@cpc/design/parts/scene-math";
import type { AnalyzeResponse } from "../lib/analyze-types";

/* The count of the lights of the drift. A drift places each light itself, so only the count and the tones count. */
const DRIFT_LIGHTS = 12;

/*
 * The scene of the title hero before a grade: lights that drift and never settle (story 25).
 * One plain object for every render, so a render of the form never restarts the drift.
 */
export const driftScene: HeroScene = {
  lights: Array.from({ length: DRIFT_LIGHTS }, (_, index) => ({
    x: index,
    y: 0,
    label: "",
    tone: index % 3 === 0 ? "bright" : "dim",
  })),
  guides: [],
  margin: null,
  restIndex: null,
  mode: "drift",
};

/* The space between the centers of two groups, in the units of the scene. Each group has a radius of one. */
const GROUP_GAP = 4;

/*
 * The scene of the verdict hero: one group per side of the trade, in the order of the trade (story 26).
 * A group holds the light of the team and one light for each factor that leans for that side. A side that gets more
 * has more factors for it, so its group is bigger. A lopsided trade flares each side but the one that gives more. A
 * fair or a good-for-both trade, or a document with no fairness block, has no side that gets more, so it has no flare.
 */
export function verdictScene(doc: AnalyzeResponse): HeroScene {
  const { fairness } = doc;
  const lights = doc.trade.sides.flatMap((side, index): SceneLight[] => {
    const factors = doc.sides.find((decided) => decided.roster_id === side.roster_id)?.factors ?? [];
    const leans = factors.filter((factor) => factor.lean === "for");
    const getsMore = fairness?.state === "lopsided" && side.roster_id !== fairness.gives_more;
    const center = { x: index * GROUP_GAP, y: 0 };
    // The factor lights sit on a ring around the team light, from the top and clockwise.
    const ring = leans.map((factor, step) => {
      const angle = -Math.PI / 2 + (2 * Math.PI * step) / leans.length;
      return { x: center.x + Math.cos(angle), y: center.y + Math.sin(angle), label: `${side.team} · ${factor.name}` };
    });
    return [
      { ...center, label: side.team, tone: getsMore ? "flare" : "bright" },
      ...ring.map((light) => ({ ...light, tone: getsMore ? ("flare" as const) : ("dim" as const) })),
    ];
  });
  return { lights, guides: [], margin: null, restIndex: null, mode: "settle" };
}
