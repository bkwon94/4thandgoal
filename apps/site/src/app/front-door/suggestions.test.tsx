/**
 * Tests for the Suggestion chips of the dock: quiet placeholder chips hold the place of the chips until the browser
 * reads the day, so the dock never jumps when the chips land. A tap on a chip keeps the focus in the ask box until the
 * action runs, then closes the keyboard (ticket 37).
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
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

  /* A press that takes the focus blurs the ask box. The keyboard closes, the dock moves, and the click lands on the page,
     so the first tap would do nothing (ticket 37). fireEvent returns false when a handler cancels the default. */
  it("keeps the focus in the ask box while the thumb presses a chip, More, or a row of More", () => {
    render(<Suggestions picks={["week_recap"]} {...props} moreOpen facts={{ week_recap: "You won by 12" }} />);
    const group = screen.getByRole("group", { name: "Suggestions" });
    expect(fireEvent.mouseDown(within(group).getByRole("button", { name: /You won by 12/ }))).toBe(false);
    expect(fireEvent.mouseDown(within(group).getByRole("button", { name: "More" }))).toBe(false);
    const list = screen.getByRole("list", { name: "All Topics" });
    expect(fireEvent.mouseDown(within(list).getByRole("button", { name: /You won by 12/ }))).toBe(false);
  });

  it("closes the keyboard after a chip or a row of More acts", () => {
    const onPick = vi.fn();
    render(
      <>
        <input aria-label="Ask a question" />
        <Suggestions picks={["week_recap"]} {...props} moreOpen onPick={onPick} facts={{ week_recap: "You won by 12" }} />
      </>,
    );
    const field = screen.getByRole("textbox");
    for (const button of screen.getAllByRole("button", { name: /You won by 12/ })) {
      field.focus();
      fireEvent.click(button);
      expect(document.activeElement, "the field gives up the focus").not.toBe(field);
    }
    expect(onPick).toHaveBeenCalledTimes(2);
  });

  it("keeps the keyboard open after More acts", () => {
    render(
      <>
        <input aria-label="Ask a question" />
        <Suggestions picks={["week_recap"]} {...props} facts={{ week_recap: "You won by 12" }} />
      </>,
    );
    const field = screen.getByRole("textbox");
    field.focus();
    fireEvent.click(screen.getByRole("button", { name: "More" }));
    expect(document.activeElement).toBe(field);
  });
});
