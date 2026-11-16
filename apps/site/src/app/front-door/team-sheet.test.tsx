/**
 * Tests for the team sheet of the front door. They drag the sheet with a mouse pointer and read the role of the dialog.
 * A drag down closes the sheet on a change of team, and the sheet of the first visit has no close of any kind.
 */
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import "@cpc/design/ui/sheet-jsdom";
import { standInForAnimate } from "@cpc/design/ui/sheet-drag-jsdom";
import type { DoorTeam } from "@/lib/data/front-door-data";
import { TeamSheet } from "./team-sheet";

let putBack = () => {};
beforeEach(() => {
  putBack = standInForAnimate();
});
afterEach(() => {
  cleanup();
  putBack();
});

const TEAMS: DoorTeam[] = [
  { id: 1, name: "Alpha", avatar: null, wins: 5, losses: 2, rank: 1 },
  { id: 2, name: "Beta", avatar: null, wins: 3, losses: 4, rank: 2 },
];

/* A mouse drag down the sheet: press on it, move the pointer down in steps, then let go. */
function dragDown(element: Element) {
  const pointer = { pointerId: 1, pointerType: "mouse", button: 0 };
  fireEvent.pointerDown(element, { ...pointer, clientX: 100, clientY: 100 });
  for (const y of [140, 200, 280, 380]) {
    fireEvent.pointerMove(document, { ...pointer, clientX: 100, clientY: y });
  }
  fireEvent.pointerUp(document, { ...pointer, clientX: 100, clientY: 380 });
}

describe("the team sheet", () => {
  it("closes on a drag down on a change of team, and keeps the old team", async () => {
    const closed: string[] = [];
    const picked: number[] = [];
    render(
      <TeamSheet siteName="Test league" teams={TEAMS} current={1} onPick={(id) => picked.push(id)} onClose={() => closed.push("close")} />,
    );
    await act(async () => dragDown(screen.getByRole("dialog", { name: "Which team is yours?" })));
    await waitFor(() => expect(closed).toEqual(["close"]));
    expect(picked).toEqual([]);
  });

  it("does not close on a drag down on the first visit", async () => {
    render(<TeamSheet siteName="Test league" teams={TEAMS} current={null} onPick={() => {}} />);
    await act(async () => dragDown(screen.getByRole("dialog", { name: "Which team is yours?" })));
    expect(screen.getByRole("dialog", { name: "Which team is yours?" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Close" })).toBeNull();
  });
});
