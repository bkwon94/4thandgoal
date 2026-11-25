/**
 * The copy of a Clinch line of the League board and the team sheet (decision 06), such as "Clinches a spot with a win and a
 * median win." Each takes data from the sim file and returns text, so the board, the sheet, and the tests read one wording.
 */
import type { ClinchLine, ClinchWay, WeekSim } from "../schema/sim-types";
import { nameOf } from "./format";

/* The most results of other teams that a line names before "and N more results", so it fits a phone (decision 06). */
const OTHERS_SHOWN = 2;

/* A list in a sentence: "a", "a and b", or "a, b, and c". */
function listText(items: string[]): string {
  if (items.length <= 2) return items.join(" and ");
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

/* The results of the team itself. With a median game, a game result with any median result reads "any win" or "any loss". */
function ownResults(way: ClinchWay, medianGame: boolean): string[] {
  const parts: string[] = [];
  if (way.game !== null) {
    const result = way.game === "win" ? "win" : "loss";
    parts.push(medianGame && way.median === null ? `any ${result}` : `a ${result}`);
  }
  if (way.median !== null) parts.push(way.median === "above" ? "a median win" : "a median miss");
  return parts;
}

/* A result of another team, such as "a Teez Nuts loss to Bo Girds" or "an Omarion Himpton median miss". A name that starts
   with "The" takes no article before it, so it reads "a median win by The Blue Tent". */
function otherResult(sim: WeekSim, other: ClinchWay["others"][number]): string {
  const team = nameOf(sim, other.kind === "game" ? other.loser : other.roster_id);
  const result =
    other.kind === "game" ? "loss" : `median ${other.median === "above" ? "win" : "miss"}`;
  const to = other.kind === "game" ? ` to ${nameOf(sim, other.winner)}` : "";
  if (/^the\s/i.test(team)) return `a ${result} by ${team}${to}`;
  return `${/^[aeiou]/i.test(team) ? "an" : "a"} ${team} ${result}${to}`;
}

/* The sentence of one way of a Clinch line, with the Goal named. It names at most `shown` results of other teams, then
   "and N more results". */
function wayText(sim: WeekSim, line: ClinchLine, way: ClinchWay, shown: number): string {
  const head =
    line.status === "in"
      ? `Clinches ${line.goal === "spot" ? "a spot" : "a bye"}`
      : line.goal === "spot"
        ? "Out of the playoffs"
        : "Out of the bye race";
  const others = way.others.map((other) => otherResult(sim, other));
  const more = others.length - shown;
  const parts = [
    ...ownResults(way, sim.parameters.median_game),
    ...others.slice(0, shown),
    ...(more > 0 ? [`${more} more ${more === 1 ? "result" : "results"}`] : []),
  ];
  const text =
    parts.length === 0 ? `${head} whatever happens this week` : `${head} with ${listText(parts)}`;
  // A team name can end in a period, such as "Puka Deez...", and the sentence then takes no second one.
  return text.endsWith(".") ? text : `${text}.`;
}

/* The sentence of a Clinch line on the board: its most likely way, with the Goal named. */
export const clinchText = (sim: WeekSim, line: ClinchLine): string =>
  wayText(sim, line, line.ways[0], OTHERS_SHOWN);

/* The sentences of the team sheet: each stored way of a Clinch line, most likely first, with every result named. */
export const clinchWayTexts = (sim: WeekSim, line: ClinchLine): string[] =>
  line.ways.map((way) => wayText(sim, line, way, Infinity));

/* The Clinch lines of a team for the Goal of the view. A Seed Goal has none (decision 06). */
export const clinchLinesOf = (lines: ClinchLine[], goal: string): ClinchLine[] =>
  lines.filter((line) => line.goal === goal);
