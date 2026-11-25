/**
 * Tests for the reader of the published teams of the Live names: the names of each roster across the season, newest
 * first, and the avatar URL of the newest week. Each test builds a temp public/ folder of week pages.
 */
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, spyOn } from "bun:test";
import { weekPageJson } from "@/fixtures/week-page-json";

const roots: string[] = [];
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

type Team = { roster_id: number; name: string; avatar_url: string | null };

/* A temp public/ folder with one week page per entry, each with the teams it gets. */
async function readerOver(weeks: Record<string, Team[]>) {
  const root = mkdtempSync(join(tmpdir(), "live-names-data-"));
  roots.push(root);
  mkdirSync(join(root, "public"));
  for (const [week, teams] of Object.entries(weeks)) {
    const base = JSON.parse(weekPageJson());
    const first = Object.values(base.teams)[0] as Record<string, unknown>;
    const published = Object.fromEntries(
      teams.map((team) => [String(team.roster_id), { ...first, ...team }]),
    );
    mkdirSync(join(root, "public", "2026", week), { recursive: true });
    writeFileSync(
      join(root, "public", "2026", week, "page.json"),
      JSON.stringify({ ...base, teams: published }),
    );
  }
  spyOn(process, "cwd").mockReturnValue(root);
  return import("./live-names-data");
}

describe("publishedTeams", () => {
  it("gives each roster its names newest first and the avatar URL of the newest week", async () => {
    const { publishedTeams } = await readerOver({
      "week-09": [
        { roster_id: 5, name: "Puka Party", avatar_url: "https://sleepercdn.com/uploads/old.jpg" },
      ],
      "week-10": [
        {
          roster_id: 5,
          name: "Puka Deez...",
          avatar_url: "https://sleepercdn.com/uploads/puka.jpg",
        },
      ],
    });
    expect(publishedTeams(2026)).toEqual([
      {
        rosterId: 5,
        names: ["Puka Deez...", "Puka Party"],
        avatarUrl: "https://sleepercdn.com/uploads/puka.jpg",
      },
    ]);
  });

  it("gives no team for a season with no week page", async () => {
    const { publishedTeams } = await readerOver({});
    expect(publishedTeams(2026)).toEqual([]);
  });
});
