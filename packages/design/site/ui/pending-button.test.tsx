/**
 * Tests for the pending button, the wrapper of the ui-sdk Button.
 * They press it from the keyboard and read the attributes a reader and a screen reader get.
 */
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it } from "bun:test";
import { PendingButton } from "./pending-button";

afterEach(cleanup);

/* A press that stays open until the test calls the returned function. */
function openPress() {
  let finish = () => {};
  const press = () => new Promise<void>((resolve) => (finish = resolve));
  return { press, finish: () => finish() };
}

describe("the pending button", () => {
  it("goes pending on a press whose handler returns a Promise, and keeps its label and its focus", async () => {
    const { press, finish } = openPress();
    render(<PendingButton onClick={press}>Grade the Trade</PendingButton>);
    const button = screen.getByRole("button", { name: "Grade the Trade" });
    button.focus();
    // A keyboard tap on a native button is a click.
    fireEvent.click(button);
    await waitFor(() => expect(button.getAttribute("aria-busy")).toBe("true"));
    expect(button.hasAttribute("data-pending")).toBe(true);
    expect(button.getAttribute("aria-disabled")).toBe("true");
    expect(button.textContent).toBe("Grade the Trade");
    expect(document.activeElement).toBe(button);
    finish();
    await waitFor(() => expect(button.hasAttribute("data-pending")).toBe(false));
  });

  it("ignores a second press while it is pending", async () => {
    let presses = 0;
    const { press, finish } = openPress();
    render(
      <PendingButton
        onClick={() => {
          presses += 1;
          return press();
        }}
      >
        Grade the Trade
      </PendingButton>,
    );
    const button = screen.getByRole("button", { name: "Grade the Trade" });
    fireEvent.click(button);
    fireEvent.click(button);
    expect(presses).toBe(1);
    finish();
  });

  it("announces the pending message after a second", async () => {
    const { press } = openPress();
    render(
      <PendingButton onClick={press} pendingAnnouncement="Grading the trade">
        Grade the Trade
      </PendingButton>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Grade the Trade" }));
    expect(await screen.findByText("Grading the trade", {}, { timeout: 2500 })).toBeTruthy();
  });
});
