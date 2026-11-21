/**
 * Tests of the steps that the full check runs for each client folder.
 * A client with the finder on gets a second build against the local API, then the grade-bar project.
 */
// @vitest-environment node
import { describe, expect, it } from "vitest";
import { stepsOfClient } from "./client-steps.mjs";

describe("the steps of a client", () => {
  it("runs the floor on the normal build, then the grade-bar project on a second build, for norcal", () => {
    const scripts = stepsOfClient("norcal").map((step) => step.script);
    expect(scripts).toEqual([
      "build",
      "check:export",
      "check:floor",
      "build",
      "check:grade-bar-export",
    ]);
  });

  it("builds norcal against the local API for the second build only", () => {
    const [firstBuild, , , secondBuild] = stepsOfClient("norcal");
    expect(firstBuild.env).toBeUndefined();
    expect(secondBuild.env).toEqual({ NEXT_PUBLIC_API_URL: "http://localhost:8080" });
  });

  it("runs the grade-bar project on a second build for cpc, the client with the finder on", () => {
    const steps = stepsOfClient("cpc");
    expect(steps.map((step) => step.script)).toEqual([
      "build",
      "check:export",
      "check:floor",
      "build",
      "check:grade-bar-export",
    ]);
    expect(steps[3].env).toEqual({ NEXT_PUBLIC_API_URL: "http://localhost:8080" });
  });
});
