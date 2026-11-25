/**
 * Tests for the sim page of Your team on the real CPC week 10 sim file: the page opens on the stored team, and a visitor
 * with no team picks one in the page, which the browser keeps for the next visit.
 */
import "@cpc/design/ui/sheet-jsdom";
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "bun:test";
import { weekSim } from "@cpc/sim/fixtures/sim";
import { getYourTeam, setYourTeam } from "@/app/front-door/your-team-store";
import { YourSimPage } from "./your-sim-page";

afterEach(() => {
  cleanup();
  localStorage.clear();
});

const yourTeam = () => screen.getByRole("region", { name: "Your team" });

describe("the sim page of Your team", () => {
  it("opens on the team that the browser keeps", async () => {
    setYourTeam(6);
    await act(async () => {
      render(<YourSimPage sim={weekSim} avatars={{}} />);
    });
    expect(yourTeam().textContent).toContain("Bo Girds");
  });

  it("asks a visitor with no team to pick one, then opens on it and keeps it", async () => {
    await act(async () => {
      render(<YourSimPage sim={weekSim} avatars={{}} />);
    });
    const pick = screen.getByRole("list", { name: "Teams" });
    expect(within(pick).getAllByRole("button")).toHaveLength(12);
    fireEvent.click(within(pick).getByRole("button", { name: "Bo Girds" }));
    expect(yourTeam().textContent).toContain("Bo Girds");
    expect(getYourTeam()).toBe(6);
  });

  it("asks again when the kept team is not in the league", async () => {
    setYourTeam(99);
    await act(async () => {
      render(<YourSimPage sim={weekSim} avatars={{}} />);
    });
    expect(screen.getByRole("list", { name: "Teams" })).toBeTruthy();
  });
});
