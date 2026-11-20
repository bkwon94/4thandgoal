/**
 * Tests for the passphrase dialog of the analyzer. It is the shared Sheet, which the Drawer renders with a side.
 * It is a gate, so Escape leaves it open, the Drawer lifts it above the keyboard, and the field and the submit still work.
 */
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import "@cpc/design/ui/sheet-jsdom";
import { standInForAnimate } from "@cpc/design/ui/sheet-drag-jsdom";
import { PassphraseDialog } from "./passphrase-dialog";

let putBack = () => {};
beforeEach(() => {
  putBack = standInForAnimate();
});
afterEach(() => {
  cleanup();
  putBack();
});

const noop = () => {};

describe("the passphrase dialog of the analyzer", () => {
  it("renders the shared Sheet from the bottom, with no grip because it does not drag", () => {
    render(<PassphraseDialog open onSubmit={noop} />);
    expect(
      screen.getByRole("dialog", { name: "League Passphrase" }).getAttribute("data-side"),
    ).toBe("bottom");
    expect(document.querySelector('[data-slot="sheet-grip"]')).toBeNull();
  });

  it("leaves the lift above the keyboard to the Drawer, so the content keeps its height", () => {
    render(<PassphraseDialog open onSubmit={noop} />);
    const content = screen.getByRole("dialog", { name: "League Passphrase" });
    // The Drawer sets the top of the content inline, so a bottom offset would squash the content and push the field off the screen.
    expect(content.style.bottom).toBe("");
    expect(content.parentElement?.style.inset).toContain("var(--keyboard-inset");
  });

  it("shows the error line and sends the trimmed passphrase", () => {
    const sent: string[] = [];
    render(
      <PassphraseDialog
        open
        error="That passphrase is wrong."
        onSubmit={(value) => sent.push(value)}
      />,
    );
    expect(screen.getByText("That passphrase is wrong.")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Passphrase"), { target: { value: " abc " } });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));
    expect(sent).toEqual(["abc"]);
  });

  it("stays open on Escape", async () => {
    render(<PassphraseDialog open onSubmit={noop} />);
    fireEvent.keyDown(screen.getByLabelText("Passphrase"), { key: "Escape" });
    await act(async () => {});
    expect(screen.getByRole("dialog", { name: "League Passphrase" })).toBeTruthy();
  });
});
