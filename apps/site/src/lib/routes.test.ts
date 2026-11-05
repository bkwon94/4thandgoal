/**
 * Unit test of the route builders. Each row checks one builder.
 * The app layer calls the builders to make every href.
 */
import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

type Routes = typeof import("./routes");

const builders: [string, (routes: Routes) => string, string][] = [
  ["homeHref", (r) => r.homeHref(), "/"],
  ["rankingsHref", (r) => r.rankingsHref(), "/rankings/"],
  ["analyzeHref", (r) => r.analyzeHref(), "/analyze/"],
  ["weekHref", (r) => r.weekHref("2026", "week-06"), "/2026/week-06/"],
  ["waiverHref", (r) => r.waiverHref("2026", "week-06"), "/2026/week-06/waiver/"],
  ["managersHref", (r) => r.managersHref("2026"), "/2026/managers/"],
  ["managerHref", (r) => r.managerHref("2026", 7), "/2026/managers/7/"],
  ["managerHrefFrom", (r) => r.managerHrefFrom(r.managersHref("2026"), 7), "/2026/managers/7/"],
];

describe("routes", () => {
  it.each(builders)("%s builds its route from the root", async (_name, call, route) => {
    expect(call(await import("./routes"))).toBe(route);
  });
});
