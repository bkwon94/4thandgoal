/**
 * Tests for the replay of the sim page with the reduced-motion media query on: each screen still plays, and no element
 * moves. matchMedia is a stub, and it must exist before Framer Motion first reads it, so the stub runs at the top.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { weekSim } from "../fixtures/sim";
import { SimPage } from "../page/sim-page";
import { replaySeason } from "../replay/season";
import { stepsOf } from "./steps";

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
  // Framer Motion asks for its next frame once and waits for it, so the frame it asked for under the fake clock runs here.
  vi.advanceTimersByTime(100);
  vi.useRealTimers();
});

afterAll(() => {
  vi.unstubAllGlobals();
});

const YOU = 6;

/* No element of the replay moves: no inline transform holds a translate, a scale, or a rotate. A fade sets only opacity. */
function expectNoMovement(box: HTMLElement) {
  for (const element of [box, ...box.querySelectorAll<HTMLElement>("*")]) {
    expect(element.style.transform ?? "").not.toMatch(/translate|scale|rotate/);
  }
}

/* Moves the clock across `ms` and checks three frames: the first frame, where a part that would move has its first
   style, the middle, and the end. */
async function playChecked(ms: number, box: () => HTMLElement) {
  for (const hold of [16, Math.max(0, ms / 2 - 16), ms / 2]) {
    await act(async () => {
      vi.advanceTimersByTime(hold);
    });
    expectNoMovement(box());
  }
}

const stage = () => screen.getByRole("region", { name: "Sim replay" });

describe("the replay of the sim page with reduced motion", () => {
  it("plays Season, Playoffs, and Champion, and moves nothing", async () => {
    render(<SimPage sim={weekSim} you={YOU} random={() => 0} />);
    fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
    const steps = stepsOf(replaySeason({ ...weekSim, sample: [weekSim.sample[0]] }, 0), "season");
    const seen = new Set<string>();
    for (const step of steps) {
      seen.add(within(stage()).getByRole("button", { current: "step" }).textContent ?? "");
      await playChecked(Math.max(step.ms, 100), stage);
    }
    expect([...seen]).toEqual(["Season", "Playoffs", "Champion"]);
    expect(within(stage()).getByRole("heading", { name: "Lil Fridge" })).toBeTruthy();
  });

  it("plays Games, then Standings of week 11, and moves nothing", async () => {
    render(<SimPage sim={weekSim} you={YOU} random={() => 0} />);
    fireEvent.click(screen.getByRole("button", { name: "Sim week 11" }));
    await playChecked(700, stage);
    await playChecked(3400, stage);
    await playChecked(1000, stage);
    expect(within(stage()).getByRole("button", { current: "step" }).textContent).toBe("Standings");
    expect(within(stage()).getByRole("list", { name: "Standings" })).toBeTruthy();
  });
});
