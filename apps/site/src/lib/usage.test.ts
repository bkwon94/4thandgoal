/**
 * Tests for the usage helpers: the count script URL and the event call.
 * The event call must never throw, so one test runs it with no goatcounter global.
 */
import { afterEach, describe, expect, it, vi } from "vitest";
import { countEvent, usageScriptUrl } from "./usage";

afterEach(() => {
  delete window.goatcounter;
});

describe("usageScriptUrl", () => {
  it("builds the count URL from a site code", () => {
    expect(usageScriptUrl("cpcfantasy")).toBe("https://cpcfantasy.goatcounter.com/count");
  });

  it("returns null for an empty code", () => {
    expect(usageScriptUrl("")).toBeNull();
  });
});

describe("countEvent", () => {
  it("calls count with the event name as the path", () => {
    const count = vi.fn();
    window.goatcounter = { count };
    countEvent("analyze-grade");
    expect(count).toHaveBeenCalledWith({ path: "analyze-grade", event: true });
  });

  it("does nothing when goatcounter is absent", () => {
    expect(() => countEvent("analyze-grade")).not.toThrow();
  });
});
