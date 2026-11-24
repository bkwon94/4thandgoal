/**
 * The words of the Finish list and its Paths, the copy of decision 06 of playoff-paths: the name and the line of a Finish,
 * the conditions of a Path, and the sentence of each case. Each takes data from the page block and returns a string.
 */
import type {
  Finish,
  FinishPath,
  PlanWeek,
  ScoreToBeat,
  WeekPlan,
  WeekSim,
} from "../schema/sim-types";
import { nameOf, recordText } from "./format";
import { type GoalKey, seedOf } from "./goals";

/* The name of a Finish by its wins and losses in the results left, such as "4-2". */
export const finishName = (finish: Finish, winsLeft: number) =>
  `${finish.more_wins}-${winsLeft - finish.more_wins}`;

/* The line of a Finish, such as "4-2 · ends 15-13 · 26% likely". */
export const finishLine = (finish: Finish, winsLeft: number) =>
  `${finishName(finish, winsLeft)} · ends ${recordText(finish.record)} · ${Math.round(finish.chance)}% likely`;

/* What the Goal gives, said of Your team or of another team, such as "You're in" or "They get a bye". */
function reach(goal: GoalKey, mine: boolean): string {
  const who = mine ? "You" : "They";
  const seed = seedOf(goal);
  if (seed !== null) return `${who} get the ${seed} seed`;
  if (goal === "bye") return `${who} get a bye`;
  return mine ? "You're in" : "They're in";
}

/* The sentence of a Finish at 99.5% or more. */
export const sureText = (goal: GoalKey, mine: boolean) =>
  `${reach(goal, mine)} whatever the others do.`;

/* The sentence of a Finish under 0.5%. */
export function noneText(goal: GoalKey): string {
  const seed = seedOf(goal);
  if (seed !== null) return `No way to the ${seed} seed at this record.`;
  return goal === "bye" ? "No way to a bye at this record." : "No way in at this record.";
}

/* The sentence of a Finish with no Path to show, such as a Finish of too few runs. */
export const openText = "No Path to show at this record.";

/* The conditions of a Path as one sentence, such as "If Omarion Himpton ends 14-14 or worse, 💿 🐑 ends 16-12 or worse,
   and Bengals Buddies ends 15-13 or worse." */
export function conditionsText(sim: WeekSim, path: FinishPath): string {
  const parts = path.conditions.map(
    (condition) =>
      `${nameOf(sim, condition.roster_id)} ends ${recordText(condition.record)} or worse`,
  );
  if (parts.length === 1) return `If ${parts[0]}.`;
  if (parts.length === 2) return `If ${parts[0]} and ${parts[1]}.`;
  return `If ${parts.slice(0, -1).join(", ")}, and ${parts.at(-1)}.`;
}

/* How often a Path happens and the odds of the Goal on it, such as "Happens 17% · you're in 99%." */
export function happensText(path: FinishPath, goal: GoalKey, mine: boolean): string {
  const odds = reach(goal, mine);
  return `Happens ${Math.round(path.chance)}% · ${odds[0].toLowerCase()}${odds.slice(1)} ${path.odds}%.`;
}

/* The header of a Week plan with the odds of "Try it", such as "Your plan to 15-13 · you're in 81%". */
export function planHeader(finish: Finish, plan: WeekPlan, goal: GoalKey, mine: boolean): string {
  const odds = reach(goal, mine);
  return `${mine ? "Your" : "Their"} plan to ${recordText(finish.record)} · ${odds[0].toLowerCase()}${odds.slice(1)} ${plan.odds}%`;
}

/* The order line of a plan whose order does not matter, such as "Any 4 wins of your 6 work. This is the most common
   order." Null when the order matters. */
export function orderLine(
  finish: Finish,
  plan: WeekPlan,
  winsLeft: number,
  mine: boolean,
): string | null {
  if (!plan.any_order) return null;
  const wins = finish.more_wins;
  return `Any ${wins} ${wins === 1 ? "win" : "wins"} of ${mine ? "your" : "their"} ${winsLeft} ${wins === 1 ? "works" : "work"}. This is the most common order.`;
}

/* The result of one week of a plan as a sentence, such as "Win and beat the median." or "Lose, but beat the median." */
export function planResult(week: PlanWeek): string {
  const win = week.game === "win";
  if (week.median === null) return win ? "Win." : "Lose.";
  if (week.median === "above")
    return win ? "Win and beat the median." : "Lose, but beat the median.";
  return win ? "Win, but miss the median." : "Lose and miss the median.";
}

/* The Score to beat of one week of a plan, such as "Score 109 to win, 127 to be sure. Score 107 to beat the median, 114
   to be sure." A loss names no score for the game, and a median miss names none for the median. */
export function planScores(week: PlanWeek, beat: ScoreToBeat | undefined): string | null {
  if (beat === undefined) return null;
  const parts: string[] = [];
  if (week.game === "win") parts.push(`Score ${beat.win} to win, ${beat.win_sure} to be sure.`);
  if (week.median === "above" && beat.median !== null)
    parts.push(`Score ${beat.median} to beat the median, ${beat.median_sure} to be sure.`);
  return parts.length > 0 ? parts.join(" ") : null;
}

/* The games to root for in one week of a plan, such as "Immaculate Concepcion over Bengals Buddies · Nico Collinsizer
   over Omarion Himpton". Null with none. */
export function planRootFor(sim: WeekSim, week: PlanWeek): string | null {
  if (week.root_for.length === 0) return null;
  return week.root_for
    .map((game) => `${nameOf(sim, game.winner)} over ${nameOf(sim, game.loser)}`)
    .join(" · ");
}
