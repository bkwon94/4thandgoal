/**
 * Tests for the waiver page route. Each test builds a temp public/ folder with week pages, some with a waiver file.
 * They read the static params and what a reader sees: the masthead line, the menu, and the lists with the week page avatars.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import fixture from "@/fixtures/waiver.json";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
});

/* A temp public/ folder with week 5 and week 6 pages. Only week 6 has the waiver file. */
async function routeOver() {
  const root = mkdtempSync(join(tmpdir(), "waiver-page-"));
  for (const week of ["week-05", "week-06"]) {
    mkdirSync(join(root, "public", "2026", week), { recursive: true });
    writeFileSync(
      join(root, "public", "2026", week, "page.json"),
      weekPageJson({
        week: Number(week.slice(-2)),
        avatars: { "4": "avatars/4.jpg" },
      }),
    );
  }
  writeFileSync(join(root, "public", "2026", "week-06", "waiver.json"), JSON.stringify(fixture));
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them.
  vi.resetModules();
  return import("./page");
}

describe("generateStaticParams", () => {
  // The client build gates the route file, so the params read the files only.
  it("lists only the weeks with a waiver file", async () => {
    const { generateStaticParams } = await routeOver();
    expect(generateStaticParams()).toEqual([{ season: "2026", week: "week-06" }]);
  });
});

describe("WaiverPage", () => {
  it("shows the week and the build time under the top band", async () => {
    const { default: WaiverPage } = await routeOver();
    render(await WaiverPage({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
    const page = document.body;
    expect(page.textContent).toContain("WEEK 6");
    // The build time reads in league time, US Eastern.
    expect(page.textContent).toContain("Built Fri, Oct 23, 10:05 AM EDT");
  });

  it("gives the menu a link to its own week, through the menu link of the waiver package", async () => {
    await routeOver();
    const { menuLink } = await import("./menu");
    expect(menuLink()).toEqual({ label: "Waiver Wire", href: "/2026/week-06/waiver/" });
  });

  it("shows the budgets with the avatars of the week folder, and the best adds after the top six", async () => {
    const { default: WaiverPage } = await routeOver();
    render(await WaiverPage({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
    const budgets = within(screen.getByRole("list", { name: "Budgets" })).getAllByRole("listitem");
    expect(budgets).toHaveLength(12);
    expect(within(budgets[0]).getByText("Pukancun on 3")).toBeTruthy();
    expect(budgets[0].querySelector("img")?.getAttribute("src")).toBe("/2026/week-06/avatars/4.jpg");
    expect(within(screen.getByRole("list", { name: "Also" })).getAllByRole("listitem")).toHaveLength(2);
  });
});
