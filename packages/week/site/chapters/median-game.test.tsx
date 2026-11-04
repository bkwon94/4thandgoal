/**
 * Tests for the median game. They render the week 6 JSON and read the KPI values, the bars, and the hint.
 * A copy of the JSON with no median checks that the chapter is left out.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { firstSentence, week6 } from "../fixtures/week-page";
import { MedianGame } from "./median-game";

afterEach(() => {
  cleanup();
});

function renderMedian() {
  return render(<MedianGame median={week6.median} blurb={week6.blurbs.median} />);
}

describe("MedianGame", () => {
  it("shows the median and both gaps with their signs", () => {
    renderMedian();
    expect(screen.getByText("106.83")).toBeTruthy();
    expect(screen.getByText("+2.79")).toBeTruthy();
    expect(screen.getByText("−2.79")).toBeTruthy();
    expect(screen.getByText("Bo Girds, closest win")).toBeTruthy();
    expect(screen.getByText("Amon-Ra Dawg Your Team, closest miss")).toBeTruthy();
  });

  it("shows one bar row per team with the score", () => {
    renderMedian();
    expect(screen.getByText("Lil Fridge")).toBeTruthy();
    expect(screen.getByText("126.79")).toBeTruthy();
    expect(screen.getByText("Return of T Mac")).toBeTruthy();
    expect(screen.getByText("120.29")).toBeTruthy();
  });

  it("shows the hint and the blurb", () => {
    renderMedian();
    expect(screen.getByText("Dashed line: median 106.83.")).toBeTruthy();
    expect(screen.getByText(firstSentence(week6.blurbs.median), { exact: false })).toBeTruthy();
  });

  it("leaves the chapter out when the week has no median game", () => {
    const copy = { ...week6, median: null };
    const { container } = render(<MedianGame median={copy.median} blurb={copy.blurbs.median} />);
    expect(container.innerHTML).toBe("");
    expect(screen.queryByText("The Median Game")).toBeNull();
  });
});
