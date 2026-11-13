/**
 * Tests for the viewport of every page, which the root layout exports. An iPhone gives a page its safe area only with viewport-fit=cover, so
 * the ask box of the front door can keep clear of the home bar (AT-47).
 */
import { describe, expect, it } from "vitest";
import { SITE_VIEWPORT as viewport } from "./viewport";

describe("the viewport of the root layout", () => {
  it("covers the whole screen of an iPhone, so env(safe-area-inset-bottom) reaches the page (AT-47)", () => {
    expect(viewport).toMatchObject({ width: "device-width", initialScale: 1, viewportFit: "cover" });
  });

  it("asks Chrome on Android to shrink the layout viewport with the keyboard, so the ask box sticks above it", () => {
    expect(viewport.interactiveWidget).toBe("resizes-content");
  });
});
