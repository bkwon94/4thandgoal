/**
 * Tests for the claim sheet of the egg hunt. It is the shared Sheet, so it shows the grip and drags closed with a mouse pointer.
 * A drag down calls onClose, as the team sheet of the front door does.
 */
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useState } from "react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import "@cpc/design/ui/sheet-jsdom";
import { standInForAnimate } from "@cpc/design/ui/sheet-drag-jsdom";
import { fakeEggsApi } from "../lib/fixtures/eggs-api";
import { ClaimSheet } from "./claim-sheet";

let putBack = () => {};
beforeEach(() => {
  localStorage.clear();
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

describe("the claim sheet of the egg hunt", () => {
  it("shows the grip of the shared Sheet and the team pills", async () => {
    const api = fakeEggsApi({ match: false });
    render(
      <ClaimSheet
        api={api}
        letter="C"
        token="t1"
        onClaimed={noop}
        onClaimedFirst={noop}
        onClose={noop}
      />,
    );
    expect(document.querySelector('[data-slot="sheet-grip"]')).toBeTruthy();
    expect(await screen.findByRole("button", { name: "Lil Fridge" })).toBeTruthy();
  });

  it("closes on a drag down and calls onClose once", async () => {
    const closed: string[] = [];
    const api = fakeEggsApi({ match: false });
    /* The caller keeps the sheet on screen until it closes, as the hunt does. */
    function Holder() {
      const [shown, setShown] = useState(true);
      if (!shown) return null;
      return (
        <ClaimSheet
          api={api}
          letter="C"
          token="t1"
          onClaimed={noop}
          onClaimedFirst={noop}
          onClose={() => {
            closed.push("close");
            setShown(false);
          }}
        />
      );
    }
    render(<Holder />);
    await act(async () => dragDown(await screen.findByRole("dialog")));
    await waitFor(() => expect(closed).toEqual(["close"]));
  });
});
