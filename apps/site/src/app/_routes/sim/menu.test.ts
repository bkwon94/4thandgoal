/**
 * Tests for the menu link of the sim package and the read of the latest week sim file. Each test builds a temp public/
 * folder from the real week pages, with the real CPC week 10 sim file in the given week folders.
 */
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import weekSimJson from "@cpc/sim/fixtures/week-sim.json";
import { publicOver, removePublics } from "../midseason/temp-public";

afterEach(removePublics);

/* A temp public/ with the weeks up to `latest`, and the week sim file in each week of `simWeeks`. */
function publicWithSims(latest: number, simWeeks: number[]) {
  publicOver({ latest });
  for (const week of simWeeks) {
    const folder = join(process.cwd(), "public", "2026", `week-${String(week).padStart(2, "0")}`);
    writeFileSync(join(folder, "sim.json"), JSON.stringify({ ...weekSimJson, week }));
  }
}

describe("the menu link of the sim package", () => {
  it("links the sim page of the season of the latest week", async () => {
    publicWithSims(10, [10]);
    expect((await import("./menu")).menuLink()).toEqual({ label: "Season Sim", href: "/sim/2026/" });
  });

  it("gives no link when no week of the season has a sim file", async () => {
    publicWithSims(10, []);
    expect((await import("./menu")).menuLink()).toBeNull();
  });
});

describe("the latest week sim file", () => {
  it("reads the newest week folder that holds a sim file", async () => {
    publicWithSims(10, [9, 10]);
    const { latestWeekSim, weekSimSeasons } = await import("@/lib/data/sim-data");
    expect(weekSimSeasons()).toEqual(["2026"]);
    expect(latestWeekSim("2026")?.week).toBe(10);
  });

  it("gives null for a season with no week sim file", async () => {
    publicWithSims(10, []);
    const { latestWeekSim, weekSimSeasons } = await import("@/lib/data/sim-data");
    expect(weekSimSeasons()).toEqual([]);
    expect(latestWeekSim("2026")).toBeNull();
  });
});
