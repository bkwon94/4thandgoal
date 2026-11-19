/**
 * Tests for the rules of the sim Announcement on the home page, with the real week 10 file of CPC and real local storage.
 * Each render is one page load. It opens 0.7 s after load, once per browser, and never over a sheet or with no team.
 */
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import "@cpc/design/ui/sheet-jsdom";
import { standInForAnimate } from "@cpc/design/ui/sheet-drag-jsdom";
import { weekSim } from "@cpc/sim/fixtures/sim";
import { previewOf } from "@cpc/sim/announcement/preview";
import { YOUR_TEAM_KEY } from "@cpc/analyzer/lib/your-team";
import { TeamSheet } from "@/app/front-door/team-sheet";
import { LOAD_BEAT_MS } from "@/app/use-announcement";
import { SIM_ANNOUNCEMENT, SimAnnouncement } from "./announcement";

const DATA = previewOf(weekSim);
const BO_GIRDS = 6;
// A day of the week after the release, before the stop date.
const IN_THE_WEEK = new Date(`${SIM_ANNOUNCEMENT.stops}T12:00:00`).getTime() - 3 * 86_400_000;

let putBack = () => {};
beforeEach(() => {
  vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "Date"] });
  vi.setSystemTime(IN_THE_WEEK);
  putBack = standInForAnimate();
  localStorage.clear();
  window.history.replaceState(null, "", "/");
});
afterEach(() => {
  cleanup();
  putBack();
  vi.useRealTimers();
});

const title = () => screen.queryByRole("dialog", { name: "See your path to the playoffs" });

/* One page load of the home page: mount the Announcement, then let the load beat pass. Unmount it before the next load. */
function load() {
  const page = render(<SimAnnouncement data={DATA} siteName="Test League" href="/sim/2026/" />);
  act(() => vi.advanceTimersByTime(LOAD_BEAT_MS));
  return page;
}

describe("the sim Announcement on the home page", () => {
  it("opens with the copy of the spec about 0.7 s after load, with Bo Girds set (AT-51)", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    render(<SimAnnouncement data={DATA} siteName="Test League" href="/sim/2026/" />);
    act(() => vi.advanceTimersByTime(LOAD_BEAT_MS - 1));
    expect(title()).toBeNull();
    act(() => vi.advanceTimersByTime(1));
    const sheet = title()!;
    expect(sheet).toBeTruthy();
    for (const copy of ["New: Season sim", "Pick this week's results and watch your playoff odds move.", "Open the sim", "Not now"]) {
      expect(sheet.textContent).toContain(copy);
    }
    expect(sheet.textContent).toContain("The Blue Tent");
    expect(sheet.textContent).toContain("Return of T Mac");
    expect(sheet.textContent).toContain("Playoff line");
    expect(sheet.textContent).toContain("What-if: Bo Girds win both");
  });

  it("stays hidden on a reload after Not now (AT-55)", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    const first = load();
    fireEvent.click(screen.getByRole("button", { name: "Not now" }));
    act(() => vi.advanceTimersByTime(1000));
    expect(title()).toBeNull();
    first.unmount();
    load();
    expect(title()).toBeNull();
  });

  it("stays hidden on a reload after a press of Open the sim (AT-55)", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    const first = load();
    fireEvent.click(screen.getByRole("link", { name: "Open the sim" }));
    first.unmount();
    load();
    expect(title()).toBeNull();
  });

  it("does not open on the page it links to (AT-56)", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    window.history.replaceState(null, "", "/sim/2026/");
    load();
    expect(title()).toBeNull();
  });

  it("does not open over another sheet, and that skipped load does not count (AT-56, AT-57)", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    const first = render(
      <>
        <TeamSheet siteName="Test League" teams={[]} current={null} onPick={() => {}} />
        <SimAnnouncement data={DATA} siteName="Test League" href="/sim/2026/" />
      </>,
    );
    act(() => vi.advanceTimersByTime(LOAD_BEAT_MS * 3));
    expect(screen.getByRole("dialog", { name: "Which team is yours?" })).toBeTruthy();
    expect(title()).toBeNull();
    first.unmount();
    load();
    expect(title()).toBeTruthy();
  });

  it("does not open with no team set, and opens on a later load after a team is set (AT-57, AT-58)", () => {
    const first = load();
    expect(title()).toBeNull();
    first.unmount();
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    load();
    expect(title()).toBeTruthy();
  });

  it("skips the load of the team picker after a pick before the beat, and opens on the next load (AT-57)", () => {
    const first = render(<SimAnnouncement data={DATA} siteName="Test League" href="/sim/2026/" />);
    act(() => vi.advanceTimersByTime(LOAD_BEAT_MS / 2));
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    act(() => vi.advanceTimersByTime(LOAD_BEAT_MS * 3));
    expect(title()).toBeNull();
    first.unmount();
    load();
    expect(title()).toBeTruthy();
  });

  it("does not open with a kept team that is not in the sim file", () => {
    localStorage.setItem(YOUR_TEAM_KEY, "99");
    load();
    expect(title()).toBeNull();
  });

  it("does not open 1 day past its end date (AT-59)", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    vi.setSystemTime(new Date(`${SIM_ANNOUNCEMENT.stops}T12:00:00`).getTime() + 86_400_000);
    load();
    expect(title()).toBeNull();
  });

  it("stops on its end date, 1 week after the release", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    vi.setSystemTime(new Date(`${SIM_ANNOUNCEMENT.release}T00:00:00`).getTime() + 7 * 86_400_000);
    load();
    expect(title()).toBeNull();
  });

  it("opens on the last day before its end date", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    vi.setSystemTime(new Date(`${SIM_ANNOUNCEMENT.stops}T00:00:00`).getTime() - 60_000);
    load();
    expect(title()).toBeTruthy();
  });
});
