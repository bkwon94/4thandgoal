/**
 * Tests for the hunt with the reduced-motion media query on: a tap on the egg shows the letter tile at once, and a tap on
 * the stub of the claim ticket tears it and shows the stamp, each with no motion.
 * matchMedia is a stub, and it must exist before Framer Motion first reads it, so the stub runs at the top of the file.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { TAP_GAP_MS } from "../listener/listener";
import { fakeEggsApi, PASSPHRASE } from "../lib/fixtures/eggs-api";
import { STAMP_MS } from "./claim-ticket";
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

afterEach(() => {
  cleanup();
  localStorage.clear();
});
afterAll(() => vi.unstubAllGlobals());

describe("EggHunt with reduced motion", () => {
  it("shows the letter tile at once on a tap of the egg, with no ring, no crack line, no shard, and no motion class", async () => {
    render(
      <>
        <span data-stable-id="luck-3">+1.20</span>
        <EggHunt api={fakeEggsApi({ match: true, claimed: false, letter: "C", token: "t1" })} />
      </>,
    );
    // The listener starts when the board loads with a drop.
    await act(async () => {});
    const cell = screen.getByText("+1.20");
    for (const _ of [1, 2]) fireEvent.pointerUp(cell, { isPrimary: true });
    await act(() => new Promise((done) => setTimeout(done, TAP_GAP_MS + 50)));
    await screen.findByRole("heading", { name: "You found an egg" });
    expect(document.querySelector(".egg-ripple")).toBeNull();
    expect(document.querySelector(".egg-bob")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Crack the egg" }));
    // No wait: the letter and the claim show in the same render as the tap.
    const tile = screen.getByTestId("egg-letter");
    expect(tile.textContent).toBe("C");
    expect(tile.className).not.toContain("egg-tile-rise");
    expect(screen.queryAllByTestId("egg-crack-line")).toEqual([]);
    expect(document.querySelector(".egg-shard")).toBeNull();
    expect(document.querySelector(".egg-flash")).toBeNull();
    expect(screen.getByRole("button", { name: "Claim C" })).toBeTruthy();
  });

  it("tears the stub on a tap and shows the CLAIMED stamp at once, with no flutter, no sweep, and no motion", async () => {
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    const api = fakeEggsApi({ match: true, claimed: false, letter: "C", token: "t1" });
    render(
      <>
        <span data-stable-id="luck-3">+1.20</span>
        <EggHunt api={api} />
      </>,
    );
    await act(async () => {});
    const cell = screen.getByText("+1.20");
    for (const _ of [1, 2]) fireEvent.pointerUp(cell, { isPrimary: true });
    await act(() => new Promise((done) => setTimeout(done, TAP_GAP_MS + 50)));
    fireEvent.click(await screen.findByRole("button", { name: "Crack the egg" }));
    fireEvent.click(screen.getByRole("button", { name: "Claim C" }));
    fireEvent.click(await screen.findByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(screen.getByRole("button", { name: "CORNERSTONE" }));
    const ticket = screen.getByRole("group", { name: "Claim ticket" });
    const stub = within(ticket).getByRole("button", { name: "Tear to claim C for CORNERSTONE" });
    // No wait for a tear: the claim sends in the same tap.
    await act(async () => fireEvent.click(stub));
    expect(api.claims).toEqual([{ token: "t1", roster_id: 2, word: "CORNERSTONE" }]);
    const stamp = within(ticket).getByText("CLAIMED");
    expect(stamp.className).not.toContain("egg-ticket-stamp-in");
    // The stub leaves with no flutter, and the ticket shows no sweep.
    expect(stub.className).toContain("invisible");
    expect(stub.className).not.toContain("egg-stub-flutter");
    expect(ticket.querySelector(".egg-ticket-sweep")).toBeNull();
    await act(() => new Promise((done) => setTimeout(done, STAMP_MS + 50)));
    expect(screen.getByRole("dialog", { name: "C goes to CORNERSTONE." })).toBeTruthy();
  });
});
