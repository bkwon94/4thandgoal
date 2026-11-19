/**
 * Tests for the Tour of the front door. Each test renders the page with the fixed copy of the published data of cpc,
 * with Bo Girds as Your team, and reads what a league mate sees: the Stop card, its copy, its count, and the seen key.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import HomePage from "./door-page";
import { STOPS, dismissStep } from "./tour";
// The jsdom stand-ins of the browser APIs that the popover and the menu sheet need.
import "@cpc/design/ui/sheet-jsdom";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));

const BO_GIRDS = "6";

/* The copy of the Stops, word for word from the table of the PRD (decision 03). */
const COPY = [
  { header: "Suggestions", line: "Picks for your team right now. Tap one to open it, or tap More for the full list." },
  { header: "Ask", line: "Type any question about your team or your league, such as start or sit, a trade, or the playoff race." },
  { header: "Your team", line: "Tap to see the league as another manager." },
  { header: "Menu", line: "Every page of the league lives here." },
];

/* jsdom does not match :popover-open, so its default style sheet hides each element with a popover attribute, open or
   not. A browser shows an open popover in the top layer, so this sheet shows the open Stop card, as a browser does. */
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
  // Each test starts as a browser that never saw the Tour.
  localStorage.removeItem("cpc.tour-seen");
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
});

const findCard = (name: string) => screen.findByRole("dialog", { name }, { timeout: 2000 });
const queryCard = () => screen.queryByRole("dialog", { name: /^(Suggestions|Ask|Your team|Menu)$/ });
const button = (card: HTMLElement, name: string) => within(card).getByRole("button", { name });
const queryButton = (card: HTMLElement, name: string) => within(card).queryByRole("button", { name });

describe("the Tour of the front door", () => {
  it("shows Stop 1 on load to a browser with Your team and no seen key, with no team sheet (AT-2)", async () => {
    render(<HomePage />);
    const card = await findCard("Suggestions");
    expect(within(card).getByText("1 of 4")).toBeTruthy();
    expect(screen.queryByRole("dialog", { name: "Which team is yours?" })).toBeNull();
  });

  it("is a modal dialog named by its header and described by its line (AT-29, AT-39)", async () => {
    render(<HomePage />);
    const card = await findCard("Suggestions");
    expect(card.getAttribute("aria-modal")).toBe("true");
    const described = (card.getAttribute("aria-describedby") ?? "").split(" ").map((id) => document.getElementById(id)?.textContent);
    expect(described).toContain(COPY[0].line);
  });

  it("writes \"1\" to the seen key when Stop 1 opens (AT-23)", async () => {
    render(<HomePage />);
    await findCard("Suggestions");
    expect(localStorage.getItem("cpc.tour-seen")).toBe("1");
  });

  it("shows the copy, the count, and four dots of each Stop as Next goes through them, then Done ends it (AT-3, AT-7, AT-12)", async () => {
    render(<HomePage />);
    for (const [index, stop] of COPY.entries()) {
      const card = await findCard(stop.header);
      expect(within(card).getByText(stop.line)).toBeTruthy();
      expect(within(card).getByText(`${index + 1} of 4`)).toBeTruthy();
      const dots = card.querySelectorAll("[data-tour-dot]");
      expect(dots).toHaveLength(4);
      expect([...dots].map((dot) => dot.hasAttribute("data-current"))).toEqual([0, 1, 2, 3].map((at) => at === index));
      expect(button(card, "Skip")).toBeTruthy();
      const last = index === COPY.length - 1;
      expect(queryButton(card, "Next") === null).toBe(last);
      expect(queryButton(card, "Done") !== null).toBe(last);
      fireEvent.click(button(card, last ? "Done" : "Next"));
    }
    await waitFor(() => expect(queryCard()).toBeNull());
    expect(document.querySelector("[data-tour-hole]")).toBeNull();
  });

  it("ends on Skip (AT-9)", async () => {
    render(<HomePage />);
    fireEvent.click(button(await findCard("Suggestions"), "Next"));
    fireEvent.click(button(await findCard("Ask"), "Skip"));
    await waitFor(() => expect(queryCard()).toBeNull());
    expect(document.querySelector("[data-tour-hole]")).toBeNull();
  });

  it("ends on the Escape key (AT-10)", async () => {
    render(<HomePage />);
    fireEvent.click(button(await findCard("Suggestions"), "Next"));
    const card = await findCard("Ask");
    fireEvent.keyDown(card, { key: "Escape" });
    await waitFor(() => expect(queryCard()).toBeNull());
  });

  it("goes to the next Stop on a press outside the card (AT-8)", async () => {
    render(<HomePage />);
    await findCard("Suggestions");
    await act(async () => {
      fireEvent.pointerDown(document.body, { button: 0, pointerType: "mouse" });
      fireEvent.pointerUp(document.body, { button: 0, pointerType: "mouse" });
      fireEvent.click(document.body);
    });
    await findCard("Ask");
  });

  it("shows no Tour to a browser with the seen key (AT-24, AT-25)", async () => {
    localStorage.setItem("cpc.tour-seen", "1");
    render(<HomePage />);
    await screen.findByRole("group", { name: "Suggestions" });
    await new Promise((done) => setTimeout(done, 1000));
    expect(queryCard()).toBeNull();
  });

  it("shows no Tour when the read of the seen key throws, and the Suggestions still render (AT-26)", async () => {
    const read = Storage.prototype.getItem;
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(function (this: Storage, key: string) {
      if (key === "cpc.tour-seen") throw new Error("SecurityError");
      return read.call(this, key);
    });
    render(<HomePage />);
    await screen.findByRole("group", { name: "Suggestions" });
    await new Promise((done) => setTimeout(done, 1000));
    expect(queryCard()).toBeNull();
  });

  it("aims Stop 4 at the menu button when the pill bar is hidden, and at the pill bar when the menu button is hidden (AT-4)", async () => {
    for (const hidden of ["nav", "button"] as const) {
      render(<HomePage />);
      const banner = screen.getByRole("banner");
      const menuButton = within(banner).getByRole("button", { name: "Open the menu" });
      const pillBar = within(banner).getByRole("navigation", { name: "Site menu" });
      // The site hides one of the two with a class at each width. jsdom has no style sheet, so the test hides one inline.
      (hidden === "nav" ? pillBar : menuButton).style.display = "none";
      for (const header of ["Suggestions", "Ask", "Your team"]) {
        fireEvent.click(button(await findCard(header), "Next"));
      }
      await findCard("Menu");
      expect((hidden === "nav" ? menuButton : pillBar).hasAttribute("data-tour-target")).toBe(true);
      expect((hidden === "nav" ? pillBar : menuButton).hasAttribute("data-tour-target")).toBe(false);
      cleanup();
      localStorage.removeItem("cpc.tour-seen");
    }
  });

  it("puts no stable id on the dim or the card, so a hold in the Tour sends no egg check (AT-33)", async () => {
    render(<HomePage />);
    const card = await findCard("Suggestions");
    const hole = document.querySelector("[data-tour-hole]")!;
    expect(hole).toBeTruthy();
    for (const part of [hole, card]) {
      expect(part.closest("[data-stable-id]")).toBeNull();
      expect(part.querySelector("[data-stable-id]")).toBeNull();
    }
  });
});

describe("the Stops of the Tour", () => {
  it("aim at the Suggestions, the ask box, the team switch, and the menu button or the pill bar, by their names", () => {
    expect(STOPS.map((stop) => stop.selector)).toEqual([
      '[role="group"][aria-label="Suggestions"]',
      'form[aria-label="Ask"]',
      'button[aria-label^="Your team:"]',
      'button[aria-label="Open the menu"], nav[aria-label="Site menu"]',
    ]);
    expect(STOPS.map(({ header, line }) => ({ header, line }))).toEqual(COPY);
  });

  it("maps each refused dismiss: a press outside goes on, or ends at Stop 4, and Escape and Back count as Skip (AT-8, AT-10, AT-11)", () => {
    expect(dismissStep("outside-press", false)).toBe("next");
    expect(dismissStep("outside-press", true)).toBe("end");
    expect(dismissStep("escape-key", false)).toBe("end");
    expect(dismissStep("back", false)).toBe("end");
  });
});
