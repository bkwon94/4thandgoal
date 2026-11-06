/**
 * The season of one stored sim run, as the replay plays it: each regular week with its games, its median, and the
 * standings after it, then the seeds, each bracket round, and the champion. It draws nothing; it reads the stored scores.
 */
import type { Sim } from "../schema/sim-types";

export type StandingRow = {
  roster_id: number;
  name: string;
  // The place after the week, 1 first.
  place: number;
  wins: number;
  losses: number;
  points: number;
  // The places the team rose since the week before: positive up, negative down, 0 for no change.
  move: number;
};

export type WeekTeam = { roster_id: number; name: string; score: number };

export type ReplayWeek = {
  week: number;
  games: { teams: [WeekTeam, WeekTeam] }[];
  // The line of the median game: the mean of the two middle scores of the week. Null when the league has no median game.
  median: number | null;
  standings: StandingRow[];
};

export type Seed = { roster_id: number; name: string; seed: number };

export type BracketTeam = Seed & { score: number };

export type BracketGame = { high: BracketTeam; low: BracketTeam; winner: number };

export type ReplayRound = {
  // "Round 1", then "Semifinal" and "Final" for the last two rounds.
  label: string;
  week: number;
  games: BracketGame[];
  // The seeds that skip this round and wait in the next one.
  byes: Seed[];
};

export type Champion = Seed & { title: number };

export type ReplaySeason = {
  // The standings at the start of the sim, from the real records.
  start: StandingRow[];
  weeks: ReplayWeek[];
  seeds: Seed[];
  // The count of seeds with a bye.
  byes: number;
  rounds: ReplayRound[];
  champion: Champion;
};

type Tally = { wins: number; losses: number; points: number };

/* The order of the sim: the most wins, then the most points, then the lowest roster ID. */
function ordered(tally: Map<number, Tally>, names: Sim["names"], before?: StandingRow[]): StandingRow[] {
  const ids = [...tally.keys()].sort((a, b) => {
    const x = tally.get(a)!;
    const y = tally.get(b)!;
    return y.wins - x.wins || y.points - x.points || a - b;
  });
  return ids.map((rid, index) => {
    const place = index + 1;
    const was = before?.find((row) => row.roster_id === rid)?.place ?? place;
    return { roster_id: rid, name: names[rid], place, ...tally.get(rid)!, move: was - place };
  });
}

/* The median line, the same rule as the sim: the mean of the two middle scores. */
function median(scores: number[]): number {
  const sorted = [...scores].sort((a, b) => b - a);
  const middle = Math.floor(sorted.length / 2);
  return (sorted[middle - 1] + sorted[middle]) / 2;
}

/* The label of a round by its place from the end, so a bracket of any size ends on the semifinal and the final. */
function roundLabel(index: number, count: number): string {
  if (index === count - 1) return "Final";
  if (index === count - 2) return "Semifinal";
  return `Round ${index + 1}`;
}

export function replaySeason(sim: Sim, index: number): ReplaySeason {
  const run = sim.sample[index];
  const { names } = sim;
  const regular = sim.weeks.filter((week) => !sim.bracket_weeks.includes(week));
  const tally = new Map<number, Tally>(
    Object.entries(sim.records).map(([rid, [wins, losses, points]]) => [Number(rid), { wins, losses, points }]),
  );
  const start = ordered(tally, names);

  let before = start;
  const weeks: ReplayWeek[] = regular.map((week, column) => {
    const score = (rid: number) => run.scores[rid][column]!;
    const games = sim.schedule[week].map(([a, b]) => ({
      teams: [a, b].map((rid) => ({ roster_id: rid, name: names[rid], score: score(rid) })) as [WeekTeam, WeekTeam],
    }));
    for (const { teams } of games) {
      const [x, y] = teams;
      // An exact tie gives no win, the same rule as the sim.
      if (x.score !== y.score) {
        const [win, loss] = x.score > y.score ? [x, y] : [y, x];
        tally.get(win.roster_id)!.wins += 1;
        tally.get(loss.roster_id)!.losses += 1;
      }
    }
    const line = sim.parameters.median_game ? median([...tally.keys()].map(score)) : null;
    for (const [rid, team] of tally) {
      if (line !== null && score(rid) > line) team.wins += 1;
      else if (line !== null && score(rid) < line) team.losses += 1;
      team.points += score(rid);
    }
    const standings = ordered(tally, names, before);
    before = standings;
    return { week, games, median: line, standings };
  });

  const seeds = run.table
    .slice(0, sim.parameters.playoff_spots)
    .map((rid, i) => ({ roster_id: rid, name: names[rid], seed: i + 1 }));
  const seedOf = new Map(seeds.map((seed) => [seed.roster_id, seed]));
  const rounds: ReplayRound[] = run.bracket.map((pairs, r) => {
    const column = regular.length + r;
    const team = (rid: number): BracketTeam => ({ ...seedOf.get(rid)!, score: run.scores[rid][column]! });
    const games = pairs.map(([a, b]) => {
      const [high, low] = [team(a), team(b)];
      // A tie in a bracket game goes to the higher seed, the same rule as the sim.
      return { high, low, winner: low.score > high.score ? low.roster_id : high.roster_id };
    });
    const playing = new Set(pairs.flat());
    const next = run.bracket[r + 1]?.flat() ?? [];
    const byes = next.filter((rid) => !playing.has(rid)).map((rid) => seedOf.get(rid)!);
    return { label: roundLabel(r, run.bracket.length), week: sim.bracket_weeks[r], games, byes };
  });

  return {
    start,
    weeks,
    seeds,
    byes: sim.parameters.bye_count,
    rounds,
    champion: { ...seedOf.get(run.champion)!, title: sim.teams[run.champion].title },
  };
}
