/**
 * The data of the drift scene: a scatter of lights that never settles into a chart, as on the 404 page (decision 07).
 * It holds no data of the league, so it lives in the design package. The 404 page and the analyzer form use it.
 */
import type { HeroScene, SceneLight } from "./scene-math";

/* The count of lights of the scatter: 12, the count of teams of a scene with data, so the scatter reads as the same sky. */
const DRIFT_LIGHTS = 12;

/*
 * The scene with a fixed scatter. The canvas draws a drift from its own start places, so the x and y values here only
 * give the layout a box to hold. Every third light is dim, so the scatter has depth. No light has a label.
 * It is one constant, so a render never makes a new object, and a render of a hero never restarts the drift.
 */
export const driftScene: HeroScene = {
  lights: Array.from({ length: DRIFT_LIGHTS }, (_, index): SceneLight => ({
    x: index,
    // A fixed zigzag, so the scene is the same on the server and on the client.
    y: (index * 7) % DRIFT_LIGHTS,
    label: "",
    tone: index % 3 === 2 ? "dim" : "bright",
  })),
  guides: [],
  margin: null,
  restIndex: null,
  mode: "drift",
};
