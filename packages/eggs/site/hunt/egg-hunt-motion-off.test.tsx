/**
 * Tests for the find with the reduced-motion media query on: a tap on the egg shows the letter tile at once, with no motion.
 * matchMedia is a stub, and it must exist before Framer Motion first reads it, so the stub runs at the top of the file.
 */
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { TAP_GAP_MS } from "../listener/listener";
import { fakeEggsApi } from "../lib/fixtures/eggs-api";
import { EggHunt } from "./egg-hunt";

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

afterEach(cleanup);
afterAll(() => vi.unstubAllGlobals());

describe("EggHunt with reduced motion", () => {
  it("shows the letter tile at once on a tap of the egg, with no ring, no crack, and no motion class", async () => {
    render(
      <>
        <span data-stable-id="luck-3">+1.20</span>
        <EggHunt api={fakeEggsApi({ match: true, claimed: false, letter: "C", token: "t1" })} />
      </>,
    );
    const cell = screen.getByText("+1.20");
    for (const _ of [1, 2, 3]) fireEvent.pointerUp(cell, { isPrimary: true });
    await act(() => new Promise((done) => setTimeout(done, TAP_GAP_MS + 50)));
    await screen.findByRole("heading", { name: "You found an egg" });
    expect(document.querySelector(".egg-ripple")).toBeNull();
    expect(document.querySelector(".egg-bob")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Crack the egg" }));
    // No wait: the letter and the claim show in the same render as the tap.
    const tile = screen.getByTestId("egg-letter");
    expect(tile.textContent).toBe("C");
    expect(tile.className).not.toContain("egg-tile-rise");
    expect(document.querySelector(".egg-crack")).toBeNull();
    expect(document.querySelector(".egg-burst")).toBeNull();
    expect(screen.getByRole("button", { name: "Claim C" })).toBeTruthy();
  });
});
