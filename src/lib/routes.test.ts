/**
 * Unit test of the route builders. It checks each path with and without a base path.
 * A builder is the only place that joins the base path to a route.
 */
import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe("routes", () => {
  it("builds every route with no base path", async () => {
    const routes = await import("./routes");
    expect(routes.homeHref()).toBe("/");
    expect(routes.rankingsHref()).toBe("/rankings/");
    expect(routes.analyzeHref()).toBe("/analyze/");
    expect(routes.weekHref("2026", "week-06")).toBe("/2026/week-06/");
    expect(routes.waiverHref("2026", "week-06")).toBe("/2026/week-06/waiver/");
    expect(routes.managersHref("2026")).toBe("/2026/managers/");
    expect(routes.managerHref("2026", 7)).toBe("/2026/managers/7/");
  });

  it("puts the base path in front of every route", async () => {
    vi.stubEnv("NEXT_PUBLIC_BASE_PATH", "/site");
    const routes = await import("./routes");
    expect(routes.homeHref()).toBe("/site/");
    expect(routes.rankingsHref()).toBe("/site/rankings/");
    expect(routes.analyzeHref()).toBe("/site/analyze/");
    expect(routes.weekHref("2026", "week-06")).toBe("/site/2026/week-06/");
    expect(routes.waiverHref("2026", "week-06")).toBe("/site/2026/week-06/waiver/");
    expect(routes.managersHref("2026")).toBe("/site/2026/managers/");
    expect(routes.managerHref("2026", 7)).toBe("/site/2026/managers/7/");
  });
});
