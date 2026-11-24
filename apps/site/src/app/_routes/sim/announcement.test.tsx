/**
 * Tests for the rules of The Race Announcement on the home page, with the real week 11 file of CPC and real local storage.
 * Each render is one page load. It opens 0.7 s after load, once per browser, and never over a sheet or with no team.
 */
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, jest, setSystemTime } from "bun:test";
import "@cpc/design/ui/sheet-jsdom";
import { standInForAnimate } from "@cpc/design/ui/sheet-drag-jsdom";
import { weekElevenSim } from "@cpc/sim/fixtures/sim";
import { previewOf } from "@cpc/sim/announcement/preview";
import { YOUR_TEAM_KEY } from "@cpc/analyzer/lib/your-team";
import { TeamSheet } from "@/app/front-door/team-sheet";
import { LOAD_BEAT_MS } from "@/app/use-announcement";
import { SIM_ANNOUNCEMENT, SimAnnouncement } from "./announcement";

const DATA = previewOf(weekElevenSim);
const BO_GIRDS = 6;
// A day of the week after the release, before the stop date.
const IN_THE_WEEK = new Date(`${SIM_ANNOUNCEMENT.stops}T12:00:00`).getTime() - 3 * 86_400_000;

let putBack = () => {};
beforeEach(() => {
  // Bun fakes each timer and `Date` together. It has no choice of which ones to fake.
  jest.useFakeTimers();
  setSystemTime(IN_THE_WEEK);
  putBack = standInForAnimate();
  localStorage.clear();
  window.history.replaceState(null, "", "/");
});
afterEach(() => {
  cleanup();
  putBack();
  jest.useRealTimers();
});

const title = () => screen.queryByRole("dialog", { name: "The Race is on" });

/* One page load of the home page: mount the Announcement, then let the load beat pass. Unmount it before the next load. */
function load() {
  const page = render(<SimAnnouncement data={DATA} siteName="Test League" href="/sim/2026/" />);
  act(() => jest.advanceTimersByTime(LOAD_BEAT_MS));
  return page;
}

describe("The Race Announcement on the home page", () => {
  it("opens with the copy of the spec about 0.7 s after load, with Bo Girds set (AT-49)", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    render(<SimAnnouncement data={DATA} siteName="Test League" href="/sim/2026/" />);
    act(() => jest.advanceTimersByTime(LOAD_BEAT_MS - 1));
    expect(title()).toBeNull();
    act(() => jest.advanceTimersByTime(1));
    const sheet = title()!;
    expect(sheet).toBeTruthy();
    for (const copy of [
      "New: The Race",
      "See what you need each week, and who to root for.",
      "Open The Race",
      "Not now",
    ]) {
      expect(sheet.textContent).toContain(copy);
    }
    // The art shows the League board rows around Bo Girds.
    expect(sheet.textContent).toContain("Bengals Buddies");
    expect(sheet.textContent).toContain("Omarion Himpton");
    expect(sheet.textContent).toContain("League board");
    expect(screen.getByRole("link", { name: "Open The Race" }).getAttribute("href")).toBe(
      "/sim/2026/",
    );
  });

  it("stays hidden on a reload after Not now (AT-49)", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    const first = load();
    fireEvent.click(screen.getByRole("button", { name: "Not now" }));
    act(() => jest.advanceTimersByTime(1000));
    expect(title()).toBeNull();
    first.unmount();
    load();
    expect(title()).toBeNull();
  });

  it("stays hidden on a reload after a press of Open The Race", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    const first = load();
    fireEvent.click(screen.getByRole("link", { name: "Open The Race" }));
    first.unmount();
    load();
    expect(title()).toBeNull();
  });

  it("does not open on the page it links to", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    window.history.replaceState(null, "", "/sim/2026/");
    load();
    expect(title()).toBeNull();
  });

  it("does not open over another sheet, and that skipped load does not count", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    const first = render(
      <>
        <TeamSheet siteName="Test League" teams={[]} current={null} onPick={() => {}} />
        <SimAnnouncement data={DATA} siteName="Test League" href="/sim/2026/" />
      </>,
    );
    act(() => jest.advanceTimersByTime(LOAD_BEAT_MS * 3));
    expect(screen.getByRole("dialog", { name: "Which team is yours?" })).toBeTruthy();
    expect(title()).toBeNull();
    first.unmount();
    load();
    expect(title()).toBeTruthy();
  });

  it("does not open with no team set, and opens on a later load after a team is set", () => {
    const first = load();
    expect(title()).toBeNull();
    first.unmount();
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    load();
    expect(title()).toBeTruthy();
  });

  it("skips the load of the team picker after a pick before the beat, and opens on the next load", () => {
    const first = render(<SimAnnouncement data={DATA} siteName="Test League" href="/sim/2026/" />);
    act(() => jest.advanceTimersByTime(LOAD_BEAT_MS / 2));
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    act(() => jest.advanceTimersByTime(LOAD_BEAT_MS * 3));
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

  it("does not open 1 day past its end date", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    setSystemTime(new Date(`${SIM_ANNOUNCEMENT.stops}T12:00:00`).getTime() + 86_400_000);
    load();
    expect(title()).toBeNull();
  });

  it("stops on its end date, 1 week after the release", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    setSystemTime(new Date(`${SIM_ANNOUNCEMENT.release}T00:00:00`).getTime() + 7 * 86_400_000);
    load();
    expect(title()).toBeNull();
  });

  it("opens on the last day before its end date", () => {
    localStorage.setItem(YOUR_TEAM_KEY, String(BO_GIRDS));
    setSystemTime(new Date(`${SIM_ANNOUNCEMENT.stops}T00:00:00`).getTime() - 60_000);
    load();
    expect(title()).toBeTruthy();
  });
});
