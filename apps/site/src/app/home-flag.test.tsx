/**
 * Tests for the page at / under the flag front_door of client.toml: off, / is the home page with its chapters; on, / is
 * the front door. Each test renders the page with the fixed copy of the published data of cpc (ticket 43 of front-door).
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import { clientValues } from "@/generated/client-values";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

afterEach(() => {
  cleanup();
  vi.doUnmock("@/generated/client-values");
  vi.restoreAllMocks();
  localStorage.clear();
});

/* The page at / of a build with the flag front_door set to `frontDoor`. */
async function homeWithFlag(frontDoor: boolean) {
  const values = await vi.importActual<typeof import("@/generated/client-values")>("@/generated/client-values");
  vi.resetModules();
  readFixtureSite("cpc");
  vi.doMock("@/generated/client-values", () => ({ clientValues: { ...values.clientValues, frontDoor } }));
  return (await import("./page")).default;
}

describe("the page at /", () => {
  it("is the home page of main with the front door off: the intro, the chapters, and no sheet of Your team", async () => {
    const Home = await homeWithFlag(false);
    render(<Home />);
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe(clientValues.copy.siteName);
    expect(screen.getByRole("region", { name: "Weekly Reports" })).toBeTruthy();
    expect(screen.queryByRole("dialog", { name: "Which team is yours?" })).toBeNull();
    expect(screen.queryByRole("form", { name: "Ask" })).toBeNull();
  });

  it("is the front door with the front door on: the sheet of Your team on a first visit, and no home chapter", async () => {
    const Home = await homeWithFlag(true);
    render(<Home />);
    expect(await screen.findByRole("dialog", { name: "Which team is yours?" })).toBeTruthy();
    expect(screen.queryByRole("region", { name: "Weekly Reports" })).toBeNull();
  });
});
