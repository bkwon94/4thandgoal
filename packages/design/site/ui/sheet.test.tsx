/**
 * Tests for the sheet wrapper of the ui-sdk Drawer. They press the trigger by its name.
 * They read the role and the name of the open sheet, not its class names.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Sheet, SheetClose, SheetContent, SheetGrip, SheetTitle, SheetTrigger } from "./sheet";
// The jsdom stand-ins that the Drawer needs.
import "./sheet-jsdom";

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
