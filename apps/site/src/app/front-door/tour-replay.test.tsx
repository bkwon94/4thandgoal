/**
 * Tests for the replay of the Tour: the "Show the tour" row of the menu sheet and the "?" button of the top band.
 * Each test renders the page with the fixed copy of the published data of cpc, as a browser that already saw the Tour.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "bun:test";
import { stubPhone } from "../../../test/phone";
import { readFixtureSite, restoreFixtureSite } from "@/fixtures/sites";
import AnalyzePage from "@/app/_routes/analyzer/page";
import HomePage from "./door-page";
// The jsdom stand-ins of the browser APIs that the popover and the menu sheet need.
import "@cpc/design/ui/sheet-jsdom";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. */
beforeEach(() => readFixtureSite("cpc"));
afterEach(restoreFixtureSite);

/* The menu sheet closes at the desktop tier, and happy-dom has a desktop-wide window, so each test sees a phone. */
beforeEach(stubPhone);

const BO_GIRDS = "6";

/* jsdom does not match :popover-open, so its default style sheet hides each element with a popover attribute. A browser
   shows an open popover in the top layer, so this sheet shows the open Stop card, as a browser does. */
beforeEach(() => {
  const style = document.createElement("style");
  style.textContent = '[data-slot="popover-content"][data-open] { display: block !important; }';
  document.head.append(style);
  return () => style.remove();
});

beforeEach(() => {
  readFixtureSite("cpc");
  localStorage.setItem("cpc.passphrase", "cornerstone-test");
  localStorage.setItem("cpc.your-team", BO_GIRDS);
  // Each test starts as a browser that already saw the Tour, so only a replay shows it.
  localStorage.setItem("cpc.tour-seen", "1");
});

afterEach(() => {
  cleanup();
  localStorage.clear();
});

const findCard = (name: string) => screen.findByRole("dialog", { name }, { timeout: 2000 });
const queryCard = () =>
  screen.queryByRole("dialog", { name: /^(Suggestions|Ask|Your team|Menu)$/ });
const band = () => screen.getByRole("banner");

describe("the replay of the Tour", () => {
  it('shows a "Show the tour" row in the menu sheet that closes the sheet, then shows Stop 1 (AT-27)', async () => {
    render(<HomePage />);
    await screen.findByRole("group", { name: "Suggestions" });
    localStorage.removeItem("cpc.tour-seen");
    fireEvent.click(within(band()).getByRole("button", { name: "Open the menu" }));
    const sheet = screen
      .getByRole("navigation", { name: "Pages" })
      .closest<HTMLElement>('[role="dialog"]')!;
    fireEvent.click(within(sheet).getByRole("button", { name: "Show the tour" }));
    const card = await findCard("Suggestions");
    expect(within(card).getByText("1 of 4")).toBeTruthy();
    expect(screen.queryByRole("navigation", { name: "Pages" })).toBeNull();
    // A replay writes the seen key again.
    expect(localStorage.getItem("cpc.tour-seen")).toBe("1");
  });

  it("waits for the menu sheet to leave, and blurs a focused ask box, before a replay shows Stop 1 (AT-32)", async () => {
    // The page at the moment the Stop card joins it, before the card moves the focus into itself.
    let atCard: { focus: Element | null; sheet: boolean } | undefined;
    const observer = new MutationObserver(() => {
      if (atCard !== undefined || !document.querySelector("[data-tour-card]")) return;
      atCard = {
        focus: document.activeElement,
        sheet: screen.queryByRole("navigation", { name: "Pages" }) !== null,
      };
    });
    observer.observe(document.body, { subtree: true, childList: true });
    render(<HomePage />);
    await screen.findByRole("group", { name: "Suggestions" });
    fireEvent.click(within(band()).getByRole("button", { name: "Open the menu" }));
    const sheet = screen
      .getByRole("navigation", { name: "Pages" })
      .closest<HTMLElement>('[role="dialog"]')!;
    fireEvent.click(within(sheet).getByRole("button", { name: "Show the tour" }));
    // Once the sheet leaves, the reader taps the ask box before Stop 1 shows.
    const field = screen.getByRole("textbox", { name: "Ask a question" });
    await waitFor(() => {
      expect(screen.queryByRole("navigation", { name: "Pages" })).toBeNull();
      field.focus();
      expect(document.activeElement).toBe(field);
    });
    await findCard("Suggestions");
    observer.disconnect();
    const textField = (el: Element | null | undefined) =>
      !!el && el.matches("input, textarea, [contenteditable]");
    expect(atCard?.sheet).toBe(false);
    expect(textField(atCard?.focus)).toBe(false);
    expect(textField(document.activeElement)).toBe(false);
  });

  it('shows a "?" button named "Show the tour" right before the theme button, and it shows Stop 1 (AT-28)', async () => {
    render(<HomePage />);
    await screen.findByRole("group", { name: "Suggestions" });
    const replay = within(band()).getByRole("button", { name: "Show the tour" });
    // The "?" sits right before the theme button.
    expect(replay.nextElementSibling?.getAttribute("aria-label")).toMatch(
      /^Switch to (light|dark) theme$/,
    );
    fireEvent.click(replay);
    const card = await findCard("Suggestions");
    expect(within(card).getByText("1 of 4")).toBeTruthy();
  });

  it('puts focus back on the "?" button after Done (AT-31)', async () => {
    render(<HomePage />);
    await screen.findByRole("group", { name: "Suggestions" });
    const replay = within(band()).getByRole("button", { name: "Show the tour" });
    replay.focus();
    fireEvent.keyDown(replay, { key: "Enter" });
    fireEvent.click(replay);
    for (const header of ["Suggestions", "Ask", "Your team"]) {
      fireEvent.click(within(await findCard(header)).getByRole("button", { name: "Next" }));
    }
    fireEvent.click(within(await findCard("Menu")).getByRole("button", { name: "Done" }));
    await waitFor(() => expect(queryCard()).toBeNull());
    await waitFor(() => expect(document.activeElement).toBe(replay));
  });
});

describe("the other pages", () => {
  it("show no replay control in the band or the menu sheet, and set no seen key (AT-34)", () => {
    localStorage.removeItem("cpc.tour-seen");
    render(<AnalyzePage />);
    expect(within(band()).queryByRole("button", { name: "Show the tour" })).toBeNull();
    fireEvent.click(within(band()).getByRole("button", { name: "Open the menu" }));
    expect(screen.getByRole("navigation", { name: "Pages" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Show the tour" })).toBeNull();
    expect(queryCard()).toBeNull();
    expect(localStorage.getItem("cpc.tour-seen")).toBeNull();
  });
});
