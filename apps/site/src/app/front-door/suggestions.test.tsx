/**
 * Tests for the Suggestion chips of the dock: quiet placeholder chips hold the place of the chips until the browser
 * reads the day, so the dock never jumps when the chips land. A chip shows only its Topic name: a first tap shows its
 * fact in the strip, and a second tap opens the Topic (decision 02). A press keeps the focus in the ask box (ticket 37).
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Suggestions } from "./suggestions";

afterEach(() => cleanup());

const props = { facts: {}, moreOpen: false, onMore: () => {}, onPick: () => {} };

const FACTS = { week_recap: "You scored 80.11, 12th of 12", power_rankings: "6th, down 5" };

describe("Suggestions", () => {
  it("shows each chip with only its Topic name, in one row with More first (AT-42)", () => {
    render(<Suggestions picks={["week_recap", "power_rankings"]} {...props} facts={FACTS} />);
    const group = screen.getByRole("group", { name: "Suggestions" });
    expect(group.className).toContain("flex-nowrap");
    expect(group.className).not.toContain("flex-wrap");
    const [more, ...chips] = within(group).getAllByRole("button");
    expect(more.textContent).toBe("More");
    expect(chips.map((chip) => chip.textContent)).toEqual(["Week recap", "Power rankings"]);
    // A screen reader still hears the fact with the name.
    expect(chips[0].getAttribute("aria-label")).toBe("Week recap: You scored 80.11, 12th of 12");
  });

  it("shows the whole fact and Open on the first tap, and opens the Topic on the second tap (AT-43)", () => {
    const onPick = vi.fn();
    render(<Suggestions picks={["week_recap", "power_rankings"]} {...props} facts={FACTS} onPick={onPick} />);
    expect(screen.queryByRole("button", { name: "Open Week recap" })).toBeNull();
    const chip = screen.getByRole("button", { name: /^Week recap/ });
    fireEvent.click(chip);
    expect(onPick).not.toHaveBeenCalled();
    expect(chip.getAttribute("aria-expanded")).toBe("true");
    const strip = screen.getByRole("button", { name: "Open Week recap" });
    expect(strip.textContent).toContain("You scored 80.11, 12th of 12");
    expect(strip.textContent).toContain("Open →");
    expect(chip.getAttribute("aria-controls")).toBe(strip.closest("[id]")!.id);
    fireEvent.click(chip);
    expect(onPick).toHaveBeenCalledWith("week_recap");
  });

  it("opens the Topic on a tap on the strip", () => {
    const onPick = vi.fn();
    render(<Suggestions picks={["week_recap"]} {...props} facts={FACTS} onPick={onPick} />);
    fireEvent.click(screen.getByRole("button", { name: /^Week recap/ }));
    fireEvent.click(screen.getByRole("button", { name: "Open Week recap" }));
    expect(onPick).toHaveBeenCalledExactlyOnceWith("week_recap");
  });

  it("moves the strip to the fact of another chip on its tap, and opens no Topic (AT-44)", async () => {
    const onPick = vi.fn();
    render(<Suggestions picks={["week_recap", "power_rankings"]} {...props} facts={FACTS} onPick={onPick} />);
    fireEvent.click(screen.getByRole("button", { name: /^Week recap/ }));
    const rankings = screen.getByRole("button", { name: /^Power rankings/ });
    fireEvent.click(rankings);
    expect(onPick).not.toHaveBeenCalled();
    expect(rankings.getAttribute("aria-expanded")).toBe("true");
    expect(screen.getByRole("button", { name: /^Week recap/ }).getAttribute("aria-expanded")).toBe("false");
    const strip = screen.getByRole("button", { name: "Open Power rankings" });
    await waitFor(() => expect(strip.textContent).not.toContain("You scored"));
    expect(strip.textContent).toContain("6th, down 5");
  });

  it("closes the strip when More opens", async () => {
    const { rerender } = render(<Suggestions picks={["week_recap"]} {...props} facts={FACTS} />);
    fireEvent.click(screen.getByRole("button", { name: /^Week recap/ }));
    expect(screen.getByRole("button", { name: "Open Week recap" })).toBeTruthy();
    rerender(<Suggestions picks={["week_recap"]} {...props} facts={FACTS} moreOpen />);
    // The strip fades out on --duration-quick, then leaves.
    await waitFor(() => expect(screen.queryByRole("button", { name: "Open Week recap" })).toBeNull());
  });

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

  it("closes the keyboard after a row of More or the second tap on a chip acts", () => {
    const onPick = vi.fn();
    const { rerender } = render(
      <>
        <input aria-label="Ask a question" />
        <Suggestions picks={["week_recap"]} {...props} moreOpen onPick={onPick} facts={{ week_recap: "You won by 12" }} />
      </>,
    );
    const field = screen.getByRole("textbox");
    field.focus();
    fireEvent.click(within(screen.getByRole("list", { name: "All Topics" })).getByRole("button", { name: /You won by 12/ }));
    expect(document.activeElement, "the field gives up the focus").not.toBe(field);
    rerender(
      <>
        <input aria-label="Ask a question" />
        <Suggestions picks={["week_recap"]} {...props} onPick={onPick} facts={{ week_recap: "You won by 12" }} />
      </>,
    );
    const chip = within(screen.getByRole("group", { name: "Suggestions" })).getByRole("button", { name: /You won by 12/ });
    field.focus();
    fireEvent.click(chip);
    // The first tap only shows the fact, so the keyboard stays open, as it does for More.
    expect(document.activeElement).toBe(field);
    fireEvent.click(chip);
    expect(document.activeElement, "the field gives up the focus").not.toBe(field);
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
