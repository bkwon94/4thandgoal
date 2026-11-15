/**
 * Tests for the sheet wrapper of the ui-sdk Drawer. They press the trigger by its name.
 * They read the role and the name of the open sheet, not its class names.
 */
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Sheet, SheetClose, SheetContent, SheetHandle, SheetTitle, SheetTrigger } from "./sheet";
// The jsdom stand-ins that the Drawer needs.
import "./sheet-jsdom";

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
