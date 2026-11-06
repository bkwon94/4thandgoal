/**
 * Tests for the sim replay with the reduced-motion media query on: each beat keeps its timeline and its facts, and only fades.
 * matchMedia is a stub, and it must exist before Framer Motion first reads it, so the stub runs at the top of the file.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { sim } from "../fixtures/sim";
import { beatsOf } from "./beats";
import { replaySeason } from "./season";
import { SimReplay } from "./sim-replay";

vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      // Framer Motion asks for "(prefers-reduced-motion)" with no value, so the stub matches the feature name.
      matches: query.includes("prefers-reduced-motion"),
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList,
);

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

afterAll(() => {
  vi.unstubAllGlobals();
});

/* No element of the replay moves: no inline transform holds a translate, a scale, or a rotate. A fade sets only opacity. */
function expectNoMovement(box: HTMLElement) {
  for (const element of [box, ...box.querySelectorAll<HTMLElement>("*")]) {
    expect(element.style.transform ?? "").not.toMatch(/translate|scale|rotate/);
  }
}

describe("the sim replay with reduced motion", () => {
  it("plays each beat on the same timeline with the same facts, and moves nothing", async () => {
    render(<SimReplay sim={sim} pick={() => 0} />);
    fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
    const stage = screen.getByRole("region", { name: "The replay" });
    const beats = beatsOf(replaySeason(sim, 0));
    const seen: string[] = [];
    for (const beat of beats) {
      // A frame passes, so a part that would move has its first style.
      await act(async () => {
        vi.advanceTimersByTime(16);
      });
      expectNoMovement(stage);
      seen.push(within(stage).getByRole("status").textContent ?? "");
      await act(async () => {
        vi.advanceTimersByTime(Math.max(0, beat.ms - 16));
      });
    }
    expect(seen).toEqual([
      "Week 9 final",
      "Week 10 final",
      "Week 11 final",
      "Week 12 final",
      "Week 13 final",
      "Week 14 final",
      "Playoffs",
      "Final standings",
      "Round 1",
      "Round 1 results",
      "Semifinal",
      "Semifinal results",
      "Final",
      "Final results",
      "Lil Fridge wins the title in this run",
    ]);
    expect(within(stage).getByRole("dialog", { name: "Champion of this run" }).textContent).toContain(
      "Wins the title in 14.4% of all 10,000 runs",
    );
  });

  it("shows the scores of a week as a still list, with no crawl", () => {
    render(<SimReplay sim={sim} pick={() => 0} />);
    fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
    const third = screen.getByRole("group", { name: "Week 9 final" });
    expect(third.textContent).toContain("The Blue Tent 112.9");
    // The crawl doubles the scores for its loop. The still list holds each game once.
    expect(third.textContent!.split("The Blue Tent 112.9")).toHaveLength(2);
  });
});
