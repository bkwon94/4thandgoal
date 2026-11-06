/**
 * Tests for the home part of the midseason package. Each test builds a temp public/ folder from the real week 6 page
 * and the real midseason fixture of CPC week 8, then reads the part that the home page gets for the latest week.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import fixture from "@cpc/midseason/fixtures/midseason.json";
import { publicOver, removePublics } from "./temp-public";

afterEach(() => {
  cleanup();
  removePublics();
});

/* The home part over a temp public/ folder with the week pages up to `latest`, and the midseason file of 2026 when
   one is given. */
async function homeOver(latest: number, report?: unknown) {
  publicOver({ latest, report });
  return (await import("./home")).homeSection;
}

describe("the home part of the midseason package", () => {
  it("shows the takeover in place of the usual top with week 8 published", async () => {
    const sections = (await homeOver(8, fixture))();
    expect(sections.map((section) => section.place)).toEqual(["takeover"]);
    render(<>{sections[0].part}</>);
    const takeover = screen.getByRole("region", { name: "2026 Midseason Report" });
    expect(within(takeover).getByRole("heading", { level: 2, name: "The Title Race" })).toBeTruthy();
    expect(within(takeover).getByRole("link", { name: "Read the Midseason Report" }).getAttribute("href")).toBe(
      "/midseason/2026/",
    );
  });

  it.each([9, 10])("shows the report tile with one big fact with week %i published", async (latest) => {
    const sections = (await homeOver(latest, fixture))();
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
