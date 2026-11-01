/**
 * Tests for the managers index route. Each test builds a temp public/ folder with a week page, the managers file, and the rankings file.
 * They read the static params, the title, and the twelve cards a reader sees, in standings order, each with its grade letter.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/lib/week-page-fixture";
import fixture from "@/components/managers/fixture.json";
import { rankings as rankingsFixture } from "@/components/rankings/fixture";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

/* A temp public/ folder with the week 6 page, the rankings file, and the managers file when one is given. */
async function routeOver(managers?: unknown) {
  const root = mkdtempSync(join(tmpdir(), "managers-index-"));
  mkdirSync(join(root, "public", "2026", "week-06"), { recursive: true });
  writeFileSync(join(root, "public", "2026", "week-06", "page.json"), weekPageJson({ avatars: {} }));
  writeFileSync(join(root, "public", "2026", "rankings.json"), JSON.stringify(rankingsFixture));
  if (managers !== undefined) writeFileSync(join(root, "public", "2026", "managers.json"), JSON.stringify(managers));
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them.
  vi.resetModules();
  return import("./page.managers");
}

describe("generateStaticParams", () => {
  it("lists the latest season when the managers file exists", async () => {
    const { generateStaticParams } = await routeOver(fixture);
    expect(generateStaticParams()).toEqual([{ season: "2026" }]);
  });

  it("lists no season when the managers file is missing", async () => {
    const { generateStaticParams } = await routeOver();
    expect(generateStaticParams()).toEqual([]);
  });
});

describe("ManagersIndex", () => {
  it("has the managers title", async () => {
    const { metadata } = await routeOver(fixture);
    expect(metadata.title).toBe("Managers · Cornerstone Fantasy Football League");
  });

  it("lists twelve cards in standings order, each one link to its manager page", async () => {
    const { default: ManagersPage } = await routeOver(fixture);
    render(await ManagersPage({ params: Promise.resolve({ season: "2026" }) }));
    const links = within(screen.getByRole("main")).getAllByRole("link");
    expect(links.map((link) => link.getAttribute("href"))).toEqual(
      [3, 5, 6, 9, 2, 1, 8, 10, 12, 11, 7, 4].map((id) => `/2026/managers/${id}/`),
    );
    // One card reads the name, the owner, and the record.
    const maye = links[3];
    expect(maye.textContent).toContain("Maye d'force B with U");
    expect(maye.textContent).toContain(fixture.managers[8].team.owner);
    expect(maye.textContent).toContain("7-5");
  });

  it("shows the grade letter on each card, and a dash with no grade", async () => {
    const managers = fixture.managers.map((entry) => (entry.roster_id === 5 ? { ...entry, grade: null } : entry));
    const { default: ManagersPage } = await routeOver({ ...fixture, managers });
    render(await ManagersPage({ params: Promise.resolve({ season: "2026" }) }));
    const links = within(screen.getByRole("main")).getAllByRole("link");
    // Maye d'force B with U holds a B. London Cooking has no grade in this file.
    expect(within(links[3]).getByText("B")).toBeTruthy();
    expect(within(links[1]).getByText("—")).toBeTruthy();
  });

  it("marks the managers entry of the menu as the open page", async () => {
    const { default: ManagersPage } = await routeOver(fixture);
    render(await ManagersPage({ params: Promise.resolve({ season: "2026" }) }));
    const row = screen.getByRole("navigation", { name: "Site menu" });
    expect(within(row).getByRole("link", { name: "Managers" }).getAttribute("aria-current")).toBe("page");
  });
});
