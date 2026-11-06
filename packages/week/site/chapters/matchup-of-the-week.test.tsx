/**
 * Tests for the hero of the week page, the matchup of the week. They render the week 8 JSON of CPC and read the hero.
 * They check what a reader sees by role and text, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { firstSentence, week8 } from "../fixtures/week-page";
import { MatchupOfTheWeek } from "./matchup-of-the-week";

afterEach(() => {
  cleanup();
});

function renderHero(avatars = week8.avatars, headshots = week8.headshots) {
  render(
    <MatchupOfTheWeek
      week={week8.week}
      dates={week8.dates}
      publishDate={week8.publish_date}
      pick={week8.pick}
      avatars={avatars}
      headshots={headshots}
      blurb={week8.blurbs.motw}
    />,
  );
  return screen.getByRole("region", { name: "Matchup of the Week" });
}

describe("MatchupOfTheWeek", () => {
  it("is the hero of the page, with the week and the matchup of the week as the page heading", () => {
    const hero = renderHero();
    expect(within(hero).getByRole("heading", { level: 1 }).textContent).toBe("Week 08 // Matchup of the Week");
    // The hero draws the art of the look, so the hero stays dark in light (AT-5).
    expect(hero.querySelectorAll("[data-hero-art]").length).toBeGreaterThan(0);
  });

  it("shows the dates and the publish date of the week", () => {
    const hero = renderHero();
    expect(within(hero).getByText("Oct 29 – Nov 2, 2026 · Published Tue Nov 3, 2026")).toBeTruthy();
  });

  it("shows the reason, the margin, both teams, and both scores (AT-16)", () => {
    const hero = renderHero();
    expect(within(hero).getByText("Closest Finish · Margin")).toBeTruthy();
    expect(within(hero).getByText("1.43")).toBeTruthy();
    expect(within(hero).getByText("The Blue Tent")).toBeTruthy();
    expect(within(hero).getByText("London Cooking")).toBeTruthy();
    expect(within(hero).getByText("100.31")).toBeTruthy();
    expect(within(hero).getByText("98.88")).toBeTruthy();
  });

  it("shows the top player of each team", () => {
    const hero = renderHero();
    expect(within(hero).getByText("Brock Bowers · TE · 24.7")).toBeTruthy();
    expect(within(hero).getByText("Michael Wilson · WR · 22.8")).toBeTruthy();
  });

  it("shows the share of the winner as a bar with its value", () => {
    const hero = renderHero();
    const bar = within(hero).getByRole("meter", { name: "Share of the points" });
    // 100.31 of 199.19 points.
    expect(bar.getAttribute("aria-valuenow")).toBe("50.4");
  });

  it("shows the headshot of the top player of the winner in a round frame", () => {
    const hero = renderHero();
    expect(within(hero).getByRole("img", { name: "Brock Bowers" }).getAttribute("src")).toBe("headshots/11604.png");
  });

  it("shows the initials when the week has no headshot of the top player (AT-33)", () => {
    const hero = renderHero(week8.avatars, {});
    expect(within(hero).getByRole("img", { name: "Brock Bowers" }).textContent).toBe("BB");
  });

  it("shows the full blurb as prose", () => {
    const hero = renderHero();
    const blurb = within(hero).getByText(firstSentence(week8.blurbs.motw), { exact: false });
    expect(blurb.tagName).toBe("P");
    expect(blurb.textContent).toBe(week8.blurbs.motw);
  });
});
