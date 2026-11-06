/**
 * Tests for the season of one stored run, as the replay plays it: the standings after each week, the bracket, and the champion.
 * Every test reads the real sim file of CPC 2026 week 8, and checks each of its 200 runs against the facts the sim stored.
 */
import { describe, expect, it } from "vitest";
import { sim } from "../fixtures/sim";
import { replaySeason } from "./season";

describe("the season of a stored run", () => {
  it("ends the regular season in the stored final table, for each of the 200 runs", () => {
    sim.sample.forEach((run, index) => {
      const season = replaySeason(sim, index);
      expect(season.weeks.map((week) => week.week)).toEqual([9, 10, 11, 12, 13, 14]);
      expect(season.weeks.at(-1)!.standings.map((row) => row.roster_id)).toEqual(run.table);
    });
  });

  it("plays each stored bracket game and crowns the stored champion, for each of the 200 runs", () => {
    sim.sample.forEach((run, index) => {
      const season = replaySeason(sim, index);
      expect(season.rounds.map((round) => round.games.map((game) => [game.high.roster_id, game.low.roster_id]))).toEqual(
        run.bracket,
      );
      expect(season.rounds.map((round) => round.week)).toEqual([15, 16, 17]);
      expect(season.champion.roster_id).toBe(run.champion);
    });
  });

  it("gives each week the scores of its games, the median, and the move of each team", () => {
    const season = replaySeason(sim, 0);
    const week9 = season.weeks[0];
    // Week 9 of run 0: The Blue Tent scores 112.9, and the median is the mean of the two middle scores of the week.
    const blueTent = week9.games.flatMap((game) => game.teams).find((team) => team.roster_id === 1)!;
    expect(blueTent.score).toBe(112.9);
    const scores = week9.games.flatMap((game) => game.teams.map((team) => team.score)).sort((a, b) => b - a);
    expect(week9.median).toBeCloseTo((scores[5] + scores[6]) / 2, 5);
    // The move is the change of place from the week before; the first week compares with the real standings of week 8.
    for (const row of season.weeks[1].standings) {
      const before = season.weeks[0].standings.findIndex((r) => r.roster_id === row.roster_id) + 1;
      expect(row.move).toBe(before - row.place);
    }
  });

  it("names the seeds, the byes, and the cut of the final standings", () => {
    const season = replaySeason(sim, 0);
    // Run 0 ends with Lil Fridge first and Return of T Mac second, so they take the two byes.
    expect(season.seeds.slice(0, 2).map((team) => team.name)).toEqual(["Lil Fridge", "Return of T Mac"]);
    expect(season.seeds).toHaveLength(6);
    expect(season.byes).toBe(2);
  });

  it("reseeds the CPC semifinal so seed 1 meets the lowest seed left", () => {
    sim.sample.forEach((_, index) => {
      const semi = replaySeason(sim, index).rounds[1];
      const seeds = semi.games.flatMap((game) => [game.high.seed, game.low.seed]);
      expect(semi.games[0].high.seed).toBe(1);
      expect(semi.games[0].low.seed).toBe(Math.max(...seeds));
    });
  });

  it("gives the champion its title odds over all runs", () => {
    const season = replaySeason(sim, 0);
    expect(season.champion.name).toBe("Lil Fridge");
    expect(season.champion.title).toBe(14.4);
  });
});
