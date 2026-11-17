/**
 * Tests for the sheet of the analyzer. It is the shared Sheet, so it shows the grip and drags closed with a mouse pointer.
 * A drag down calls onClose, as the team sheet of the front door does.
 */
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useState } from "react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import "@cpc/design/ui/sheet-jsdom";
import { standInForAnimate } from "@cpc/design/ui/sheet-drag-jsdom";
import { Sheet } from "./sheet";

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

describe("the sheet of the analyzer", () => {
  it("shows the grip of the shared Sheet, the title, the body, and the footer", () => {
    render(
      <Sheet open title="Your Team" onClose={() => {}} footer={<button type="button">Done</button>}>
        <p>Body</p>
      </Sheet>,
    );
    expect(document.querySelector('[data-slot="sheet-grip"]')).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Your Team" })).toBeTruthy();
    expect(screen.getByText("Body")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Done" })).toBeTruthy();
  });

  it("closes on a drag down and calls onClose", async () => {
    const closed: string[] = [];
    /* The caller keeps the open state, as the trade form does. */
    function Holder() {
      const [open, setOpen] = useState(true);
      return (
        <Sheet
          open={open}
          title="Your Team"
          onClose={() => {
            closed.push("close");
            setOpen(false);
          }}
        >
          <p>Body</p>
        </Sheet>
      );
    }
    render(<Holder />);
    await act(async () => dragDown(screen.getByRole("dialog", { name: "Your Team" })));
    await waitFor(() => expect(closed).toEqual(["close"]));
  });
});
