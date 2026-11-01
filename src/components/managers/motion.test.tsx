/**
 * Tests for the motion of the manager page with motion on. jsdom has no matchMedia, so Framer Motion reads no reduced motion.
 * The odds count from zero once and must end at the final percent. The grade and the slot lines must end at rest.
 */
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Manager } from "@/lib/manager-types";
import fixture from "@/fixtures/managers.json";
import { ManagerHero } from "./manager-hero";
import { Roster } from "./roster";

afterEach(cleanup);

/* A fixture entry with the joined fields of the loader and the given playoff odds. */
function managerOf(odds: Manager["odds"]): Manager {
  const entry = fixture.managers[0] as Manager;
  return { ...entry, standing: 1, rank: 2, movement: 0, odds, odds_change: odds ? 0 : null };
}

/* The number under each label of the Hero Numbers group, in order: the grade, the odds, and the power rank. */
function numbers(): HTMLElement[] {
  const group = screen.getByRole("group", { name: "Hero Numbers" });
  return [...group.querySelectorAll("dt")].map((term) => term.nextElementSibling as HTMLElement);
}

describe("Manager page motion", () => {
  it("counts the odds up once and ends at the final percent", async () => {
    render(<ManagerHero manager={managerOf({ playoff: 63, bye: 20, seed: 3, status: "open" })} avatar="avatars/1.jpg" teams={12} />);
    const odds = numbers()[1];
    // The count starts from zero on the next frame, so the percent first reads under the final number.
    await waitFor(() => expect(Number.parseInt(odds.textContent!)).toBeLessThan(63), { timeout: 1000 });
    // The count runs over the next frames, so the wait passes once the count ends.
    await waitFor(() => expect(odds.textContent).toBe("63%"), { timeout: 1000 });
    // The count runs once, so the percent stays final after more frames.
    await new Promise((done) => setTimeout(done, 100));
    expect(odds.textContent).toBe("63%");
  });

  it("shows the dash at once with no odds", () => {
    render(<ManagerHero manager={managerOf(null)} avatar="avatars/1.jpg" teams={12} />);
    expect(numbers()[1].textContent).toBe("—");
  });

  it("settles the grade letter at rest", async () => {
    render(<ManagerHero manager={managerOf(null)} avatar="avatars/1.jpg" teams={12} />);
    const letter = within(numbers()[0]).getByText("D");
    await waitFor(() => expect(letter.closest("[data-reveal]")).not.toBeNull());
    await waitFor(() => expect((letter.closest("[data-reveal]") as HTMLElement).style.opacity).toBe("1"), { timeout: 1000 });
  });

  it("enters the four slot rank lines, each in its own reveal", async () => {
    render(<Roster manager={managerOf(null)} teams={12} />);
    const lines = screen.getAllByRole("listitem");
    expect(lines).toHaveLength(4);
    for (const line of lines) expect(line.querySelector("[data-reveal]")).not.toBeNull();
    await waitFor(
      () => lines.forEach((line) => expect((line.querySelector("[data-reveal]") as HTMLElement).style.opacity).toBe("1")),
      { timeout: 1000 },
    );
  });
});
