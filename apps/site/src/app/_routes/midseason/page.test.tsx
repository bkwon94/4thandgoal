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

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

/* A temp public/ folder with the week 8 page, and the midseason file when one is given. */
async function routeOver(report?: unknown) {
  const root = mkdtempSync(join(tmpdir(), "midseason-page-"));
  mkdirSync(join(root, "public", "2026", "week-08"), { recursive: true });
  writeFileSync(join(root, "public", "2026", "week-08", "page.json"), weekPageJson({}));
  if (report !== undefined) writeFileSync(join(root, "public", "2026", "midseason.json"), JSON.stringify(report));
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
});
