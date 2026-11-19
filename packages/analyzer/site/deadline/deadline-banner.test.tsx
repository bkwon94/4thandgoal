/**
 * Tests of the Deadline banner: its text in each phase, its tick, its one button, and the sheet it opens.
 * The clock is a fixed test input, and the Lock is the real Lock of CPC. Each expected text comes from the spec.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
// The jsdom stand-ins that the Drawer of the sheet needs.
import "@cpc/design/ui/sheet-jsdom";
import { DeadlineBanner } from "./deadline-banner";

const LOCK = Date.parse("2026-11-24T00:00:00-05:00");

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

/* The banner at the time `iso`, after its first tick. */
function bannerAt(iso: string) {
  vi.useFakeTimers({ toFake: ["Date", "setInterval", "clearInterval"] });
  vi.setSystemTime(new Date(iso));
  const view = render(<DeadlineBanner lock={LOCK} />);
  act(() => vi.advanceTimersByTime(0));
  return view;
}

const trigger = () => screen.getByRole("button", { name: /^Open the Trade Wire/ });

describe("the Deadline banner", () => {
  it("is one button that shows the trade deadline over the countdown (AT-1)", () => {
    bannerAt("2026-11-21T09:55:00-05:00");
    expect(screen.getByRole("button", { name: "Open the Trade Wire" })).toBeTruthy();
    expect(trigger().textContent).toContain("Trade deadline");
    expect(trigger().textContent).toContain("~2d 14h 05m");
    expect(trigger().closest("[data-deadline-banner]")?.getAttribute("data-phase")).toBe("open");
  });

  it("ticks one minute on when the clock moves on 60 s (AT-2)", () => {
    bannerAt("2026-11-21T09:55:00-05:00");
    act(() => vi.advanceTimersByTime(60_000));
    expect(trigger().textContent).toContain("~2d 14h 04m");
  });

  it("shows the seconds in the last hours (AT-3)", () => {
    bannerAt("2026-11-23T21:18:50-05:00");
    expect(trigger().textContent).toContain("~2h 41m 10s");
    expect(trigger().closest("[data-deadline-banner]")?.getAttribute("data-phase")).toBe("last-hours");
  });

  it("says the trade deadline has passed, with the badge Final, after the Lock (AT-9)", () => {
    bannerAt("2026-11-24T00:00:01-05:00");
    const button = screen.getByRole("button", { name: "Open the Trade Wire, final. The trade deadline has passed." });
    expect(button.textContent).toContain("The trade deadline has passed. Good luck in the playoffs.");
    expect(button.textContent).toContain("Final");
    expect(button.textContent).not.toContain("Trade deadline~");
  });

  it("goes away one day after the Lock (AT-10)", () => {
    bannerAt("2026-11-25T00:00:01-05:00");
    expect(screen.queryByRole("button")).toBeNull();
    expect(document.querySelector("[data-deadline-banner]")).toBeNull();
  });

  it("opens the shared sheet with the eyebrow, the title Trade Wire, and the empty line", () => {
    bannerAt("2026-11-21T09:55:00-05:00");
    fireEvent.click(trigger());
    const sheet = screen.getByRole("dialog", { name: "Trade Wire" });
    expect(within(sheet).getByText("Trade deadline ~2d 14h 05m")).toBeTruthy();
    expect(within(sheet).getByText("No trades yet this week.")).toBeTruthy();
  });

  it("shows the closed empty line in the sheet after the Lock", () => {
    bannerAt("2026-11-24T00:00:01-05:00");
    fireEvent.click(trigger());
    const sheet = screen.getByRole("dialog", { name: "Trade Wire" });
    expect(within(sheet).getByText("No trades this week.")).toBeTruthy();
  });

  it("never says Lock or that rosters are locked", () => {
    for (const iso of ["2026-11-21T09:55:00-05:00", "2026-11-23T21:18:50-05:00", "2026-11-24T00:00:01-05:00"]) {
      const view = bannerAt(iso);
      fireEvent.click(trigger());
      expect(document.body.textContent).not.toMatch(/\block/i);
      view.unmount();
      vi.useRealTimers();
    }
  });
});
