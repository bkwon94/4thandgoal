/**
 * Tests for the data of the analyzer scenes: the two groups of the verdict hero.
 * The verdict scenes come from real answers of the API, among them the recorded answer to grade-clarity trade A.
 */
import { describe, expect, it } from "vitest";
import { analyzeResponse, analyzeResponseThree, analyzeResponseTradeA } from "../lib/fixtures/api";
import { type SceneLight, sceneLines } from "@cpc/design/parts/scene-math";
import { verdictScene } from "./analyzer-scene";

/* The lights of each side, by the team name at the start of each label. */
function groupsOf(lights: SceneLight[], teams: string[]): SceneLight[][] {
  return teams.map((team) => lights.filter((light) => light.label === team || light.label.startsWith(`${team} · `)));
}

describe("verdictScene", () => {
  const scene = verdictScene(analyzeResponseTradeA);
  const [lamb, girds] = groupsOf(scene.lights, ["behold the lamb", "Bo Girds"]);

  it("settles into two groups, one per side of trade A, with each light in one group", () => {
    expect(scene.mode).toBe("settle");
    expect(lamb.length + girds.length).toBe(scene.lights.length);
    // The groups sit apart: each light of behold the lamb is left of each light of Bo Girds.
    expect(Math.max(...lamb.map((light) => light.x))).toBeLessThan(Math.min(...girds.map((light) => light.x)));
  });

  it("joins no light of behold the lamb to a light of Bo Girds, so the scene reads as two groups (AT-21)", () => {
    expect(lamb.every((light) => light.group === lamb[0].group)).toBe(true);
    expect(girds.every((light) => light.group === girds[0].group)).toBe(true);
    expect(lamb[0].group).not.toBe(girds[0].group);
    for (const [a, b] of sceneLines(scene.lights)) expect(scene.lights[a].group).toBe(scene.lights[b].group);
  });

  it("keeps a clear gap between the groups, wider than a group", () => {
    const lambXs = lamb.map((light) => light.x);
    const girdsXs = girds.map((light) => light.x);
    const width = Math.max(...lambXs) - Math.min(...lambXs);
    expect(Math.min(...girdsXs) - Math.max(...lambXs)).toBeGreaterThan(width);
  });

  it("puts the bigger group on the side of behold the lamb, the side that gets more (AT-21)", () => {
    expect(lamb.length).toBeGreaterThan(girds.length);
  });

  it("flares the side that gets more and no light of the side that gives more", () => {
    expect(lamb.every((light) => light.tone === "flare")).toBe(true);
    expect(girds.some((light) => light.tone === "flare")).toBe(false);
  });

  it("names a factor that leans for the side in the label of each light past the team light", () => {
    expect(lamb.map((light) => light.label)).toEqual([
      "behold the lamb",
      "behold the lamb · deal",
      "behold the lamb · roster fit",
      "behold the lamb · standing",
      "behold the lamb · schedule",
    ]);
    expect(girds.map((light) => light.label)).toEqual(["Bo Girds"]);
  });

  it("shows no label at rest, no guide, and no margin mark", () => {
    expect(scene.restIndex).toBeNull();
    expect(scene.guides).toEqual([]);
    expect(scene.margin).toBeNull();
  });

  it("flares no side of a fair trade", () => {
    expect(verdictScene(analyzeResponse).lights.some((light) => light.tone === "flare")).toBe(false);
  });

  it("flares no side of a document with no fairness block", () => {
    expect(verdictScene({ ...analyzeResponseTradeA, fairness: undefined }).lights.some((light) => light.tone === "flare")).toBe(false);
  });

  it("gives a trade of three sides three groups, in the order of the trade", () => {
    const three = verdictScene(analyzeResponseThree);
    const teams = analyzeResponseThree.trade.sides.map((side) => side.team);
    const groups = groupsOf(three.lights, teams);
    expect(groups.every((group) => group.length > 0)).toBe(true);
    expect(groups.flat()).toHaveLength(three.lights.length);
    const centers = groups.map((group) => group[0].x);
    expect(centers).toEqual([...centers].sort((a, b) => a - b));
  });
});
