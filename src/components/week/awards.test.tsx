/**
 * Tests for the awards tiles. They render the week 6 JSON and read each title, player, and number.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Awards } from "./awards";
import { firstSentence, week6 } from "@/fixtures/week-page";

afterEach(() => {
  cleanup();
});

function renderAwards() {
  return render(<Awards awards={week6.awards} headshots={week6.headshots} blurb={week6.blurbs.awards} />);
}

describe("Awards", () => {
  it("shows each award title", () => {
    renderAwards();
    for (const title of ["Top Scorer", "MVB · Most Valuable Benchwarmer", "Underperformer", "Overachiever"]) {
      expect(screen.getByText(title)).toBeTruthy();
    }
  });

  it("shows each player and the points as formatted text", () => {
    renderAwards();
    expect(screen.getByText("Trevor Lawrence")).toBeTruthy();
    expect(screen.getByText("28.34")).toBeTruthy();
    expect(screen.getByText("Jayden Daniels")).toBeTruthy();
    expect(screen.getByText("21")).toBeTruthy();
    expect(screen.getByText("6.3")).toBeTruthy();
  });

  it("puts the projection in the sub line only when there is one", () => {
    renderAwards();
    expect(screen.getByText("Amon-Ra Dawg Your Team")).toBeTruthy();
    expect(screen.getByText("proj 23.08 · To Infinity and Bijan")).toBeTruthy();
    expect(screen.getByText("proj 7.58 · All You Need Is Love")).toBeTruthy();
  });

  it("shows a note in place of the player when the award is missing", () => {
    render(<Awards awards={[{ title: "Overachiever", missing: true }]} headshots={{}} blurb="" />);
    expect(screen.getByText("Projections unavailable this week")).toBeTruthy();
  });

  it("shows the blurb", () => {
    renderAwards();
    expect(screen.getByText(firstSentence(week6.blurbs.awards), { exact: false })).toBeTruthy();
  });
});
