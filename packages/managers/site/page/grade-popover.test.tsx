/**
 * Tests for the grade popover of the manager hero. A click on the grade letter opens it.
 * They read the name of the trigger, the four part lines in order, the lead sentence, the close on Escape, and no trigger with no grade.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Manager } from "../schema/manager-types";
import { managers as fixture } from "../fixtures/managers";
import { ManagerHero } from "./manager-hero";

afterEach(cleanup);

/* Roster 9 of the fixture, grade B, with the joined fields of the loader. */
function manager(overrides: Partial<Manager> = {}): Manager {
  const entry = fixture.managers.find((row) => row.roster_id === 9) as Manager;
  return { ...entry, standing: 4, rank: 4, movement: 0, odds: null, odds_change: null, ...overrides };
}

/* Renders the hero, clicks the grade letter, and returns the open popover. */
async function openPopover() {
  render(<ManagerHero manager={manager()} avatar="avatars/9.jpg" teams={12} />);
  fireEvent.click(screen.getByRole("button", { name: "Grade B, how the grade reads" }));
  return screen.findByRole("dialog", { name: "How The Grade Reads" });
}

describe("Grade popover", () => {
  it("names the trigger with the letter and what it opens", () => {
    render(<ManagerHero manager={manager()} avatar="avatars/9.jpg" teams={12} />);
    const trigger = screen.getByRole("button", { name: "Grade B, how the grade reads" });
    expect(trigger.textContent).toBe("B");
    expect(trigger.getAttribute("aria-expanded")).toBe("false");
  });

  it("lists the four parts in order, each with its rank of the league, after a click", async () => {
    const popover = await openPopover();
    expect(within(popover).getAllByRole("listitem").map((line) => line.textContent)).toEqual([
      "Projection Ahead · 9th of 12",
      "Season Production · 12th of 12",
      "Trade Value · 3rd of 12",
      "Depth And Holes · 6th of 12",
    ]);
  });

  it("leads with the grade in words, before the part lines", async () => {
    const popover = await openPopover();
    const read = within(popover).getByText("Strong at QB and TE. Soft at WR. Thin at RB.");
    expect(read.compareDocumentPosition(within(popover).getByRole("list"))).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });

  it("closes on Escape and returns focus to the letter", async () => {
    const popover = await openPopover();
    fireEvent.keyDown(popover, { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "How The Grade Reads" })).toBeNull());
    const trigger = screen.getByRole("button", { name: "Grade B, how the grade reads" });
    await waitFor(() => expect(document.activeElement).toBe(trigger));
  });

  it("closes when the letter is clicked again", async () => {
    await openPopover();
    fireEvent.click(screen.getByRole("button", { name: "Grade B, how the grade reads" }));
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "How The Grade Reads" })).toBeNull());
  });

  it("does not open on hover alone", async () => {
    render(<ManagerHero manager={manager()} avatar="avatars/9.jpg" teams={12} />);
    const trigger = screen.getByRole("button", { name: "Grade B, how the grade reads" });
    fireEvent.pointerEnter(trigger);
    fireEvent.mouseEnter(trigger);
    fireEvent.mouseOver(trigger);
    await new Promise((done) => setTimeout(done, 50));
    expect(screen.queryByRole("dialog", { name: "How The Grade Reads" })).toBeNull();
  });

  it("shows a plain dash and no button with no grade", () => {
    render(<ManagerHero manager={manager({ grade: null })} avatar="avatars/9.jpg" teams={12} />);
    expect(screen.queryByRole("button")).toBeNull();
    expect(screen.getByLabelText("No grade").textContent).toBe("—");
  });
});
