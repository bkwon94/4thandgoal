/**
 * Tests for the waiver reader. Each test builds a temp public/ folder with week pages, some with a waiver file.
 * The fixture is the file in the exact shape the pipeline writes, so a change to that shape breaks these tests.
 */
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import fixture from "@/fixtures/waiver.json";

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
});

/* A temp public/ folder with one week page per week folder, and the waiver file in the weeks given. */
async function readerOver(weeks: string[], withWaiver: Record<string, unknown>) {
  const root = mkdtempSync(join(tmpdir(), "waiver-data-"));
  for (const week of weeks) {
    mkdirSync(join(root, "public", "2026", week), { recursive: true });
    writeFileSync(join(root, "public", "2026", week, "page.json"), weekPageJson());
  }
  for (const [week, body] of Object.entries(withWaiver)) {
    writeFileSync(join(root, "public", "2026", week, "waiver.json"), JSON.stringify(body));
  }
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The week reader reads the working folder when it loads, so reset it to pick up the temp folder.
  vi.resetModules();
  return import("./waiver-data");
}

describe("listWaiverWeeks", () => {
  it("lists only the weeks with a waiver file", async () => {
    const { listWaiverWeeks } = await readerOver(["week-05", "week-06"], { "week-06": fixture });
    expect(listWaiverWeeks()).toEqual([{ season: "2026", week: "week-06" }]);
  });
});

describe("loadWaiver", () => {
  it("reads the fixture board", async () => {
    const { loadWaiver } = await readerOver(["week-06"], { "week-06": fixture });
    const board = loadWaiver("2026", "week-06")!;
    expect(board.week).toBe(6);
    expect(board.buckets.best_adds).toHaveLength(8);
    expect(board.buckets.best_adds[0]).toMatchObject({ player_id: "7567", name: "Kenny Gainwell", position: "RB" });
    expect(board.budgets).toHaveLength(12);
  });

  it("returns null for a week with no waiver file", async () => {
    const { loadWaiver } = await readerOver(["week-05"], {});
    expect(loadWaiver("2026", "week-05")).toBeNull();
  });

  it("throws when the schema version is not 1", async () => {
    const { loadWaiver } = await readerOver(["week-06"], { "week-06": { ...fixture, schema_version: 2 } });
    expect(() => loadWaiver("2026", "week-06")).toThrow(/schema_version 2/);
  });
});

describe("currentWaiverHref", () => {
  it("links the latest week with a waiver file", async () => {
    // Week 7 has a page but no waiver file yet, so the link stays on week 6.
    const { currentWaiverHref } = await readerOver(["week-05", "week-06", "week-07"], {
      "week-05": fixture,
      "week-06": fixture,
    });
    expect(currentWaiverHref()).toBe("/2026/week-06/waiver/");
  });

  it("gives no link when no week has a waiver file", async () => {
    const { currentWaiverHref } = await readerOver(["week-06"], {});
    expect(currentWaiverHref()).toBeNull();
  });
});
