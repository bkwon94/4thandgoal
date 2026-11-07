/**
 * Tests for the egg banner of the home page, rendered from the board fixture that the API tests hold to the real answer.
 * The banner names the day of the last drop and the count left, and a hide stays until the next drop.
 */
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { EggsError, type Board } from "../lib/api";
import { board, fakeEggsApi } from "../lib/fixtures/eggs-api";
import { EggBanner, EggBannerScreen } from "./egg-banner";

afterEach(() => {
  cleanup();
  localStorage.clear();
});

/* The fixture with the drop of six eggs on Tuesday 27 October, as the API gives it, and `left` eggs left to find. */
function tuesdayDrop(left: number, droppedAt = "2026-10-27T09:30:00-04:00"): Board {
  return { ...board, counts: { ...board.counts, left }, last_drop: { week: 10, count: 6, dropped_at: droppedAt } };
}

const TUESDAY_NIGHT = new Date("2026-10-27T23:30:00-04:00");
const WEDNESDAY = new Date("2026-10-28T10:00:00-04:00");

const line = () => screen.getByRole("region", { name: "Egg drop" }).querySelector("[data-banner-line]")!.textContent;

describe("EggBanner", () => {
  it("names the drop of today on the day of the drop, then the weekday of the drop", () => {
    const { unmount } = render(<EggBanner board={tuesdayDrop(6)} href="/eggs/" now={TUESDAY_NIGHT} />);
    expect(line()).toBe("6 eggs dropped today · 6 left");
    unmount();
    render(<EggBanner board={tuesdayDrop(5)} href="/eggs/" now={WEDNESDAY} />);
    expect(line()).toBe("6 eggs dropped Tue · 5 left");
  });

  it("reads the day in the timezone of the drop, not of the browser", () => {
    // 01:30 UTC on Wednesday is still Tuesday night in New York.
    render(<EggBanner board={tuesdayDrop(6)} href="/eggs/" now={new Date("2026-10-28T01:30:00Z")} />);
    expect(line()).toBe("6 eggs dropped today · 6 left");
  });

  it("links to the egg board", () => {
    render(<EggBanner board={tuesdayDrop(6)} href="/eggs/" now={WEDNESDAY} />);
    expect(screen.getByRole("link", { name: /Egg board/ }).getAttribute("href")).toBe("/eggs/");
  });

  it("stays hidden after a hide and a reload, until the next drop", () => {
    const { unmount } = render(<EggBanner board={tuesdayDrop(6)} href="/eggs/" now={WEDNESDAY} />);
    fireEvent.click(screen.getByRole("button", { name: "Hide the banner" }));
    expect(screen.queryByRole("region", { name: "Egg drop" })).toBeNull();
    unmount();
    // A reload renders the banner again from the same drop.
    const reload = render(<EggBanner board={tuesdayDrop(6)} href="/eggs/" now={WEDNESDAY} />);
    expect(screen.queryByRole("region", { name: "Egg drop" })).toBeNull();
    reload.unmount();
    // The next drop shows the banner again.
    render(<EggBanner board={tuesdayDrop(12, "2026-11-03T09:30:00-05:00")} href="/eggs/" now={new Date("2026-11-03T12:00:00-05:00")} />);
    expect(line()).toBe("6 eggs dropped today · 12 left");
  });

  it("wraps the line and grows the strip, so a narrow phone never cuts the line", () => {
    render(<EggBanner board={tuesdayDrop(6)} href="/eggs/" now={TUESDAY_NIGHT} />);
    const strip = screen.getByRole("region", { name: "Egg drop" });
    const lineBox = strip.querySelector("[data-banner-line]")!;
    // The strip has a least height of one row, not a fixed height, so a line of two rows makes it taller.
    expect(strip.classList.contains("min-h-banner")).toBe(true);
    expect(strip.classList.contains("h-banner")).toBe(false);
    // The line has no class that cuts or hides text past the end of its box.
    const cuts = ["truncate", "text-ellipsis", "whitespace-nowrap", "overflow-hidden", "line-clamp-1"];
    expect([...lineBox.classList].filter((name) => cuts.includes(name))).toEqual([]);
  });

  it("shows nothing before the first drop", () => {
    const { container } = render(<EggBanner board={{ ...board, last_drop: null }} href="/eggs/" now={WEDNESDAY} />);
    expect(container.textContent).toBe("");
  });
});

describe("EggBannerScreen", () => {
  it("shows the banner of the last drop from the board of the API", async () => {
    render(<EggBannerScreen api={fakeEggsApi({ match: false })} href="/eggs/" />);
    expect(await screen.findByRole("region", { name: "Egg drop" })).toBeTruthy();
  });

  it("renders nothing before the first drop, while the board loads, and when the call fails", async () => {
    const before = render(<EggBannerScreen api={fakeEggsApi({ match: false }, {}, { ...board, last_drop: null })} href="/eggs/" />);
    expect(before.container.innerHTML).toBe("");
    await act(async () => {});
    expect(before.container.innerHTML).toBe("");
    before.unmount();
    const failed = render(<EggBannerScreen api={fakeEggsApi({ match: false }, { board: new EggsError(500, "Server error") })} href="/eggs/" />);
    await act(async () => {});
    expect(failed.container.innerHTML).toBe("");
  });
});
