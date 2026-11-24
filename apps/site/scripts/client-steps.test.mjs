/**
 * Tests of the steps that the full check runs for each client folder.
 * A client with the finder on gets a second build against the local API, then the grade-bar project.
 */
import { describe, expect, it } from "bun:test";
import { BUILD_NOW, stepsOfClient } from "./client-steps.mjs";

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
    expect(firstBuild.env).toEqual({ BUILD_NOW });
    expect(secondBuild.env).toEqual({ BUILD_NOW, NEXT_PUBLIC_API_URL: "http://localhost:8080" });
  });

  it("sets the build clock to a time before the CPC Lock on each build step", () => {
    const builds = stepsOfClient("cpc").filter((step) => step.script === "build");
    expect(builds.length).toBe(2);
    for (const build of builds) {
      expect(Date.parse(build.env.BUILD_NOW)).toBeLessThan(Date.parse("2026-11-24T00:00:00-05:00"));
    }
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
    expect(steps[3].env).toEqual({ BUILD_NOW, NEXT_PUBLIC_API_URL: "http://localhost:8080" });
  });
});
