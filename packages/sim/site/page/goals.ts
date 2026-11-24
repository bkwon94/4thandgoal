/**
 * The Goals of The Race: the key, the name, and the short label of each Goal, the Goals of a page, and the League board in
 * odds order. Each takes data from the sim file and returns data, so the parts and the tests read one wording.
 */
import type { BoardTeam, GoalOdds, SimPage, WeekSim } from "../schema/sim-types";

/* A Goal by its key in the file: "spot", "bye", or "seed-1" to the last seed. */
export type GoalKey = "spot" | "bye" | `seed-${number}`;

/* The seed of a seed Goal, else null. */
export const seedOf = (goal: GoalKey): number | null =>
  goal.startsWith("seed-") ? Number(goal.slice("seed-".length)) : null;

/* The Goal in a sentence, such as "a playoff spot", "a bye", or "the 3 seed". */
export function goalName(goal: GoalKey): string {
  const seed = seedOf(goal);
  if (seed !== null) return `the ${seed} seed`;
  return goal === "bye" ? "a bye" : "a playoff spot";
}

/* The Goal on a small label, such as "Spot", "Bye", or "Seed 3". */
export function goalShort(goal: GoalKey): string {
  const seed = seedOf(goal);
  if (seed !== null) return `Seed ${seed}`;
  return goal === "bye" ? "Bye" : "Spot";
}

/* The Goals of a page. A file written before The Race has none, so its page gives only the spot, from its playoff odds. */
export function pageGoals(page: SimPage): Record<string, GoalOdds> {
  if (Object.keys(page.goals).length > 0) return page.goals;
  return { spot: { odds: page.playoff, status: page.status } };
}

/* The Goal a page opens on. A file written before The Race opens on the spot. */
export const openGoal = (page: SimPage): GoalKey => (page.open_goal ?? "spot") as GoalKey;

/* The League board of the file. A file written before The Race gives the spot of each team from its playoff odds. */
export function boardOf(sim: WeekSim): BoardTeam[] {
  if (sim.board.length > 0) return sim.board;
  return Object.values(sim.teams).map((team) => ({
    roster_id: team.roster_id,
    goals: { spot: { odds: team.playoff, status: "open" as const } },
  }));
}

/* The odds of one Goal of a board team. A Goal the file does not hold reads 0. */
export const boardOdds = (team: BoardTeam, goal: GoalKey): number => team.goals[goal]?.odds ?? 0;

/* The board in odds order for `goal`. A tie keeps the order of the standings: wins, then Points For, then Points Against. */
export function boardOrder(sim: WeekSim, goal: GoalKey): BoardTeam[] {
  const record = (id: number) => sim.records[id] ?? [0, 0, 0, 0];
  const standings = (a: number, b: number) => {
    const [aw, , apf, apa = 0] = record(a);
    const [bw, , bpf, bpa = 0] = record(b);
    return bw - aw || bpf - apf || bpa - apa || a - b;
  };
  return [...boardOf(sim)].sort(
    (a, b) => boardOdds(b, goal) - boardOdds(a, goal) || standings(a.roster_id, b.roster_id),
  );
}

/* The Goals of the switch in a league: the spot, the bye when the league has one, and the seeds. */
export const hasBye = (sim: WeekSim) => sim.parameters.bye_count > 0;
