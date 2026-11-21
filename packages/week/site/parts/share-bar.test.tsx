/**
 * Tests for the share bar: the static HTML holds the full width, and with motion allowed the fill grows once from 0.
 * The fill is the shared bar fill of the design package, so these tests cover the growth of every bar.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { renderToString } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, it, spyOn } from "bun:test";
import { ShareBar } from "./share-bar";

/* jsdom has no matchMedia, and Framer Motion reads it. The stub matches no query, so motion is allowed. */
const matchMediaStub = (query: string) =>
  ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }) as unknown as MediaQueryList;

beforeEach(() => {
  spyOn(globalThis, "matchMedia").mockImplementation(matchMediaStub);
});
afterEach(() => cleanup());

/* happy-dom has Element.prototype.animate, so Framer Motion runs a fade as a Web Animation and the inline style holds no
   middle value. Framer Motion checks for the method once per file, so a file that reads the middle values hides it first. */
const animate = Element.prototype.animate;
// happy-dom has an IntersectionObserver that never reports an entry, so the fill would wait at 0. jsdom has none, and the
// bar then grows on mount, so the file hides the observer too.
const observer = globalThis.IntersectionObserver;
beforeEach(() => {
  // @ts-expect-error The bar checks for the observer with typeof.
  delete globalThis.IntersectionObserver;
  // @ts-expect-error Framer Motion checks for an own property, so only a delete hides it.
  delete Element.prototype.animate;
});
afterEach(() => {
  Element.prototype.animate = animate;
  globalThis.IntersectionObserver = observer;
});

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
    samples
      .slice(1)
      .forEach((scale, index) => expect(scale).toBeGreaterThanOrEqual(samples[index]));
    expect(samples.at(-1)).toBe(1);
  });
});
