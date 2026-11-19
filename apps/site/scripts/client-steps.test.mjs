/**
 * Tests of the steps that the full check runs for each client folder.
 * A client with the finder on gets the grade-bar project on an export built against the local API.
 */
// @vitest-environment node
import { describe, expect, it } from "vitest";
import { stepsOfClient } from "./client-steps.mjs";

describe("the steps of a client", () => {
  it("runs the grade-bar project for norcal, the client with the finder on", () => {
    const scripts = stepsOfClient("norcal").map((step) => step.script);
    expect(scripts).toEqual(["build", "check:export", "check:floor", "check:grade-bar-export"]);
  });

  it("builds the export of norcal against the local API", () => {
    const [build] = stepsOfClient("norcal");
    expect(build.env).toEqual({ NEXT_PUBLIC_API_URL: "http://localhost:8080" });
  });

  it("runs no grade-bar project for cpc, the client with the finder off", () => {
    const steps = stepsOfClient("cpc");
    expect(steps.map((step) => step.script)).toEqual(["build", "check:export", "check:floor"]);
    expect(steps.every((step) => !step.env)).toBe(true);
  });
});
