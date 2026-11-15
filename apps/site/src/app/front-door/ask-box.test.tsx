/**
 * Tests for the ask box and the keyboard: while the ask box has the focus, the on-screen keyboard is open, so the root
 * carries data-keyboard, and it clears on blur. jsdom has no keyboard, so a real phone run checks the place above it.
 */
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AskBox } from "./ask-box";

afterEach(() => cleanup());

const field = () => screen.getByRole("textbox", { name: "Ask a question" });
const keyboardOpen = () => document.documentElement.hasAttribute("data-keyboard");

describe("AskBox and the keyboard", () => {
  it("marks no keyboard while the ask box has no focus", () => {
    render(<AskBox />);
    expect(keyboardOpen()).toBe(false);
  });

  it("marks the keyboard open while the ask box has the focus", () => {
    render(<AskBox />);
    act(() => field().focus());
    expect(keyboardOpen()).toBe(true);
  });

  it("clears the keyboard mark when the ask box loses the focus", () => {
    render(<AskBox />);
    act(() => field().focus());
    act(() => field().blur());
    expect(keyboardOpen()).toBe(false);
  });

  it("clears the keyboard mark when the ask box leaves the page with the focus", () => {
    render(<AskBox />);
    act(() => field().focus());
    cleanup();
    expect(keyboardOpen()).toBe(false);
  });

  it("keeps the focus in the ask box when a question goes", () => {
    render(<AskBox />);
    act(() => field().focus());
    fireEvent.change(field(), { target: { value: "Who should I start?" } });
    fireEvent.submit(screen.getByRole("form", { name: "Ask" }));
    expect(keyboardOpen()).toBe(true);
  });

  /* The press on Send must not take the focus from the field. A blur closes the keyboard, the foot of the Thread drops
     under the thumb, and the click lands on the page, so the first tap would send nothing (ticket 34). */
  it("keeps the focus in the ask box when the thumb presses Send", () => {
    render(<AskBox />);
    act(() => field().focus());
    fireEvent.change(field(), { target: { value: "Who should I start?" } });
    // fireEvent returns false when a handler cancels the default, here the move of the focus to the button.
    expect(fireEvent.mouseDown(screen.getByRole("button", { name: "Send" }))).toBe(false);
  });

  /* A sent question closes the keyboard, so the Answer shows. The blur comes after the submit, so the press of ticket 34
     still sends on its first tap (ticket 37). */
  it("closes the keyboard once a question goes", () => {
    const onAsk = vi.fn();
    render(<AskBox onAsk={onAsk} />);
    act(() => field().focus());
    fireEvent.change(field(), { target: { value: "Who should I start?" } });
    fireEvent.submit(screen.getByRole("form", { name: "Ask" }));
    expect(onAsk).toHaveBeenCalledWith("Who should I start?");
    expect(document.activeElement).not.toBe(field());
    expect(document.documentElement.hasAttribute("data-keyboard")).toBe(false);
  });
});
