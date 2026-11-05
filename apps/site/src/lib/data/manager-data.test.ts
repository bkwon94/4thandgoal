/**
 * Tests for the managers reader. Each test builds a temp public/ folder, because the real one may not hold the file yet.
 * The fixtures are the managers file and the rankings file in the exact shape the pipeline writes.
 */
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import { managers as fixture } from "@cpc/managers/fixtures/managers";
import { rankings as rankingsFixture } from "@cpc/rankings/fixtures/rankings";

afterEach(() => {
  vi.restoreAllMocks();
});

/* The rankings fixture with a week 5 before week 6, where each team's playoff odds are 10 points lower.
   The fixture's own week before week 6 is week 1, which has no odds. */
const rankingsWithWeek5 = (() => {
  const last = rankingsFixture.weeks.at(-1)!;
  const week5 = {
    ...last,
    week: 5,
    rows: last.rows.map((row) => ({ ...row, odds: { ...row.odds, playoff: Math.max(row.odds!.playoff - 10, 0) } })),
  };
  return { ...rankingsFixture, weeks: [rankingsFixture.weeks[0], week5, last] };
})();

/* A temp public/ folder with one week page, and the managers file and the rankings file when one is given. */
async function readerOver({ managers, rankings }: { managers?: unknown; rankings?: unknown }) {
  const root = mkdtempSync(join(tmpdir(), "manager-data-"));
  mkdirSync(join(root, "public", "2026", "week-06"), { recursive: true });
  writeFileSync(join(root, "public", "2026", "week-06", "page.json"), weekPageJson({ avatars: {} }));
  if (managers !== undefined) writeFileSync(join(root, "public", "2026", "managers.json"), JSON.stringify(managers));
  if (rankings !== undefined) writeFileSync(join(root, "public", "2026", "rankings.json"), JSON.stringify(rankings));
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The week reader reads the working folder when it loads, so reset it to pick up the temp folder.
  vi.resetModules();
  return import("./manager-data");
}

describe("loadManagers", () => {
  it("joins a manager with its odds, rank, and changes from the last rankings week", async () => {
    const { loadManagers } = await readerOver({ managers: fixture, rankings: rankingsWithWeek5 });
    const managers = loadManagers()!;
    expect(managers.season).toBe(2026);
    expect(managers.through).toBe(6);
    const maye = managers.managers.find((manager) => manager.roster_id === 9)!;
    expect(maye.team.name).toBe("Maye d'force B with U");
    expect([maye.wins, maye.losses]).toEqual([7, 5]);
    expect(maye.standing).toBe(4);
    expect(maye.rank).toBe(4);
    expect(maye.movement).toBe(-2);
    expect(maye.odds).toEqual({ playoff: 71, bye: 9, seed: 4, status: "open" });
    expect(maye.odds_change).toBe(10);
  });

  it("lists the managers in standings order", async () => {
    const { loadManagers } = await readerOver({ managers: fixture, rankings: rankingsFixture });
    const managers = loadManagers()!.managers;
    expect(managers.map((manager) => manager.roster_id)).toEqual([3, 5, 6, 9, 2, 1, 8, 10, 12, 11, 7, 4]);
    expect(managers.map((manager) => manager.standing)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
  });

  it("gives no odds change when the week before has no odds", async () => {
    // The fixture's week before week 6 is week 1, before the odds engine ran.
    const { loadManagers } = await readerOver({ managers: fixture, rankings: rankingsFixture });
    const maye = loadManagers()!.managers.find((manager) => manager.roster_id === 9)!;
    expect(maye.odds?.playoff).toBe(71);
    expect(maye.odds_change).toBeNull();
  });

  it("gives no odds when no week has odds", async () => {
    const noOdds = {
      ...rankingsFixture,
      weeks: rankingsFixture.weeks.map((week) => ({ ...week, rows: week.rows.map(({ odds: _odds, ...row }) => row) })),
    };
    const { loadManagers } = await readerOver({ managers: fixture, rankings: noOdds });
    const managers = loadManagers()!.managers;
    expect(managers.every((manager) => manager.odds === null && manager.odds_change === null)).toBe(true);
    expect(managers[0].rank).toBe(2);
  });

  it("orders by wins, then points, with no rankings file", async () => {
    const { loadManagers } = await readerOver({ managers: fixture });
    const managers = loadManagers()!.managers;
    expect(managers.map((manager) => manager.roster_id)).toEqual([3, 5, 6, 9, 2, 1, 8, 10, 12, 11, 7, 4]);
    expect(managers[3]).toMatchObject({ standing: 4, rank: null, movement: null, odds: null, odds_change: null });
  });

  it("throws when the schema version is not 1", async () => {
    const { loadManagers } = await readerOver({ managers: { ...fixture, schema_version: 2 }, rankings: rankingsFixture });
    expect(() => loadManagers()).toThrow(/schema_version 2/);
  });

  it("returns null when the file is missing", async () => {
    const { loadManagers } = await readerOver({ rankings: rankingsFixture });
    expect(loadManagers()).toBeNull();
  });
});

describe("currentManagersHref", () => {
  it("links the managers index of the latest season when the file exists", async () => {
    const { currentManagersHref } = await readerOver({ managers: fixture });
    expect(currentManagersHref()).toBe("/2026/managers/");
  });

  it("gives no link when the file is missing", async () => {
    const { currentManagersHref } = await readerOver({});
    expect(currentManagersHref()).toBeNull();
  });
});
