/**
 * Tests for the hero of the home page. They render the week 8 JSON of CPC, as a reader sees it.
 * The first sentence tests use their own text, because the pipeline rewrites the blurbs of the published file.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week8 } from "../fixtures/week-page";
import { firstSentence, HomeMatchup } from "./home-matchup";

afterEach(() => {
  cleanup();
});

describe("firstSentence", () => {
  it("keeps a decimal inside the sentence", () => {
    expect(firstSentence("The Blue Tent stole this one by 1.43 in an upset. Down 3.67 after Sunday night.")).toBe(
      "The Blue Tent stole this one by 1.43 in an upset.",
    );
  });

  it("gives the whole blurb when it has no stop", () => {
    expect(firstSentence("A blurb with no stop")).toBe("A blurb with no stop");
  });
});

function renderHome() {
  render(<HomeMatchup week={8} pick={week8.pick} avatars={{}} blurb={week8.blurbs.motw} href="/2026/week-08/" />);
  return screen.getByRole("region", { name: "Matchup of the Week" });
}

describe("HomeMatchup", () => {
  it("has the winner by the margin in words as its title, at level 2 under the h1 of the intro (AT-10)", () => {
    const hero = renderHome();
    // CPC week 8: The Blue Tent over London Cooking, 100.31 to 98.88.
    const title = within(hero).getByRole("heading", { level: 2 });
    expect(title.textContent).toBe("The Blue Tent by 1.43");
    expect(within(hero).queryByRole("heading", { level: 1 })).toBeNull();
  });

  it("fills the slots in order: the week, the title, the reason, the team rows, then the link to the week", () => {
    const hero = renderHome();
    const slots = [...hero.querySelectorAll("[data-hero-slot]")].map((slot) => slot.getAttribute("data-hero-slot"));
    expect(slots).toEqual(["eyebrow", "title", "meta", "feature", "action"]);
    expect(hero.querySelector('[data-hero-slot="eyebrow"]')!.textContent).toBe("Week 08 // Matchup of the Week");
    expect(hero.querySelector('[data-hero-slot="meta"]')!.textContent).toBe("Closest Finish");
    const feature = within(hero.querySelector<HTMLElement>('[data-hero-slot="feature"]')!);
    expect(feature.getByText("The Blue Tent")).toBeTruthy();
    expect(feature.getByText("100.31")).toBeTruthy();
    expect(feature.getByText("London Cooking")).toBeTruthy();
    expect(feature.getByText("98.88")).toBeTruthy();
    const action = within(hero.querySelector<HTMLElement>('[data-hero-slot="action"]')!);
    expect(action.getByRole("link", { name: "Read Week 8" }).getAttribute("href")).toBe("/2026/week-08/");
  });

  it("names no top player, because the home hero shows the matchup in one look", () => {
    const hero = renderHome();
    expect(hero.textContent).not.toContain(" · QB · ");
    expect(hero.textContent).not.toMatch(/ · (RB|WR|TE|K|DEF) · /);
  });

  it("shows the first sentence of the blurb directly under the hero, outside its frame", () => {
    const hero = renderHome();
    const sentence = screen.getByText(firstSentence(week8.blurbs.motw));
    expect(sentence.tagName).toBe("P");
    expect(hero.contains(sentence)).toBe(false);
    expect(hero.compareDocumentPosition(sentence) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });
});
