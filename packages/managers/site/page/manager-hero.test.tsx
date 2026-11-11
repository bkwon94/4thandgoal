/**
 * Tests for the scene of the manager hero, rendered from roster 7 of the real managers file.
 * They check one canvas when the page passes the scene, none without it, and the grade popover over the scene.
 */
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Manager } from "../schema/manager-types";
import { managers as fixture } from "../fixtures/managers";
import { ManagerHero } from "./manager-hero";
import { managerScene } from "./manager-scene";

afterEach(cleanup);

/* Roster 7 of the fixture, with the joined fields of the loader. */
const entry = fixture.managers.find((row) => row.roster_id === 7) as Manager;
const manager: Manager = { ...entry, standing: 9, rank: 9, movement: 0, odds: null, odds_change: null };

describe("ManagerHero scene", () => {
  it("draws the scene of the weeks in its hero when the page passes it, as the first hero of the page (AT-18)", () => {
    const { container } = render(<ManagerHero manager={manager} avatar="avatars/7.jpg" teams={12} through={9} scene={managerScene(manager)} />);
    expect(container.querySelectorAll("section canvas[data-hero-scene]")).toHaveLength(1);
  });

  it("draws no scene when the page passes none, so the hero keeps the static grid", () => {
    const { container } = render(<ManagerHero manager={manager} avatar="avatars/7.jpg" teams={12} through={9} />);
    expect(container.querySelector("canvas")).toBeNull();
  });

  it("still opens the grade popover on a tap of the grade letter with the scene in the hero (AT-36)", async () => {
    render(<ManagerHero manager={manager} avatar="avatars/7.jpg" teams={12} through={9} scene={managerScene(manager)} />);
    const trigger = screen.getByRole("button", { name: /^Grade [A-F][+-]?, how the grade reads$/ });
    fireEvent.click(trigger);
    expect(await screen.findByRole("dialog", { name: "How The Grade Reads" })).toBeTruthy();
  });
});

describe("ManagerHero grade label", () => {
  it("says which week the grade is from, as a label by the grade (ticket 32)", () => {
    render(<ManagerHero manager={manager} avatar="avatars/7.jpg" teams={12} through={9} />);
    expect(screen.getByText("after week 9")).toBeTruthy();
  });

  it("shows no label when the manager has no grade", () => {
    render(<ManagerHero manager={{ ...manager, grade: null }} avatar="avatars/7.jpg" teams={12} through={9} />);
    expect(screen.queryByText("after week 9")).toBeNull();
  });
});
