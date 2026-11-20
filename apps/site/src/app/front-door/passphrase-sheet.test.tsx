/**
 * Tests for the passphrase sheet of the front door. It is the shared Sheet, so it shows the grip and drags closed.
 * The Drawer lifts its content above the keyboard, and the field keeps the focus.
 */
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useState } from "react";
import { afterEach, beforeEach, describe, expect, it } from "bun:test";
import "@cpc/design/ui/sheet-jsdom";
import { standInForAnimate } from "@cpc/design/ui/sheet-drag-jsdom";
import { PassphraseSheet } from "./passphrase-sheet";

let putBack = () => {};
beforeEach(() => {
  putBack = standInForAnimate();
});
afterEach(() => {
  cleanup();
  putBack();
});

/* A mouse drag down the sheet: press on it, move the pointer down in steps, then let go. */
function dragDown(element: Element) {
  const pointer = { pointerId: 1, pointerType: "mouse", button: 0 };
  fireEvent.pointerDown(element, { ...pointer, clientX: 100, clientY: 100 });
  for (const y of [140, 200, 280, 380]) {
    fireEvent.pointerMove(document, { ...pointer, clientX: 100, clientY: y });
  }
  fireEvent.pointerUp(document, { ...pointer, clientX: 100, clientY: 380 });
}

const noop = () => {};

describe("the passphrase sheet of the front door", () => {
  it("shows the grip of the shared Sheet and keeps the focus in the field", async () => {
    render(
      <PassphraseSheet siteName="Test league" wrong={false} onPassphrase={noop} onClose={noop} />,
    );
    expect(document.querySelector('[data-slot="sheet-grip"]')).toBeTruthy();
    await waitFor(() =>
      expect(document.activeElement).toBe(
        screen.getByLabelText("League passphrase", { selector: "input" }),
      ),
    );
  });

  it("leaves the lift above the keyboard to the Drawer, so the content keeps its height", () => {
    render(
      <PassphraseSheet siteName="Test league" wrong={false} onPassphrase={noop} onClose={noop} />,
    );
    const content = screen.getByRole("dialog", { name: "What is the league passphrase?" });
    // The Drawer sets the top of the content inline, so a bottom offset would squash the content and push the field off the screen.
    expect(content.style.bottom).toBe("");
    expect(content.parentElement?.style.inset).toContain("var(--keyboard-inset");
  });

  it("closes on Not now", () => {
    const closed: string[] = [];
    render(
      <PassphraseSheet
        siteName="Test league"
        wrong={false}
        onPassphrase={noop}
        onClose={() => closed.push("close")}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Not now" }));
    expect(closed).toEqual(["close"]);
  });

  it("closes on Escape", async () => {
    const closed: string[] = [];
    render(
      <PassphraseSheet
        siteName="Test league"
        wrong={false}
        onPassphrase={noop}
        onClose={() => closed.push("close")}
      />,
    );
    fireEvent.keyDown(screen.getByLabelText("League passphrase", { selector: "input" }), {
      key: "Escape",
    });
    await waitFor(() => expect(closed).toEqual(["close"]));
  });

  it("says the passphrase did not match, and sends the typed passphrase", () => {
    const sent: string[] = [];
    render(
      <PassphraseSheet
        siteName="Test league"
        wrong
        onPassphrase={(value) => sent.push(value)}
        onClose={noop}
      />,
    );
    expect(screen.getByText(/did not match/)).toBeTruthy();
    fireEvent.change(screen.getByLabelText("League passphrase", { selector: "input" }), {
      target: { value: " abc " },
    });
    fireEvent.click(screen.getByRole("button", { name: "Use this passphrase" }));
    expect(sent).toEqual(["abc"]);
  });

  /* The drag runs last: a click test that runs after a drag in jsdom misses its click. */
  it("closes on a drag down and calls onClose once", async () => {
    const closed: string[] = [];
    function Holder() {
      const [shown, setShown] = useState(true);
      if (!shown) return null;
      return (
        <PassphraseSheet
          siteName="Test league"
          wrong={false}
          onPassphrase={noop}
          onClose={() => {
            closed.push("close");
            setShown(false);
          }}
        />
      );
    }
    render(<Holder />);
    await act(async () => dragDown(screen.getByRole("dialog")));
    await waitFor(() => expect(closed).toEqual(["close"]));
  });
});
