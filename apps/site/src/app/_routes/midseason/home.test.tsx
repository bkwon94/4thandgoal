/**
 * Tests for the home part of the midseason package. Each test builds a temp public/ folder from the real week 6 page
 * and the real midseason fixture of CPC week 8, then reads the part that the home page gets for the latest week.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import fixture from "@cpc/midseason/fixtures/midseason.json";

const roots: string[] = [];

afterEach(() => {
  cleanup();
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
  vi.restoreAllMocks();
});

/* A temp public/ folder with the week pages up to `latest`, and the midseason file of 2026 when one is given. */
async function homeOver(latest: number, report?: unknown) {
  const root = mkdtempSync(join(tmpdir(), "midseason-home-"));
  roots.push(root);
  for (let week = 6; week <= latest; week++) {
    const folder = join(root, "public", "2026", `week-${String(week).padStart(2, "0")}`);
    mkdirSync(folder, { recursive: true });
    writeFileSync(join(folder, "page.json"), weekPageJson({ week, avatars: {} }));
  }
  if (report !== undefined) writeFileSync(join(root, "public", "2026", "midseason.json"), JSON.stringify(report));
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them to pick up the temp folder.
  vi.resetModules();
  return (await import("./home")).homeSection;
}

describe("the home part of the midseason package", () => {
  it.each([8, 9])("shows the takeover in place of the usual top with week %i published", async (latest) => {
    const sections = (await homeOver(latest, fixture))();
    expect(sections.map((section) => section.place)).toEqual(["takeover"]);
    render(<>{sections[0].part}</>);
    const takeover = screen.getByRole("region", { name: "2026 Midseason Report" });
    expect(within(takeover).getByRole("heading", { level: 2, name: "The title race" })).toBeTruthy();
    expect(within(takeover).getByRole("link", { name: "Read the Midseason Report" }).getAttribute("href")).toBe(
      "/midseason/2026/",
    );
  });

  it("shows the report tile with one big fact with week 10 published", async () => {
    const sections = (await homeOver(10, fixture))();
    expect(sections.map((section) => section.place)).toEqual(["middle"]);
    render(<>{sections[0].part}</>);
    expect(screen.queryByRole("region", { name: "2026 Midseason Report" })).toBeNull();
    const link = screen.getByRole("link", { name: /Midseason Report/ });
    expect(link.getAttribute("href")).toBe("/midseason/2026/");
    expect(within(link).getByText("16.8%")).toBeTruthy();
    expect(within(link).getByText("London Cooking")).toBeTruthy();
  });

  it("gives no part when the season has no midseason file", async () => {
    expect((await homeOver(8))()).toEqual([]);
  });
});
