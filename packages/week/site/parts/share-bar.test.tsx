/**
 * Tests for the share bar: the static HTML holds the full width, and with motion allowed the fill grows once from 0.
 * The fill is the shared bar fill of the design package, so these tests cover the growth of every bar.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { renderToString } from "react-dom/server";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { ShareBar } from "./share-bar";

/* jsdom has no matchMedia, and Framer Motion reads it. The stub matches no query, so motion is allowed. */
vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList,
);

afterEach(() => cleanup());
afterAll(() => vi.unstubAllGlobals());

/* The scale of the fill along the bar: 1 for no transform, else the number in scaleX(). */
function scaleOf(fill: HTMLElement): number {
  const match = fill.style.transform.match(/scaleX\(([\d.e-]+)\)/);
  return match ? Number(match[1]) : 1;
}

describe("ShareBar", () => {
  it("holds the full width and no scale in the static HTML, so a page with no script shows the bar at rest", () => {
    const html = renderToString(<ShareBar share={62.5} tone="page" />);
    expect(html).toContain("width:62.5%");
    expect(html).not.toContain("scale");
  });

  it("grows once from 0 to its full width with motion allowed", async () => {
    render(<ShareBar share={62.5} tone="page" />);
    const fill = screen.getByRole("meter").querySelector("[data-bar-fill]") as HTMLElement;
    expect(fill.style.width).toBe("62.5%");
    // The samples run past the 0.7 s rise, so the last sample is the rest state.
    const samples: number[] = [];
    for (let at = 0; at <= 1000; at += 50) {
      samples.push(scaleOf(fill));
      await new Promise((done) => setTimeout(done, 50));
    }
    expect(samples[0]).toBeLessThan(0.1);
    samples.slice(1).forEach((scale, index) => expect(scale).toBeGreaterThanOrEqual(samples[index]));
    expect(samples.at(-1)).toBe(1);
  });
});
