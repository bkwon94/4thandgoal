/**
 * Tests for the rankings reader. Each test builds a temp public/ folder, because the real one may not hold the file yet.
 * The fixture is the file in the exact shape the pipeline writes, so a change to that shape breaks these tests.
 */
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import fixture from "@cpc/rankings/fixtures/rankings.json";

afterEach(() => {
  vi.restoreAllMocks();
});

/* A temp public/ folder with one week page per week folder, and the rankings file when one is given. */
async function readerOver(weeks: string[], rankings?: unknown) {
  const root = mkdtempSync(join(tmpdir(), "rankings-data-"));
  for (const week of weeks) {
    mkdirSync(join(root, "public", "2026", week), { recursive: true });
    writeFileSync(
      join(root, "public", "2026", week, "page.json"),
      weekPageJson({ avatars: { "10": "avatars/10.jpg" } }),
    );
  }
  if (rankings !== undefined) {
    writeFileSync(join(root, "public", "2026", "rankings.json"), JSON.stringify(rankings));
  }
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The week reader reads the working folder when it loads, so reset it to pick up the temp folder.
  vi.resetModules();
  return import("./rankings-data");
}

describe("loadRankings", () => {
  it("reads the fixture for the latest season", async () => {
    const { loadRankings } = await readerOver(["week-06"], fixture);
    const rankings = loadRankings();
    expect(rankings?.season).toBe(2026);
    const last = rankings!.weeks.at(-1)!;
    expect(last.week).toBe(6);
    expect(last.rows.map((row) => row.rank)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
    expect(last.rows[0].components).toEqual({ standing: 2, form: 1, schedule_played: 2, scoring: 1 });
  });

  it("reads rows with odds and rows with no odds under schema version 1", async () => {
    const { loadRankings } = await readerOver(["week-06"], fixture);
    const rankings = loadRankings()!;
    // Week 1 comes before the odds engine ran, so its rows have no odds key. Week 6 rows carry the odds.
    expect(rankings.weeks[0].rows.every((row) => row.odds === undefined)).toBe(true);
    const last = rankings.weeks.at(-1)!;
    expect(last.rows[1].odds).toEqual({ playoff: 100, bye: 88, seed: 1, status: "in" });
    expect(last.rows[11].odds).toEqual({ playoff: 0, bye: 0, seed: null, status: "out" });
    expect(last.rows.filter((row) => row.odds?.status === "open")).toHaveLength(10);
  });

  it("throws when the schema version is not 1", async () => {
    const { loadRankings } = await readerOver(["week-06"], { ...fixture, schema_version: 2 });
    expect(() => loadRankings()).toThrow(/schema_version 2/);
  });

  it("returns null when the file is missing", async () => {
    const { loadRankings } = await readerOver(["week-06"]);
    expect(loadRankings()).toBeNull();
  });
});

describe("latestAvatars", () => {
  it("reads the avatars of the latest week, with the week folder in front", async () => {
    const { latestAvatars } = await readerOver(["week-06", "week-07"]);
    expect(latestAvatars(2026)["10"]).toBe("/2026/week-07/avatars/10.jpg");
  });

  it("returns no avatars for a season with no week page", async () => {
    const { latestAvatars } = await readerOver(["week-06"]);
    expect(latestAvatars(2025)).toEqual({});
  });
});
