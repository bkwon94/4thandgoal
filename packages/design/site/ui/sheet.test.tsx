/**
 * Tests for the sheet wrapper of the ui-sdk Drawer. They press the trigger by its name.
 * They read the role and the name of the open sheet, not its class names. The drag test reads the one class of the bleed,
 * because jsdom lays out no box and no pseudo-element.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Sheet, SheetClose, SheetContent, SheetGrip, SheetTitle, SheetTrigger } from "./sheet";
// The jsdom stand-ins that the Drawer needs.
import "./sheet-jsdom";
import { standInForAnimate } from "./sheet-drag-jsdom";

afterEach(cleanup);

function renderSheet() {
  render(
    <Sheet side="top">
      <SheetTrigger>Open menu</SheetTrigger>
      <SheetContent>
        <SheetGrip />
        <SheetTitle>Site menu</SheetTitle>
        <SheetClose>Close</SheetClose>
      </SheetContent>
    </Sheet>,
  );
}

describe("the sheet", () => {
  it("shows no content before the trigger opens it", () => {
    renderSheet();
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("opens the content on the trigger, and the title names it", () => {
    renderSheet();
    fireEvent.click(screen.getByRole("button", { name: "Open menu" }));
    expect(screen.getByRole("dialog", { name: "Site menu" })).toBeTruthy();
  });

  it("keeps the grip out of the accessibility tree, so the open sheet holds only the close button", () => {
    renderSheet();
    fireEvent.click(screen.getByRole("button", { name: "Open menu" }));
    const dialog = screen.getByRole("dialog", { name: "Site menu" });
    expect(within(dialog).getAllByRole("button").map((button) => button.textContent)).toEqual(["Close"]);
    expect(dialog.querySelector('[data-slot="sheet-grip"]')?.getAttribute("aria-hidden")).toBe("true");
  });

  it("closes the content on the close part", () => {
    renderSheet();
    fireEvent.click(screen.getByRole("button", { name: "Open menu" }));
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog", { name: "Site menu" })).toBeNull();
  });
});

/* jsdom gives each box a height of 0, so the Drawer would see a sheet with no size. This gives the open sheet a height of
   400 px for one test, and the returned function puts jsdom back. */
function standInForHeight(height: number): () => void {
  const before = Object.getOwnPropertyDescriptor(HTMLElement.prototype, "offsetHeight");
  Object.defineProperty(HTMLElement.prototype, "offsetHeight", { configurable: true, get: () => height });
  return () => {
    if (before) Object.defineProperty(HTMLElement.prototype, "offsetHeight", before);
  };
}

/* The Drawer writes the place of the sheet as an inline translate, such as "0 -22.55px". */
function translateY(sheet: HTMLElement): number {
  return Number.parseFloat(sheet.style.translate.split(" ")[1] ?? "0");
}

/* The bleed is the pseudo-element past the anchored edge of the sheet. jsdom cannot measure it, so this reads its height
   from its one class, in rem of 16 px. */
function bleedHeight(sheet: HTMLElement): number {
  const match = sheet.className.match(/after:h-\[(\d+(?:\.\d+)?)rem\]/);
  return match ? Number(match[1]) * 16 : 0;
}

/* A mouse drag on the grip, from one y to another, in steps. It returns the place of the sheet before the pointer lets go. */
async function dragGrip(sheet: HTMLElement, from: number, to: number): Promise<number> {
  const grip = sheet.querySelector('[data-slot="sheet-grip"]')!;
  const pointer = { pointerId: 1, pointerType: "mouse", button: 0 };
  fireEvent.pointerDown(grip, { ...pointer, clientX: 100, clientY: from });
  for (let step = 1; step <= 4; step++) {
    fireEvent.pointerMove(document, { ...pointer, clientX: 100, clientY: from + ((to - from) * step) / 4 });
    // The Drawer writes the translate on the next frame.
    await act(async () => new Promise((resolve) => setTimeout(resolve, 20)));
  }
  const shift = translateY(sheet);
  fireEvent.pointerUp(document, { ...pointer, clientX: 100, clientY: to });
  return shift;
}

describe("the drag of the sheet past its open height", () => {
  it.each([
    { side: "bottom" as const, from: 300, to: 100 },
    { side: "top" as const, from: 100, to: 300 },
  ])("keeps the anchored edge of a $side sheet on the edge of the viewport, within 1 px", async ({ side, from, to }) => {
    const putBackAnimate = standInForAnimate();
    const putBackHeight = standInForHeight(400);
    try {
      render(
        <Sheet side={side} defaultOpen>
          <SheetContent>
            <SheetGrip />
            <SheetTitle>Trade Wire</SheetTitle>
          </SheetContent>
        </Sheet>,
      );
      const sheet = screen.getByRole("dialog", { name: "Trade Wire" });
      const shift = await dragGrip(sheet, from, to);
      // The sheet still stretches a little past its open height, so the drag feels like a rubber band, not a wall.
      expect(Math.abs(shift)).toBeGreaterThan(0);
      // The surface of the sheet is the box plus its bleed. Its anchored edge moves by the shift, and the bleed covers it.
      const gap = Math.max(0, Math.abs(shift) - bleedHeight(sheet));
      expect(gap).toBeLessThanOrEqual(1);
    } finally {
      putBackHeight();
      putBackAnimate();
    }
  });
});
