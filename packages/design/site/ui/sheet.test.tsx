/**
 * Tests for the sheet wrapper of the ui-sdk Drawer. They press the trigger by its name.
 * They read the role and the name of the open sheet, not its class names.
 */
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Sheet, SheetClose, SheetContent, SheetHandle, SheetTitle, SheetTrigger } from "./sheet";

/* jsdom has no ResizeObserver, and the Drawer measures its sheet with one. This inert stand-in fills the gap; it feeds the Drawer no size. */
if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

/* jsdom has no getAnimations either. The Drawer asks for the running animations when it closes, and an empty list lets it finish. */
if (typeof Element.prototype.getAnimations !== "function") {
  Element.prototype.getAnimations = () => [];
}

afterEach(cleanup);

function renderSheet() {
  render(
    <Sheet side="top">
      <SheetTrigger>Open menu</SheetTrigger>
      <SheetContent>
        <SheetHandle aria-label="Resize" />
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

  it("closes the content on the close part", () => {
    renderSheet();
    fireEvent.click(screen.getByRole("button", { name: "Open menu" }));
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog", { name: "Site menu" })).toBeNull();
  });
});
