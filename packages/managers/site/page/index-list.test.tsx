/**
 * Tests for the Index list part with the rows of the real CPC week 8 files.
 * They check a chip with no team, and the letter roll that keeps the name of a row as one plain text.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import managersJson from "../../../../apps/site/src/fixtures/sites/cpc/public/2026/managers.json";
import rankingsJson from "../../../../apps/site/src/fixtures/sites/cpc/public/2026/rankings.json";
import { managersFileSchema } from "../schema/managers";
import { IndexList, type IndexRow } from "./index-list";

afterEach(() => {
  cleanup();
});

/* The ledger rows of CPC week 8, from the published rankings and managers files, in power-ranking order. */
function cpcRows(): IndexRow[] {
  const { managers } = managersFileSchema.parse(managersJson);
  // The managers package holds no rankings type, so the test names the three fields it reads.
  const last = rankingsJson.weeks.at(-1)!.rows as unknown as { roster_id: number; rank: number; odds: { playoff: number } }[];
  return last.map((row) => {
    const entry = managers.find((each) => each.roster_id === row.roster_id)!;
    return {
      id: row.roster_id,
      place: row.rank,
      name: entry.team.name,
      avatar: `avatars/${row.roster_id}.jpg`,
      href: `/2026/managers/${row.roster_id}/`,
      odds: row.odds.playoff,
      // Every team has clinched, as in the last week of a season, so Bubble and Out hold no team.
      group: "in",
      facts: "",
      grade: entry.grade,
    };
  });
}

describe("IndexList", () => {
  it("keeps a chip with no team in view with a count of 0, and it cannot be pressed", () => {
    render(<IndexList rows={cpcRows()} teams={12} />);
    const chips = within(screen.getByRole("group", { name: "Playoff Race" }));
    const out = chips.getByRole("button", { name: /Out/ });
    expect(out.textContent).toBe("Out0");
    expect(out.hasAttribute("disabled")).toBe(true);
    fireEvent.click(out);
    expect(chips.getByRole("button", { name: /All/ }).getAttribute("aria-pressed")).toBe("true");
    expect(within(screen.getByRole("list", { name: "Index List" })).getAllByRole("listitem")).toHaveLength(12);
  });

  it("gives each letter of a name its own roll window, and keeps the name as one text for a reader", () => {
    render(<IndexList rows={cpcRows()} teams={12} />);
    const head = screen.getByRole("button", { name: /The Blue Tent/ });
    // "The Blue Tent" has 11 letters and two spaces. The spaces stay plain spaces, so the name wraps between words.
    expect(head.querySelectorAll(".ix-letter")).toHaveLength(11);
    expect(head.querySelector(".ix-name")?.textContent).toBe("The Blue Tent");
  });
});
