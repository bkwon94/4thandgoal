/**
 * Tests for the waiver page route. Each test builds a temp public/ folder with week pages, some with a waiver file.
 * They read the static params and what a reader sees: the masthead line, the menu, and the lists with the week page avatars.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/lib/week-page-fixture";
import fixture from "@/components/waiver/fixture.json";

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
  return import("./page.waiver");
}

describe("generateStaticParams", () => {
  // The flag gates the route file in next.config, so the params read the files only.
  it("lists only the weeks with a waiver file", async () => {
    const { generateStaticParams } = await routeOver();
    expect(generateStaticParams()).toEqual([{ season: "2026", week: "week-06" }]);
  });
});

describe("WaiverPage", () => {
  it("shows the week and the build time in the masthead", async () => {
    const { default: WaiverPage } = await routeOver();
    render(await WaiverPage({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
    const banner = screen.getByRole("banner");
    expect(banner.textContent).toContain("WEEK 6");
    // The build time reads in league time, US Eastern.
    expect(banner.textContent).toContain("Built Fri, Oct 23, 10:05 AM EDT");
  });

  it("marks itself as the current page in the menu, with the flag on", async () => {
    // The flag on puts the waiver page in the menu. The masthead itself shows no waiver link outside the menu.
    vi.stubEnv("NEXT_PUBLIC_WAIVER", "on");
    const { default: WaiverPage } = await routeOver();
    render(await WaiverPage({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
    const banner = screen.getByRole("banner");
    // The desktop row renders the menu, so the one waiver link of the banner is the item of the row.
    const row = within(banner).getByRole("navigation", { name: "Site menu" });
    const rowItem = within(row).getByRole("link", { name: "Waiver Wire" });
    expect(within(banner).getAllByRole("link", { name: "Waiver Wire" })).toEqual([rowItem]);
    expect(rowItem.getAttribute("aria-current")).toBe("page");
    fireEvent.click(within(banner).getByRole("button", { name: "Menu" }));
    const dialog = await screen.findByRole("dialog", { name: "Menu" });
    const menu = within(dialog).getByRole("navigation", { name: "Site menu" });
    expect(within(menu).getByRole("link", { name: "Waiver Wire" }).getAttribute("aria-current")).toBe("page");
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
