/**
 * Tests for the idle stage of the analyzer hero, on the real rosters of the latest weekly build of cpc.
 * Each side shows on the stage of the title hero with a count of the players it gets, and the hero ground is the mesh (AT-1, AT-2).
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "bun:test";
import "@cpc/design/ui/sheet-jsdom";
import { apiTarget } from "@cpc/analyzer/lib/fixtures/api";
import type { Team } from "@cpc/analyzer/lib/api";
import { teamsResponseSchema } from "@cpc/analyzer/lib/schemas/api";
import { rawTeams } from "@/fixtures/raw-teams";
import { pickPlayers, pickTeam } from "@cpc/analyzer/form/form-steps";
import { TradeForm } from "@cpc/analyzer/form/trade-form";

/* The teams of trade T, roster 6 and roster 12, from the raw files of the latest week of cpc.
   The schema of the teams route checks the shape, so a drift of the helper fails here. The test sits in the app layer,
   because it reads the raw files of the client, and a package reads no file (ADR 0012). */
const TEAMS: Team[] = teamsResponseSchema.parse({
  teams: rawTeams("cpc").filter((team) => [6, 12].includes(team.roster_id)),
}).teams;

/* A manager can change the name of a team in any week, so the test reads each name from TEAMS by roster. */
const teamName = (rosterId: number) => TEAMS.find((team) => team.roster_id === rosterId)!.team;
const SIX = teamName(6);
const TWELVE = teamName(12);

beforeEach(() => {
  render(
    <TradeForm
      teams={TEAMS}
      target={apiTarget}
      finderOn={false}
      passphrase="localtest"
      onUnauthorized={() => {}}
    />,
  );
});

afterEach(() => cleanup());

describe("the idle stage", () => {
  it("draws the ground of the title hero as the mesh, in the art layer of the hero", () => {
    const hero = screen.getByRole("region", { name: "Trade Analyzer" });
    const art = hero.querySelector("[data-hero-art='texture']")!;
    expect(art.querySelector("canvas[data-hero-mesh]")).not.toBeNull();
    // The canvas draws its own grid and glow, so the art layer drops the static texture.
    expect(art.classList.contains("hero-texture")).toBe(false);
  });

  it("shows no player on the stage of an empty Stack", () => {
    const hero = screen.getByRole("region", { name: "Trade Analyzer" });
    expect(hero.querySelector("[data-hero-slot=feature]")).toBeNull();
  });

  it("counts Kenneth Walker III in the row of roster 12 after the add, with no headshot on the stage (AT-2)", async () => {
    await pickTeam("Your Team", SIX);
    await pickTeam("Team Two", TWELVE);
    await pickPlayers("Team Two", SIX, "Kenneth Walker III");
    const hero = screen.getByRole("region", { name: "Trade Analyzer" });
    const stage = hero.querySelector("[data-hero-slot=feature]") as HTMLElement;
    const row = (team: string) =>
      within(stage).getByText(team, { exact: true }).closest("li") as HTMLElement;
    expect(within(row(TWELVE)).getByText("1 player")).toBeTruthy();
    // Roster 6 gets no player yet, so its row holds the dashed empty token.
    expect(row(SIX).querySelector("[data-stage-empty]")).not.toBeNull();
    // The Stack below shows each player, so the stage shows no name and no headshot before the grade.
    expect(within(stage).queryByText("Kenneth Walker III")).toBeNull();
    expect(stage.querySelector("[title]")).toBeNull();
  });
});
