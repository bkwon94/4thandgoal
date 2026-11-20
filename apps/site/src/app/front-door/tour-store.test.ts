/**
 * Tests for the seen store of the Tour: the key `cpc.tour-seen` in local storage, one read and one write.
 * A blocked store counts as seen, so a browser with no storage never gets the Tour.
 */
import { afterEach, describe, expect, it, vi } from "vitest";
import { TOUR_SEEN_KEY, markTourSeen, tourSeen } from "./tour-store";

afterEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("the seen store of the Tour", () => {
  it("keeps the seen key as cpc.tour-seen, beside the other stores of the front door", () => {
    expect(TOUR_SEEN_KEY).toBe("cpc.tour-seen");
  });

  it("reads a browser with no seen key as not seen", () => {
    localStorage.removeItem("cpc.tour-seen");
    expect(tourSeen()).toBe(false);
  });

  it('writes "1" and then reads as seen (AT-23)', () => {
    localStorage.removeItem("cpc.tour-seen");
    markTourSeen();
    expect(localStorage.getItem("cpc.tour-seen")).toBe("1");
    expect(tourSeen()).toBe(true);
  });

  it("reads any value as seen", () => {
    localStorage.setItem("cpc.tour-seen", "yes");
    expect(tourSeen()).toBe(true);
  });

  it("reads as seen when the read of local storage throws (AT-26)", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("SecurityError");
    });
    expect(tourSeen()).toBe(true);
  });

  it("does not throw when the write of local storage throws", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("QuotaExceededError");
    });
    expect(() => markTourSeen()).not.toThrow();
  });
});
