/**
 * The words and numbers of the sim page: a team name, a record, an odds number with its "about", and the name of a result.
 * Each takes data from the page block and returns a string, so the parts and the tests read one wording.
 */
import type { WeekSim } from "../schema/sim-types";

/* The small caps label of the site, such as "PLAYOFF ODDS". */
export const LABEL = "font-mono text-label leading-tight font-bold tracking-caps uppercase";

export const nameOf = (sim: WeekSim, id: number) => sim.names[id] ?? `Team ${id}`;

/* The record as the site writes it, such as "11-9". */
export const recordText = ([wins, losses]: [number, number]) => `${wins}-${losses}`;

/* The press of each control of the page: the press of the look, and a focus ring for the keyboard. */
export const PRESS = "press outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink";

/* A card of the page. Its radius is the radius of a tile plus its padding, so the corners nest. */
export const CARD = "flex min-w-0 flex-col gap-sp-2 rounded-card border border-rule bg-card p-sp-3";

/* An odds number in whole percent. A number with the "about" flag rests on few runs, so it reads "about 58%".
   A null number means no run had the result. */
export function oddsText(value: number | null, about = false): string {
  if (value === null) return "–";
  return about ? `about ${value}%` : `${value}%`;
}

/* The weeks of the page block name a result by its game and its median. */
type Result = { game: "win" | "loss"; median: "above" | "below" | null };

/* The short name of one result, such as "Win, beat median". With no median game, it is "Win" or "Lose". */
export function resultName({ game, median }: Result): string {
  const head = game === "win" ? "Win" : "Lose";
  if (median === null) return head;
  return `${head}, ${median === "above" ? "beat" : "miss"} median`;
}

/* How likely a result is, in whole percent, such as "24% likely". */
export const chanceText = (chance: number) => `${Math.round(chance)}% likely`;

/* The wins a result adds: one for the game, one for the median. */
export const winsText = (wins: number) => (wins === 0 ? "No wins" : wins === 1 ? "+1 win" : `+${wins} wins`);
