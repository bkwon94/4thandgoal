/**
 * Tests for the closed analyzer page that a build after the Lock writes at /analyze/. They read what a reader sees:
 * the top band, the closed line, one link to Home, and no trade form.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "bun:test";
import { readFixtureSite } from "@/fixtures/sites";
import ClosedPage from "./closed-page";

beforeEach(() => readFixtureSite("cpc"));
afterEach(() => cleanup());

describe("the closed analyzer page (AT-3, AT-4, AT-5)", () => {
  it("shows the top band, the closed line, and one link to Home", () => {
    render(<ClosedPage />);
    expect(screen.getByRole("banner")).toBeTruthy();
    const main = screen.getByRole("main");
    expect(
      within(main).getByText("The trade deadline has passed. Trades open again next season."),
    ).toBeTruthy();
    const links = within(main).getAllByRole("link");
    expect(links).toHaveLength(1);
    expect(links[0].textContent).toBe("Home");
    expect(links[0].getAttribute("href")).toBe("/");
  });

  it("shows no trade form and no mode switch", () => {
    render(<ClosedPage />);
    expect(screen.queryByRole("group", { name: "The trade" })).toBeNull();
    expect(screen.queryByText("Grade a trade")).toBeNull();
    expect(screen.queryByRole("button", { name: /Grade the Trade/ })).toBeNull();
  });

  it("marks no item of the shell as the current page", () => {
    render(<ClosedPage />);
    expect(document.querySelector("[aria-current=page]")).toBeNull();
  });
});
