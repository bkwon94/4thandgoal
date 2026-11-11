/**
 * Tests for the Suggestion chips of the dock: quiet placeholder chips hold the place of the chips until the browser
 * reads the day, so the dock never jumps when the chips land.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Suggestions } from "./suggestions";

afterEach(() => cleanup());

const props = { facts: {}, moreOpen: false, wrap: true, onMore: () => {}, onPick: () => {} };

describe("Suggestions", () => {
  it("shows 3 quiet placeholder chips, hidden from a screen reader, while the picks are not in", () => {
    render(<Suggestions picks={null} {...props} />);
    const group = screen.getByRole("group", { name: "Suggestions" });
    expect(within(group).getByRole("button", { name: "More" })).toBeTruthy();
    const holders = group.querySelectorAll("[data-placeholder]");
    expect(holders).toHaveLength(3);
    for (const holder of holders) expect(holder.closest("[aria-hidden]")).not.toBeNull();
    expect(group.getAttribute("aria-busy")).toBe("true");
  });

  it("shows no placeholder once the picks land", () => {
    render(<Suggestions picks={["week_recap"]} {...props} facts={{ week_recap: "You won by 12" }} />);
    const group = screen.getByRole("group", { name: "Suggestions" });
    expect(group.querySelectorAll("[data-placeholder]")).toHaveLength(0);
    expect(group.getAttribute("aria-busy")).toBeNull();
  });
});
