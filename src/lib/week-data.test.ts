/**
 * Tests for the week data loader against the real public/ folder.
 * The week 6 JSON is the fixture, so these tests break if the publish layout changes.
 */
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "./week-page-fixture";
import { listWeeks, listWeekSummaries, loadWeek } from "./week-data";

describe("listWeeks", () => {
  it("lists week 6 of 2026 by its folder names", () => {
    expect(listWeeks()).toContainEqual({ season: "2026", week: "week-06" });
  });
});

describe("loadWeek", () => {
  it("reads the week 6 page JSON", () => {
    const page = loadWeek("2026", "week-06");
    expect(page.week).toBe(6);
    expect(page.season).toBe(2026);
    expect(page.pick.sides[0].team.name).toBe("behold the lamb");
    expect(page.avatars["10"]).toBe("avatars/10.jpg");
  });
});

describe("loadWeek schema check", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("throws when the schema version is not 2", async () => {
    // A temp public/ folder holds a page at the old version.
    const root = mkdtempSync(join(tmpdir(), "week-data-"));
    mkdirSync(join(root, "public", "2026", "week-01"), { recursive: true });
    writeFileSync(join(root, "public", "2026", "week-01", "page.json"), JSON.stringify({ schema_version: 1 }));
    vi.spyOn(process, "cwd").mockReturnValue(root);
    // The module reads the working folder when it loads, so reset it to pick up the temp folder.
    vi.resetModules();
    const { loadWeek: load } = await import("./week-data");
    expect(() => load("2026", "week-01")).toThrow(/schema_version 1/);
  });
});

describe("listWeekSummaries", () => {
  it("summarizes week 6 with its dates and link", () => {
    expect(listWeekSummaries()).toContainEqual({
      number: 6,
      dates: "Oct 15 – Oct 19, 2026",
      href: "/2026/week-06/",
    });
  });

  it("sorts the newest week first", () => {
    const numbers = listWeekSummaries().map((summary) => summary.number);
    expect(numbers).toEqual([...numbers].sort((a, b) => b - a));
  });

  it("sorts by season, then by week, as numbers", async () => {
    // A temp public/ folder holds weeks 2 and 10 of 2026 and week 1 of 2027.
    const root = mkdtempSync(join(tmpdir(), "week-data-"));
    for (const [season, week, number] of [
      ["2026", "week-02", 2],
      ["2026", "week-10", 10],
      ["2027", "week-01", 1],
    ] as const) {
      mkdirSync(join(root, "public", season, week), { recursive: true });
      writeFileSync(
        join(root, "public", season, week, "page.json"),
        weekPageJson({ week: number, dates: "d" }),
      );
    }
    vi.spyOn(process, "cwd").mockReturnValue(root);
    vi.resetModules();
    const { listWeekSummaries: list } = await import("./week-data");
    expect(list().map((summary) => summary.href)).toEqual(["/2027/week-01/", "/2026/week-10/", "/2026/week-02/"]);
  });
});
