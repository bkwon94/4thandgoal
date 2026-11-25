/**
 * Tests for the art of The Race Announcement on the real week 11 file of CPC: the League board rows around Your team in
 * odds order of a playoff spot, with the "You" tag, the odds of Your team, and a pill for a team that is Clinched or Out.
 */
import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "bun:test";
import { weekElevenSim } from "../fixtures/sim";
import type { WeekSim } from "../schema/sim-types";
import { previewOf } from "./preview";
import { SimPreview } from "./sim-preview";

const BO_GIRDS = 6;
const NFC_LEAST = 4;
const LIL_FRIDGE = 3;

const rows = () =>
  within(screen.getByRole("list", { name: "League board near your team" })).getAllByRole(
    "listitem",
  );
const rowNames = () => rows().map((row) => row.querySelector("[data-team]")?.textContent);
const pills = () => rows().map((row) => row.querySelector("[data-pill]")?.textContent ?? null);

/* The week 11 file with each Goal of one team set to `status` for the Goals in `goals`. */
function withStatus(sim: WeekSim, id: number, goals: string[]): WeekSim {
  return {
    ...sim,
    board: sim.board.map((team) =>
      team.roster_id !== id
        ? team
        : {
            ...team,
            goals: Object.fromEntries(
              Object.entries(team.goals).map(([key, value]) => [
                key,
                goals.includes(key) ? { ...value, status: "in" as const } : value,
              ]),
            ),
          },
    ),
  };
}

describe("the art of The Race Announcement", () => {
  it("takes a data shape of under 2 KB from the week sim file, so the home page does not ship the file", () => {
    expect(JSON.stringify(previewOf(weekElevenSim)).length).toBeLessThan(2000);
  });

  it("shows the board rows around Bo Girds in odds order, with the You tag and the odds of a spot (AT-49)", () => {
    render(<SimPreview data={previewOf(weekElevenSim)} you={BO_GIRDS} />);
    expect(rowNames()).toEqual(["Bengals Buddies", "Bo Girds", "Omarion Himpton"]);
    expect(rows()[1].textContent).toContain("You");
    expect(rows()[1].textContent).toContain("11-11");
    expect(rows()[0].textContent).not.toContain("You");
    expect(screen.getByRole("status").textContent).toBe("Odds of a playoff spot 48%");
    expect(pills()).toEqual([null, null, null]);
  });

  it("shows the first three rows of the board for the favorite", () => {
    render(<SimPreview data={previewOf(weekElevenSim)} you={LIL_FRIDGE} />);
    expect(rowNames()).toEqual(["Lil Fridge", "Maye d'force B with U", "Puka Deez..."]);
  });

  it("shows the Out pill on each team that is out, and no pill on a team in the hunt", () => {
    render(<SimPreview data={previewOf(weekElevenSim)} you={NFC_LEAST} />);
    expect(rowNames()).toEqual(["Immaculate Concepcion", "Unsolicited Dak Picks", "NFC Least"]);
    expect(pills()).toEqual([null, "Out", "Out"]);
  });

  it("names the best Goal locked on the pill of a team that clinched", () => {
    const bye = previewOf(withStatus(weekElevenSim, LIL_FRIDGE, ["spot", "bye"]));
    expect(bye.rows.find((row) => row.id === LIL_FRIDGE)?.pill).toBe("Clinched bye");
    const spot = previewOf(withStatus(weekElevenSim, LIL_FRIDGE, ["spot"]));
    expect(spot.rows.find((row) => row.id === LIL_FRIDGE)?.pill).toBe("Clinched spot");
    const seed = previewOf(withStatus(weekElevenSim, LIL_FRIDGE, ["spot", "bye", "seed-1"]));
    expect(seed.rows.find((row) => row.id === LIL_FRIDGE)?.pill).toBe("Clinched 1 seed");
  });
});
