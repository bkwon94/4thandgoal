/**
 * Tests for the favored side of a grade: the side that the mesh flashes and dips toward at the reveal.
 * Each input is a real analyze fixture, and the expected side comes from the rule of the spec, not from the code.
 */
import { describe, expect, it } from "vitest";
import { analyzeResponse, analyzeResponseThree, analyzeResponseTradeA } from "./fixtures/api";
import type { AnalyzeResponse, Lean } from "./analyze-types";
import { favoredSide } from "./favored-side";

const withLean = (doc: AnalyzeResponse, lean: Lean): AnalyzeResponse => ({ ...doc, lean });

describe("favoredSide", () => {
  it("favors the asker on a yes, so the reveal dips under the side of the asker", () => {
    // The fixture is a Lean yes of roster 4, the asker.
    expect(favoredSide(analyzeResponse)).toBe(4);
    // Trade A is a Send it of roster 10, the asker, though the fairness block names roster 6 as the side that gives more.
    expect(favoredSide(analyzeResponseTradeA)).toBe(10);
  });

  it("favors the other side of a two-side trade on a no", () => {
    expect(favoredSide(withLean(analyzeResponse, "Lean no"))).toBe(12);
    expect(favoredSide(withLean(analyzeResponse, "Pass"))).toBe(12);
  });

  it("favors no side on a Gut call", () => {
    expect(favoredSide(withLean(analyzeResponse, "Gut call"))).toBeNull();
    expect(favoredSide(analyzeResponseThree)).toBeNull();
  });

  it("favors the asker of a three-side trade on a yes, and no one side on a no", () => {
    expect(favoredSide(withLean(analyzeResponseThree, "Lean yes"))).toBe(4);
    expect(favoredSide(withLean(analyzeResponseThree, "Lean no"))).toBeNull();
  });
});
