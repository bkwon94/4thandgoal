/**
 * Tests for the midseason report route. Each test builds a temp public/ folder, with or without the midseason file.
 * They read what a reader sees: a static param per season with the file, and the report of that season.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import fixture from "@cpc/midseason/fixtures/midseason.json";
import simFixture from "@cpc/sim/fixtures/sim.json";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

/* A temp public/ folder with the week 8 page, and the midseason file and the sim file when each is given. */
async function routeOver(report?: unknown, sim?: unknown) {
  const root = mkdtempSync(join(tmpdir(), "midseason-page-"));
  mkdirSync(join(root, "public", "2026", "week-08"), { recursive: true });
  writeFileSync(join(root, "public", "2026", "week-08", "page.json"), weekPageJson({}));
  if (report !== undefined) writeFileSync(join(root, "public", "2026", "midseason.json"), JSON.stringify(report));
  if (sim !== undefined) writeFileSync(join(root, "public", "2026", "sim.json"), JSON.stringify(sim));
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them to pick up the temp folder.
  vi.resetModules();
  return import("./page");
}

describe("the midseason route", () => {
  it("builds no page when no season has the file", async () => {
    const route = await routeOver();
    expect(route.generateStaticParams()).toEqual([]);
  });

  it("builds the report of 2026 from the midseason file", async () => {
    const route = await routeOver(fixture);
    expect(route.generateStaticParams()).toEqual([{ season: "2026" }]);
    render(await route.default({ params: Promise.resolve({ season: "2026" }) }));
    expect(screen.getByRole("heading", { level: 1, name: "The title race" })).toBeTruthy();
    expect(screen.getByRole("navigation", { name: "Chapters" })).toBeTruthy();
  });

  it("fails loud on a midseason file of another schema version", async () => {
    const route = await routeOver({ ...fixture, schema_version: 2 });
    await expect(route.default({ params: Promise.resolve({ season: "2026" }) })).rejects.toThrow(
      /schema_version 2, but this site reads schema_version 1/,
    );
  });

  it("ends the last act on the sim replay when the season has the sim file", async () => {
    // AT-29: the sim is the last chapter of the report.
    const route = await routeOver(fixture, simFixture);
    render(await route.default({ params: Promise.resolve({ season: "2026" }) }));
    const last = document.getElementById(fixture.acts.at(-1)!.key)!;
    const finale = last.lastElementChild!;
    expect(finale.querySelector("h3")!.textContent).toBe("Sim the rest of the season");
    expect(screen.getByRole("button", { name: "Sim the season" })).toBeTruthy();
  });

  it("shows no replay when the season has no sim file", async () => {
    const route = await routeOver(fixture);
    render(await route.default({ params: Promise.resolve({ season: "2026" }) }));
    expect(screen.queryByRole("button", { name: "Sim the season" })).toBeNull();
  });

  it("fails loud on a sim file of another schema version", async () => {
    const route = await routeOver(fixture, { ...simFixture, schema_version: 2 });
    await expect(route.default({ params: Promise.resolve({ season: "2026" }) })).rejects.toThrow(
      /sim.json has schema_version 2, but this site reads schema_version 1/,
    );
  });
});
