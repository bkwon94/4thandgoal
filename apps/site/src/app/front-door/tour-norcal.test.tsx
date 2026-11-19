/**
 * Tests for the Tour on the norcal front door. The page reads the fixed copy of the published data of norcal, where Bo
 * Girds is roster 7, and the league mate picks Bo Girds on a new browser. The Stops show the same copy as on cpc.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import HomePage from "./door-page";
// The jsdom stand-ins of the browser APIs that the popover and the menu sheet need.
import "@cpc/design/ui/sheet-jsdom";

/* The readers of public/ read the fixed copy of the norcal data, so a weekly publish never changes these tests. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("norcal"));

/* The copy of the Stops, word for word from the table of the PRD (decision 03). */
const COPY = [
  { header: "Suggestions", line: "Picks for your team right now. Tap one to open it, or tap More for the full list." },
  { header: "Ask", line: "Type any question about your team or your league, such as start or sit, a trade, or the playoff race." },
  { header: "Your team", line: "Tap to see the league as another manager." },
  { header: "Menu", line: "Every page of the league lives here." },
];

/* jsdom does not match :popover-open, so this sheet shows the open Stop card, as a browser does. */
beforeEach(() => {
  const style = document.createElement("style");
  style.textContent = '[data-slot="popover-content"][data-open] { display: block !important; }';
  document.head.append(style);
  return () => style.remove();
});

beforeEach(() => {
  readFixtureSite("norcal");
  localStorage.setItem("cpc.passphrase", "cornerstone-test");
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("the Tour of the norcal front door", () => {
  it("shows the same four Stops, copy, and counts after the pick of Bo Girds on a new browser (AT-6)", async () => {
    render(<HomePage />);
    const sheet = await screen.findByRole("dialog", { name: "Which team is yours?" });
    fireEvent.click(within(sheet).getByRole("button", { name: /Bo Girds/ }));
    for (const [index, stop] of COPY.entries()) {
      const card = await screen.findByRole("dialog", { name: stop.header }, { timeout: 2000 });
      expect(within(card).getByText(stop.line)).toBeTruthy();
      expect(within(card).getByText(`${index + 1} of 4`)).toBeTruthy();
      fireEvent.click(within(card).getByRole("button", { name: index === COPY.length - 1 ? "Done" : "Next" }));
    }
    await waitFor(() => expect(screen.queryByRole("dialog", { name: /^(Suggestions|Ask|Your team|Menu)$/ })).toBeNull());
    // Bo Girds is roster 7 in norcal, so the pick came from the norcal teams.
    expect(localStorage.getItem("cpc.your-team")).toBe("7");
  });
});
