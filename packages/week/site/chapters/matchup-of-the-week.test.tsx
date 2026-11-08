/**
 * Tests for the hero of the week page, the matchup of the week. They render the week 8 JSON of CPC and read the hero.
 * They check what a reader sees by role and text, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { firstSentence, week8 } from "../fixtures/week-page";
import { matchupScene } from "../parts/matchup-scene";
import { MatchupOfTheWeek } from "./matchup-of-the-week";

afterEach(() => {
  cleanup();
});

function renderHero(avatars = week8.avatars, headshots = week8.headshots, scene?: ReturnType<typeof matchupScene>) {
  render(
    <MatchupOfTheWeek
      scene={scene}
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
  it("draws the scene of the week in its hero when the page passes it, as the first hero of the page (AT-15)", () => {
    const hero = renderHero(week8.avatars, week8.headshots, matchupScene(week8));
    expect(hero.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(1);
  });

  it("draws no scene when the page passes none, so the hero keeps the static grid", () => {
    expect(renderHero().querySelector("canvas")).toBeNull();
  });

  it("is the hero of the page, with the winner by the margin in words as the page heading (AT-10)", () => {
    const hero = renderHero();
    // CPC week 8: The Blue Tent over London Cooking, 100.31 to 98.88.
    const title = within(hero).getByRole("heading", { level: 1 });
    expect(title.textContent).toBe("The Blue Tent by 1.43");
    expect(title.getAttribute("data-hero-slot")).toBe("title");
    // The hero draws the art of the look, so the hero stays dark in light (AT-5).
    expect(hero.querySelectorAll("[data-hero-art]").length).toBeGreaterThan(0);
  });

  it("shows the dates and the publish date of the week", () => {
    const hero = renderHero();
    expect(within(hero).getByText("Oct 29 – Nov 2, 2026 · Published Tue Nov 3, 2026")).toBeTruthy();
  });

  it("shows the week as the eyebrow and the dates as the meta, before the title in the slot order", () => {
    const hero = renderHero();
    const slots = [...hero.querySelectorAll("[data-hero-slot]")].map((slot) => slot.getAttribute("data-hero-slot"));
    // The Matchup has no stats, so the stats slot renders no element (AT-6).
    expect(slots).toEqual(["eyebrow", "title", "meta", "feature", "action"]);
    expect(hero.querySelector('[data-hero-slot="eyebrow"]')!.textContent).toBe("Week 08 // Matchup of the Week");
    expect(hero.querySelector('[data-hero-slot="meta"]')!.textContent).toBe(
      "Oct 29 – Nov 2, 2026 · Published Tue Nov 3, 2026",
    );
  });

  it("shows the reason, both teams, and both scores in the feature (AT-16)", () => {
    const hero = renderHero();
    const feature = within(hero.querySelector<HTMLElement>('[data-hero-slot="feature"]')!);
    expect(feature.getByText("Closest Finish")).toBeTruthy();
    expect(feature.getByText("The Blue Tent")).toBeTruthy();
    expect(feature.getByText("London Cooking")).toBeTruthy();
    expect(feature.getByText("100.31")).toBeTruthy();
    expect(feature.getByText("98.88")).toBeTruthy();
  });

  it("shows the top player of each team", () => {
    const hero = renderHero();
    expect(within(hero).getByText("Brock Bowers · TE · 24.7")).toBeTruthy();
    expect(within(hero).getByText("Michael Wilson · WR · 22.8")).toBeTruthy();
  });

  it("shows the share of the winner as a bar with its value, as the last part of the hero (AT-5)", () => {
    const hero = renderHero();
    const bar = within(hero).getByRole("meter", { name: "Share of the points" });
    // 100.31 of 199.19 points.
    expect(bar.getAttribute("aria-valuenow")).toBe("50.4");
    expect(hero.querySelector('[data-hero-slot="action"]')!.contains(bar)).toBe(true);
    // No text or control of the hero follows the bar.
    const parts = [...hero.querySelectorAll("[data-hero-slot] *")].filter((part) => part.children.length === 0);
    expect(parts.at(-1)!.closest('[role="meter"]')).toBe(bar);
  });

  it("shows the headshot of the top player of the winner in a round frame", () => {
    const hero = renderHero();
    expect(within(hero).getByRole("img", { name: "Brock Bowers" }).getAttribute("src")).toBe("headshots/11604.png");
  });

  it("shows the initials when the week has no headshot of the top player (AT-33)", () => {
    const hero = renderHero(week8.avatars, {});
    expect(within(hero).getByRole("img", { name: "Brock Bowers" }).textContent).toBe("BB");
  });

  it("shows the full blurb as prose directly under the hero, outside its frame, with no fold (AT-11, AT-41)", () => {
    const hero = renderHero();
    const blurb = screen.getByText(firstSentence(week8.blurbs.motw), { exact: false });
    expect(blurb.tagName).toBe("P");
    expect(blurb.textContent).toBe(week8.blurbs.motw);
    expect(hero.contains(blurb)).toBe(false);
    expect(hero.compareDocumentPosition(blurb) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    // The blurb sits in the same chapter as the hero, the one the rail links.
    expect(blurb.closest("#motw")).toBe(hero.closest("#motw"));
    expect(screen.queryByRole("button")).toBeNull();
    expect(screen.queryByText(/read more/i)).toBeNull();
  });
});
