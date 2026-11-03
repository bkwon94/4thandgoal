/**
 * Tests for the waiver team pick in local storage. A pick survives a reload, and a blocked storage never throws.
 * A value that is not a whole roster id reads as no pick.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { getTeamPick, setTeamPick } from "./team-pick";

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("the team pick", () => {
  it("reads as no pick on a first visit", () => {
    expect(getTeamPick()).toBeNull();
  });

  it("reads back the roster id that a pick saved", () => {
    setTeamPick(7);
    expect(getTeamPick()).toBe(7);
  });

  it("saves under its own key, apart from the passphrase", () => {
    setTeamPick(7);
    expect(localStorage.getItem("cpc.waiver-team")).toBe("7");
    expect(localStorage.getItem("cpc.passphrase")).toBeNull();
  });

  it("reads a value that is not a roster id as no pick", () => {
    localStorage.setItem("cpc.waiver-team", "abc");
    expect(getTeamPick()).toBeNull();
  });

  it("reads as no pick and saves nothing when storage throws", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(() => setTeamPick(7)).not.toThrow();
    expect(getTeamPick()).toBeNull();
  });
});
