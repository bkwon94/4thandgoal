/**
 * Tests for the flag of the hint of the hero scene, on the real storage of jsdom.
 * The hint shows until the first touch on any scene, then stays gone for that reader after a reload (AT-28).
 */
import { afterEach, describe, expect, it } from "vitest";
import { hintSeen, rememberHint } from "./scene-canvas";

afterEach(() => window.localStorage.clear());

describe("the flag of the hint", () => {
  it("shows the hint to a reader who never touched a scene", () => {
    expect(hintSeen()).toBe(false);
  });

  it("keeps the hint gone after the first touch, as a reload reads the same storage", () => {
    rememberHint();
    expect(hintSeen()).toBe(true);
  });
});
