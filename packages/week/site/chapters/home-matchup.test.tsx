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

describe("HomeMatchup", () => {
  it("shows the margin, both teams with no top player, and the button to the week", () => {
    render(
      <HomeMatchup week={8} pick={week8.pick} avatars={{}} blurb={week8.blurbs.motw} href="/2026/week-08/" />,
    );
    const hero = screen.getByRole("region", { name: "Matchup of the Week" });
    expect(within(hero).getByText("1.43")).toBeTruthy();
    // The home hero shows the matchup in one look, so it names no top player.
    expect(hero.textContent).not.toContain(" · QB · ");
    expect(hero.textContent).not.toMatch(/ · (RB|WR|TE|K|DEF) · /);
    expect(within(hero).getByRole("link", { name: "Read Week 8" }).getAttribute("href")).toBe("/2026/week-08/");
    // The intro of the page holds the h1, so the hero has no heading.
    expect(within(hero).queryByRole("heading")).toBeNull();
  });
});
