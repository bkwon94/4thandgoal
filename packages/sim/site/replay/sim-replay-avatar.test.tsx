/**
 * Tests for the avatar of the champion card on the real sim file of CPC 2026 week 8: the card shows the avatar of
 * the champion's team that the app passes, and the default frame when the app passes none.
 */
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { sim } from "../fixtures/sim";
import { SimReplay } from "./sim-replay";

afterEach(cleanup);

/* Plays run 0 to its end, so the champion card shows. */
function playToEnd(avatars?: Record<string, string>) {
  const view = render(<SimReplay sim={sim} pick={() => 0} avatars={avatars} />);
  fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
  fireEvent.click(screen.getByRole("button", { name: "Skip to the end" }));
  return view.container.querySelector("[aria-label='Champion of This Run'] [data-avatar]")!;
}

describe("the avatar of the champion", () => {
  it("shows the avatar of the champion's team", () => {
    // Every roster id gets its own path, so the src names the champion.
    const avatars = Object.fromEntries(Array.from({ length: 12 }, (_, i) => [String(i + 1), `/2026/week-08/avatars/${i + 1}.jpg`]));
    const img = playToEnd(avatars).querySelector("img");
    expect(img).not.toBeNull();
    expect(img!.getAttribute("src")).toMatch(/^\/2026\/week-08\/avatars\/\d+\.jpg$/);
  });

  it("shows the default frame when the app passes no avatar", () => {
    expect(playToEnd().querySelector("img")).toBeNull();
  });
});
