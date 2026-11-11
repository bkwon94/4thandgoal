/**
 * Tests for the steps of a trade stream: a live line names the stage at work, and its done line takes its place.
 * A live line with no done line drops when the Answer comes.
 */
import { describe, expect, it } from "vitest";
import { addStep, endSteps, noSteps } from "./trade-api";

describe("the steps of a trade stream", () => {
  it("puts the done line of a stage in the place of its live line", () => {
    let steps = addStep(noSteps, "Checking 11 teams for a fit", true);
    expect(steps.lines).toEqual(["Checking 11 teams for a fit"]);
    steps = addStep(steps, "Checked 11 teams for a fit", false);
    steps = addStep(steps, "Building offers", true);
    expect(steps.lines).toEqual(["Checked 11 teams for a fit", "Building offers"]);
    steps = addStep(steps, "Built 56 offers", false);
    expect(steps.lines).toEqual(["Checked 11 teams for a fit", "Built 56 offers"]);
  });

  it("adds a done line with no live line before it, such as a line of an older API", () => {
    expect(addStep(addStep(noSteps, "Found Kenneth Walker III", false), "Checked 11 teams for a fit", false).lines).toEqual([
      "Found Kenneth Walker III",
      "Checked 11 teams for a fit",
    ]);
  });

  it("drops a live line that got no done line when the Answer comes", () => {
    const steps = addStep(addStep(noSteps, "Weighed 41 offers", false), "Picking the best offers", true);
    expect(endSteps(steps)).toEqual(["Weighed 41 offers"]);
    expect(endSteps(addStep(noSteps, "Weighed 41 offers", false))).toEqual(["Weighed 41 offers"]);
  });
});
