/**
 * Tests for Next week. They render the week 8 JSON of CPC and read each game card, the Must Watch reason, and the byes.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week8 } from "../fixtures/week-page";
import { NextWeek } from "./next-week";

afterEach(() => {
  cleanup();
});

function renderNext(games = week8.next) {
  render(<NextWeek week={week8.week} games={games} avatars={week8.avatars} blurb={week8.blurbs.next_week} />);
  return screen.getByRole("region", { name: "Next week" });
}

const cards = (chapter: HTMLElement) => within(chapter).getAllByRole("article");

describe("NextWeek", () => {
  it("names the week after the page's week and shows the blurb before the cards", () => {
    const chapter = renderNext();
    expect(chapter.id).toBe("next-week");
    expect(within(chapter).getByText("Week 09")).toBeTruthy();
    const blurb = within(chapter).getByText(week8.blurbs.next_week!);
    expect(blurb.tagName).toBe("P");
    expect(blurb.compareDocumentPosition(cards(chapter)[0]) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("shows a card for each game with both teams and their records", () => {
    const chapter = renderNext();
    expect(cards(chapter)).toHaveLength(6);
    const first = cards(chapter)[0];
    expect(within(first).getByText("Lil Fridge")).toBeTruthy();
    expect(within(first).getByText("10-6")).toBeTruthy();
    expect(within(first).getByText("behold the lamb")).toBeTruthy();
  });

  it("shows Must Watch and its reason first on a Must Watch card, with the brand edge", () => {
    const chapter = renderNext();
    const watch = cards(chapter).filter((card) => within(card).queryByText("Must Watch"));
    expect(watch).toHaveLength(2);
    const game = week8.next.find((item) => item.must_watch)!;
    expect(within(watch[0]).getByText(game.reason!)).toBeTruthy();
    expect(watch[0].textContent?.startsWith("Must Watch")).toBe(true);
    expect(watch.map((card) => card.getAttribute("data-must-watch"))).toEqual(["true", "true"]);
  });

  it("shows the players on bye of a side, key starters first in bold", () => {
    const chapter = renderNext();
    const card = cards(chapter)[2];
    const line = within(card).getAllByText("On bye")[1].parentElement!;
    expect(line.textContent).toBe("On bye Jaylen Warren RB · Carnell Tate WR · Pittsburgh Steelers DEF");
    expect(within(line).getByText("Jaylen Warren").tagName).toBe("STRONG");
    expect(within(line).getByText("Pittsburgh Steelers").tagName).not.toBe("STRONG");
  });

  it("shows no bye line for a side with no player on bye", () => {
    const chapter = renderNext();
    expect(within(cards(chapter)[4]).queryByText("On bye")).toBeNull();
  });
});
