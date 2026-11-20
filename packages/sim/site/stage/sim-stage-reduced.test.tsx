/**
 * Tests for the replay of the sim page with the reduced-motion media query on: each screen still plays, no element
 * moves, and each change of place or state shows only through a fade. matchMedia is a stub, and it must exist before Framer Motion first reads it, so the stub runs at the top.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { weekSim } from "../fixtures/sim";
import { SimPage } from "../page/sim-page";
import { replaySeason } from "../replay/season";
import { Standings } from "./standings";
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

/* The opacity the reader sees: the inline opacity of the element times that of each parent. Framer Motion sets each
   fade as an inline opacity, and the reduced-motion rule of the site stops each CSS transition. */
function shownOpacity(element: Element | null): number {
  let shown = 1;
  for (let at = element; at !== null; at = at.parentElement) {
    const own = (at as HTMLElement).style?.opacity;
    if (own) shown *= Number(own);
  }
  return shown;
}

/* Moves the clock one frame at a time across `ms`, and gives the result of `read` on each frame. */
async function framesOf<T>(ms: number, read: () => T): Promise<T[]> {
  const out: T[] = [read()];
  for (let t = 0; t < ms; t += 16) {
    await act(async () => {
      vi.advanceTimersByTime(16);
    });
    out.push(read());
  }
  return out;
}

describe("each change under reduced motion is a fade", () => {
  it("shows a new order of the standings only through a fade, never at its new place at full opacity", async () => {
    const season = replaySeason({ ...weekSim, sample: [weekSim.sample[0]] }, 0);
    const orderOf = (rows: { roster_id: number }[]) => rows.map((r) => r.roster_id).join(",");
    const all = [season.start, ...season.weeks.map((w) => w.standings)];
    const at = all.findIndex((rows, i) => i > 0 && orderOf(rows) !== orderOf(all[i - 1]));
    expect(at).toBeGreaterThan(0);
    const [before, after] = [all[at - 1], all[at]];
    const props = {
      marks: null,
      week: null,
      spots: season.seeds.length,
      byes: season.byes,
      yourTeam: YOU,
      avatars: {},
      off: true,
      cut: false,
    };
    const { container, rerender } = render(<Standings rows={before} {...props} />);
    const orderShown = (list: Element) =>
      [...list.querySelectorAll("li[data-roster]")]
        .map((li) => li.getAttribute("data-roster"))
        .join(",");
    const old = orderShown(container.querySelector('ol[aria-label="Standings"]')!);
    rerender(<Standings rows={after} {...props} />);
    // Each frame: the order of each list on the stage, with the opacity it shows.
    const frames = await framesOf(1000, () =>
      [...container.querySelectorAll('ol[aria-label="Standings"]')].map((list) => ({
        order: orderShown(list),
        opacity: shownOpacity(list),
      })),
    );
    // A folded row has no li of its own, so a list in the new order is a list whose shown rows differ from the old.
    const shown = frames.flat().filter((list) => list.order !== old);
    expect(shown.length).toBeGreaterThan(0);
    // The new order first shows faint, then fades up to full.
    expect(shown[0].opacity).toBeLessThan(1);
    expect(shown.some((list) => list.opacity > 0 && list.opacity < 1)).toBe(true);
    expect(shown.at(-1)!.opacity).toBe(1);
  });

  it("swaps Skip for Done through a fade at the end, with no control that jumps to a new place", async () => {
    render(<SimPage sim={weekSim} you={YOU} random={() => 0} />);
    fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
    const skip = within(stage()).getByRole("button", { name: "Skip" });
    for (
      let i = 0;
      i < 40 && within(stage()).queryByRole("button", { name: "Skip" }) !== null;
      i += 1
    ) {
      await act(async () => {
        fireEvent.click(within(stage()).getByRole("button", { name: "Skip" }));
        vi.advanceTimersByTime(16);
      });
    }
    const frames = await framesOf(1000, () => {
      const done = within(stage()).queryByRole("button", { name: "Done" });
      return done === null ? null : { same: done === skip, opacity: shownOpacity(done) };
    });
    const shown = frames.filter((f) => f !== null);
    expect(shown.length).toBeGreaterThan(0);
    // React must not reuse the node of Skip for Done, because that node would jump to the place of Done.
    expect(shown.every((f) => !f.same)).toBe(true);
    expect(shown[0].opacity).toBeLessThan(1);
    expect(shown.at(-1)!.opacity).toBe(1);
  });

  it("fades the Playoffs tab from off to on, with no step from 0.4 to 1", async () => {
    render(<SimPage sim={weekSim} you={YOU} random={() => 0} />);
    fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
    const tab = () => within(stage()).getByRole("button", { name: "Playoffs" });
    for (let i = 0; i < 40 && tab().getAttribute("aria-current") !== "step"; i += 1) {
      await act(async () => {
        fireEvent.click(within(stage()).getByRole("button", { name: "Skip" }));
        vi.advanceTimersByTime(16);
      });
    }
    // The CSS of a disabled tab sets 0.4, and the reduced-motion rule of the site stops its transition, so the fade
    // must be an inline opacity of its own.
    const frames = await framesOf(600, () => Number(tab().style.opacity || "NaN"));
    expect(frames.some((o) => o > 0.4 && o < 1)).toBe(true);
    expect(frames.at(-1)).toBe(1);
  });
});
