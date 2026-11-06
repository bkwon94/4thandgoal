/**
 * Tests for the chapters of Act III on the real build of CPC 2026 week 8 in the package fixture.
 * They read what a manager sees: each team's games left with the opponents' records, and the players to watch.
 */
import { cleanup, fireEvent, render, within } from "@testing-library/react";
import { oneDecimal } from "@cpc/design/format/format";
import { afterEach, describe, expect, it } from "vitest";
import { midseason } from "../fixtures/midseason";
import { MidseasonScreen } from "../report/midseason-screen";
import type { MidseasonChapter } from "../schema/midseason-types";

afterEach(cleanup);

const SHELL = {
  title: "CPC Fantasy Football",
  brand: { home: "/", logo: null },
  menu: { items: [{ kind: "home" as const, label: "Home", short: "Home", href: "/" }], weeks: [] },
};

const renderReport = () =>
  render(<MidseasonScreen report={midseason} shell={SHELL} pageHref="/midseason/2026/" />);

/* The chapter of the fixture with the key `key`. */
function chapterOf<K extends MidseasonChapter["key"]>(key: K): Extract<MidseasonChapter, { key: K }> {
  const found = midseason.acts.flatMap((act) => act.chapters).find((chapter) => chapter.key === key);
  if (found === undefined) throw new Error(`The fixture has no ${key} chapter`);
  return found as Extract<MidseasonChapter, { key: K }>;
}

const chapterEl = (key: string) => within(document.getElementById(key)!);

describe("the look ahead", () => {
  it("shows each team's 6 games of weeks 9 to 14 with the opponent's record", () => {
    renderReport();
    const { teams } = chapterOf("look-ahead").facts;
    const chapter = chapterEl("look-ahead");
    fireEvent.click(chapter.getByRole("button", { name: `Show all ${teams.length}` }));
    const rows = chapter.getByRole("list", { name: "Schedules left" }).children;
    expect(rows).toHaveLength(teams.length);
    for (const [index, team] of teams.entries()) {
      const games = within(rows[index] as HTMLElement).getByRole("list", { name: `Games left of ${team.name}` }).children;
      expect([...games].map((game) => game.getAttribute("data-week"))).toEqual(["9", "10", "11", "12", "13", "14"]);
      const first = team.games[0];
      expect(games[0].textContent).toContain(first.name);
      expect(games[0].textContent).toContain(`${first.wins}-${first.losses}`);
    }
  });

  it("rates each schedule by the opponents' win rate, the softest first, and shows 5 teams before Show all", () => {
    renderReport();
    const { teams, softest, hardest } = chapterOf("look-ahead").facts;
    const chapter = chapterEl("look-ahead");
    const rows = chapter.getByRole("list", { name: "Schedules left" }).children;
    expect(rows).toHaveLength(5);
    expect(rows[0].textContent).toContain(teams[0].name);
    expect(rows[0].textContent).toContain(`.${String(Math.round(teams[0].opponents_rate! * 1000)).padStart(3, "0")}`);
    expect(rows[0].textContent).toContain("Softest");
    expect(teams[0].roster_id).toBe(softest);
    fireEvent.click(chapter.getByRole("button", { name: /^Show all/ }));
    const last = [...rows].at(-1)!;
    expect(teams.at(-1)!.roster_id).toBe(hardest);
    expect(last.textContent).toContain("Hardest");
  });
});

describe("players to watch", () => {
  it("shows Due to rise, Due to fall, and Grab him now, 3 players each", () => {
    renderReport();
    const facts = chapterOf("watch").facts;
    const chapter = chapterEl("watch");
    const lists = [
      ["Due to Rise", facts.due_to_rise],
      ["Due to Fall", facts.due_to_fall],
      ["Grab Him Now", facts.grab_him_now],
    ] as const;
    for (const [name, players] of lists) {
      const rows = chapter.getByRole("list", { name }).children;
      expect(rows).toHaveLength(3);
      expect([...rows].map((row) => row.textContent)).toEqual(players.map((p) => expect.stringContaining(p.name)));
    }
  });

  it("gives the Expected gap a game of each rise and fall, and the projection and Free agent tag of each grab", () => {
    renderReport();
    const facts = chapterOf("watch").facts;
    const chapter = chapterEl("watch");
    const rise = chapter.getByRole("list", { name: "Due to Rise" }).children[0];
    expect(rise.textContent).toContain(facts.due_to_rise[0].manager);
    expect(rise.textContent).toContain(`${oneDecimal(-facts.due_to_rise[0].gap)} a game under`);
    const fall = chapter.getByRole("list", { name: "Due to Fall" }).children[0];
    expect(fall.textContent).toContain(`${oneDecimal(facts.due_to_fall[0].gap)} a game over`);
    const grab = chapter.getByRole("list", { name: "Grab Him Now" }).children[0];
    expect(grab.textContent).toContain("Free agent");
    expect(grab.textContent).toContain(`${Math.round(facts.grab_him_now[0].projection)} projected`);
  });
});
