/**
 * Tests for the power rankings page. Each test builds a temp public/ folder, with or without the rankings file.
 * They read what a reader sees: the empty state, or the last week of the file with the week page avatars.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/lib/week-page-fixture";
import fixture from "@/components/rankings/fixture.json";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

/* A temp public/ folder with the week 6 page, and the rankings file when one is given. */
async function pageOver(rankings?: unknown) {
  const root = mkdtempSync(join(tmpdir(), "rankings-page-"));
  mkdirSync(join(root, "public", "2026", "week-06"), { recursive: true });
  writeFileSync(
    join(root, "public", "2026", "week-06", "page.json"),
    weekPageJson({ avatars: { "5": "avatars/5.jpg" } }),
  );
  if (rankings !== undefined) {
    writeFileSync(join(root, "public", "2026", "rankings.json"), JSON.stringify(rankings));
  }
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them to pick up the temp folder.
  vi.resetModules();
  return (await import("./page")).default;
}

describe("RankingsPage", () => {
  it("shows the empty state when the file is missing", async () => {
    const RankingsPage = await pageOver();
    render(<RankingsPage />);
    expect(screen.getByRole("heading", { level: 2, name: "Power Rankings" })).toBeTruthy();
    expect(screen.getByText("No power rankings are published yet.")).toBeTruthy();
    expect(screen.queryAllByRole("listitem")).toHaveLength(0);
  });

  it("shows the last week of the file with the avatars of the latest week page", async () => {
    const RankingsPage = await pageOver(fixture);
    render(<RankingsPage />);
    // The masthead names the week of the last entry in the file.
    expect(screen.getByRole("banner").textContent).toContain("WEEK 6");
    const rows = screen.getAllByRole("listitem");
    expect(rows).toHaveLength(12);
    expect(rows[0].querySelector("img")?.getAttribute("src")).toBe("/2026/week-06/avatars/5.jpg");
  });

  it("labels the table with a level-two heading that reads Power Rankings", async () => {
    const RankingsPage = await pageOver(fixture);
    render(<RankingsPage />);
    const main = screen.getByRole("main");
    expect(within(main).getByRole("heading", { level: 2, name: "Power Rankings" })).toBeTruthy();
  });

  it("moves the masthead week line with the chosen chip", async () => {
    const RankingsPage = await pageOver(fixture);
    render(<RankingsPage />);
    const banner = screen.getByRole("banner");
    const chip = (week: number) =>
      within(screen.getByRole("group", { name: "Week" })).getByRole("button", { name: `Week ${week}` });
    expect(banner.textContent).toContain("WEEK 6");
    fireEvent.click(chip(1));
    expect(banner.textContent).toContain("WEEK 1");
    expect(banner.textContent).not.toContain("WEEK 6");
  });
});
