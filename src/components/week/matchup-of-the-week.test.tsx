/**
 * Tests for the matchup of the week. They render the week 6 JSON and read the teams, the scores, and the tag.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { firstSentence, week6 } from "@/fixtures/week-page";
import { MatchupOfTheWeek } from "./matchup-of-the-week";

afterEach(() => {
  cleanup();
});

function renderPick() {
  return render(<MatchupOfTheWeek pick={week6.pick} avatars={week6.avatars} blurb={week6.blurbs.motw} />);
}

describe("MatchupOfTheWeek", () => {
  it("shows the label, the reason tag, and both team names", () => {
    renderPick();
    expect(screen.getByText("Matchup of the Week")).toBeTruthy();
    expect(screen.getByText("Closest Finish")).toBeTruthy();
    expect(screen.getByText("behold the lamb")).toBeTruthy();
    expect(screen.getByText("Bo Girds")).toBeTruthy();
  });

  it("shows both scores as formatted text", () => {
    renderPick();
    expect(screen.getByText("114.95")).toBeTruthy();
    expect(screen.getByText("109.61")).toBeTruthy();
  });

  it("shows each team's avatar from the week folder", () => {
    const { container } = renderPick();
    const srcs = [...container.querySelectorAll("img")].map((img) => img.getAttribute("src"));
    expect(srcs).toEqual(["avatars/10.jpg", "avatars/6.jpg"]);
  });

  it("falls back to the default avatar when the map has no entry", () => {
    const { container } = render(<MatchupOfTheWeek pick={week6.pick} avatars={{}} blurb="" />);
    expect(container.querySelector("img")?.getAttribute("src")).toBe("/images/avatar-default.svg");
  });

  it("shows the blurb", () => {
    renderPick();
    expect(screen.getByText(firstSentence(week6.blurbs.motw), { exact: false })).toBeTruthy();
  });
});
