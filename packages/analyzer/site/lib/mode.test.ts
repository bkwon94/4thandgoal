/**
 * Tests for the mode of the analyzer from the query of its link: Grade a trade, or Find a trade with the finder flag on.
 * Each test reads one query string.
 */
import { describe, expect, it } from "bun:test";
import { readMode, withMode } from "./mode";

describe("readMode", () => {
  it("reads find from a link with the Find mode while the finder flag is on", () => {
    expect(readMode("?mode=find", true)).toBe("find");
  });

  it("reads grade from a link with the Grade mode", () => {
    expect(readMode("?mode=grade", true)).toBe("grade");
  });

  it("reads grade from a link with no mode or an unknown mode", () => {
    expect(readMode("", true)).toBe("grade");
    expect(readMode("?mode=deadline", true)).toBe("grade");
  });

  it("reads grade from a Find link while the finder flag is off", () => {
    expect(readMode("?mode=find", false)).toBe("grade");
  });
});

describe("withMode", () => {
  it("sets the mode and keeps the other keys of the query", () => {
    expect(withMode("?team=3&with=6", "find")).toBe("?team=3&with=6&mode=find");
    expect(withMode("?mode=find&team=3", "grade")).toBe("?mode=grade&team=3");
  });
});
