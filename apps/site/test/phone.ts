/**
 * The phone stand-in of `bun test`. happy-dom has a desktop-wide window, so each media query of the desktop tier matches.
 * A test of a page calls `stubPhone` in `beforeEach`, so the page sees a phone with motion on, as it did in jsdom.
 */
import { spyOn } from "bun:test";

/* A media query list that matches no query and never fires a change. */
const noMatch = (query: string) =>
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

/* Make `matchMedia` match no query until the end of the test. The preload restores the spy after each test. */
export function stubPhone(): void {
  spyOn(window, "matchMedia").mockImplementation(noMatch);
}
