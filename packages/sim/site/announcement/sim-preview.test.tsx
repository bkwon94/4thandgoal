/**
 * Tests for the art of the sim Announcement on the real week 10 files of CPC and NorCal: three standings rows around
 * Your team with the playoff line, the odds, and the What-if chip that a tap turns on and off (AT-51 to AT-53).
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { norcalWeekSim, weekSim } from "../fixtures/sim";
import { previewOf } from "./preview";
import { AUTO_WHAT_IF_MS, SimPreview } from "./sim-preview";

beforeEach(() => {
  vi.useFakeTimers();
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

const BO_GIRDS_CPC = 6;
const BO_GIRDS_NORCAL = 7;

const rows = () => within(screen.getByRole("list", { name: "Standings near your team" })).getAllByRole("listitem");
const rowNames = () => rows().map((row) => row.querySelector("[data-team]")?.textContent);
const chip = () => screen.getByRole("button", { name: /^What-if:/ });
// The live line names the odds that the count lands on, so the test reads the number, not a frame of the count.
const odds = () => screen.getByRole("status").textContent;

describe("the art of the sim Announcement", () => {
  it("takes a data shape of under 2 KB from the week sim file, so the home page does not ship the file", () => {
    expect(JSON.stringify(previewOf(weekSim)).length).toBeLessThan(2000);
  });

  it("shows The Blue Tent, Bo Girds, and Return of T Mac, with the playoff line under Bo Girds, in CPC (AT-51)", () => {
    render(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS_CPC} settled={false} />);
    expect(rowNames()).toEqual(["The Blue Tent", "Bo Girds", "Return of T Mac"]);
    // The odds of Your team count up on the screen, so the live line gives its number below.
    expect(rows()[0].textContent).toBe("5The Blue Tent81%");
    expect(rows()[1].textContent).toMatch(/^6Bo Girds\d+%Playoff line$/);
    expect(rows()[2].textContent).toBe("7Return of T Mac39%");
    expect(screen.getByText("Your team").nextSibling?.textContent).toBe("Bo Girds");
    expect(odds()).toBe("Playoff odds 58%");
  });

  it("shows the chip of a win and a median win in a league with the median game", () => {
    render(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS_CPC} settled={false} />);
    expect(chip().textContent).toContain("What-if: Bo Girds win both");
    expect(chip().getAttribute("aria-pressed")).toBe("false");
  });

  it("shows the chip of one win, and the playoff line above Bo Girds, in NorCal with no median game", () => {
    render(<SimPreview data={previewOf(norcalWeekSim)} you={BO_GIRDS_NORCAL} settled={false} />);
    expect(rowNames()).toEqual(["Breece Mode", "Bo Girds", "kaiedmonds"]);
    expect(rows()[0].textContent).toContain("Playoff line");
    expect(chip().textContent).toContain("What-if: Bo Girds win");
    expect(chip().textContent).not.toContain("both");
  });

  it("shows the first three rows for the team in first place", () => {
    render(<SimPreview data={previewOf(weekSim)} you={3} settled={false} />);
    expect(rowNames()).toEqual(["Lil Fridge", "All You Need Is Love", "Puka Deez..."]);
  });

  it("turns the chip off and on with a tap, and the odds go to the odds of the week and back (AT-52)", () => {
    render(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS_CPC} settled={false} />);
    fireEvent.click(chip());
    expect(chip().getAttribute("aria-pressed")).toBe("true");
    expect(odds()).toBe("Playoff odds 86%");
    fireEvent.click(chip());
    expect(chip().getAttribute("aria-pressed")).toBe("false");
    expect(odds()).toBe("Playoff odds 58%");
  });

  it("turns the chip on by itself once, only after the sheet settles (AT-53)", () => {
    const { rerender } = render(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS_CPC} settled={false} />);
    act(() => vi.advanceTimersByTime(5000));
    expect(chip().getAttribute("aria-pressed")).toBe("false");

    rerender(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS_CPC} settled />);
    act(() => vi.advanceTimersByTime(AUTO_WHAT_IF_MS - 1));
    expect(chip().getAttribute("aria-pressed")).toBe("false");
    act(() => vi.advanceTimersByTime(1));
    expect(chip().getAttribute("aria-pressed")).toBe("true");
    expect(odds()).toBe("Playoff odds 86%");

    // A tap turns it off, and it never turns on by itself again.
    fireEvent.click(chip());
    act(() => vi.advanceTimersByTime(5000));
    expect(chip().getAttribute("aria-pressed")).toBe("false");
  });

  it("leaves the chip alone when the manager taps it before the automatic turn", () => {
    const { rerender } = render(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS_CPC} settled />);
    fireEvent.click(chip());
    fireEvent.click(chip());
    rerender(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS_CPC} settled />);
    act(() => vi.advanceTimersByTime(5000));
    expect(chip().getAttribute("aria-pressed")).toBe("false");
  });
});
