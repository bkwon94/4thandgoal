/**
 * The shared steps of the analyzer tests: the slot of a side, the pick of a team, the pick of players, and the pick of a trade.
 * The tests of the trade form and of the analyzer both build a trade on the screen with these steps.
 */
import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { expect } from "vitest";

export type SideTitle = "Your Team" | "Team Two" | "Team Three" | "Team Four";

/* The slot of a side in the teams row. Its name says the team once picked. */
export const slot = (side: SideTitle) =>
  screen.getByRole("button", { name: new RegExp(`^(Pick ${side}|${side}: )`) }) as HTMLButtonElement;

/* The button that opens the picker of a side. */
export const addPlayer = (side: SideTitle) =>
  screen.getByRole("button", { name: `Add a player ${side} gets` }) as HTMLButtonElement;

/* Picks a team in the team sheet that is open, and waits for the sheet to close. */
export async function chooseTeam(team: string) {
  fireEvent.click(within(await screen.findByRole("dialog")).getByRole("button", { name: new RegExp(team) }));
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
}

export async function pickTeam(side: SideTitle, team: string) {
  fireEvent.click(slot(side));
  await chooseTeam(team);
}

/* Opens the picker of a side, checks each player on the tab of the source team, and taps Done. */
export async function pickPlayers(side: SideTitle, from: string, ...names: string[]) {
  fireEvent.click(addPlayer(side));
  const open = await screen.findByRole("dialog");
  fireEvent.click(within(open).getByRole("tab", { name: from }));
  for (const name of names) fireEvent.click(within(open).getByRole("checkbox", { name: new RegExp(name) }));
  fireEvent.click(within(open).getByRole("button", { name: /^Done/ }));
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
}

/* A trade of two teams with one player for each card. My team gets the player of the other team, and the other team gets mine. */
export type TwoTeamTrade = { mine: string; other: string; mineGets: string; otherGets: string };

/* Picks my team and the other team, then one player for each card. */
export async function pickTrade({ mine, other, mineGets, otherGets }: TwoTeamTrade) {
  await pickTeam("Your Team", mine);
  await pickTeam("Team Two", other);
  await pickPlayers("Your Team", other, mineGets);
  await pickPlayers("Team Two", mine, otherGets);
}
