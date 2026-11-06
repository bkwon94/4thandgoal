/**
 * Tests for the midseason report route. Each test builds a temp public/ folder, with or without the midseason file.
 * They read what a reader sees: a static param per season with the file, and the report of that season.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import fixture from "@cpc/midseason/fixtures/midseason.json";
import simFixture from "@cpc/sim/fixtures/sim.json";
import { publicOver, removePublics } from "./temp-public";

afterEach(() => {
  cleanup();
  removePublics();
});

/* The route over a temp public/ folder with the weeks to week 8, and the midseason file and the sim file when each
   is given. */
async function routeOver(report?: unknown, sim?: unknown) {
  publicOver({ report, sim });
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
    expect(screen.getByRole("heading", { level: 1, name: "The Title Race" })).toBeTruthy();
    expect(screen.getByRole("navigation", { name: "Chapters" })).toBeTruthy();
  });

  it("shows the avatar of the latest week on each team award", async () => {
    publicOver({ report: fixture, avatars: { "8": "avatars/8.webp" } });
    const route = await import("./page");
    render(await route.default({ params: Promise.resolve({ season: "2026" }) }));
    // Return of T Mac, roster 8, is the Streaming king of the fixture.
    expect(screen.getByRole("img", { name: "Return of T Mac" }).getAttribute("src")).toBe("/2026/week-08/avatars/8.webp");
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
    expect(finale.querySelector("h3")!.textContent).toBe("Sim the Rest of the Season");
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
