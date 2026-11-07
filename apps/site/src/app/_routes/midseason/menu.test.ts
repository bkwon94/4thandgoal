/**
 * Tests for the menu link of the midseason package. Each test builds a temp public/ folder from the real week pages
 * and the real midseason fixture of CPC week 8, then reads the link that the menu gets.
 */
import { afterEach, describe, expect, it } from "vitest";
import fixture from "@cpc/midseason/fixtures/midseason.json";
import { publicOver, removePublics } from "./temp-public";

afterEach(removePublics);

async function linkOver(report?: unknown) {
  publicOver({ latest: 8, report });
  return (await import("./menu")).menuLink();
}

describe("the menu link of the midseason package", () => {
  it("links the report of the season of the latest week", async () => {
    expect(await linkOver(fixture)).toEqual({ label: "Midseason Report", href: "/midseason/2026/" });
  });

  it("gives no link when the season has no midseason file", async () => {
    expect(await linkOver()).toBeNull();
  });
});
