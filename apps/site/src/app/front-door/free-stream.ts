/**
 * The free answer as the Thread reads it: the parts of the streamed message of useChat turned into the steps, the
 * texts, the check, and the Suggestion or the honest miss. It holds the plain line of each step, and no tool name shows.
 */
import type { UIMessage } from "ai";

/* One tool call as a step: its plain line, and whether its result is in. */
export type FreeStep = { line: string; done: boolean };

/* The check of the text: "checking" after the last word, "fixing" before the rewrite, then "checked" or "failed". */
export type CheckState = "checking" | "fixing" | "checked" | "failed";

/* What the stream shows so far. `first` is the text before a rewrite, and `second` the text of the rewrite. Each text
   is empty until its check passes. */
export type FreeView = {
  steps: FreeStep[];
  first: string;
  second: string | null;
  check: CheckState | null;
  suggestion: { topic: string; team: number | null } | null;
  closest: string[] | null;
};

/* The final free answer that the browser keeps: the steps, the checked text, and the Suggestion of a half fit. */
export type FreeResult = { steps: string[]; text: string; suggestion: { topic: string; team: number | null } | null };

/* The plain line of one tool call, from its name and its input. A tool that this build does not know reads as the
   league data, so no internal name ever shows (AT-19). */
export function stepLine(tool: string, input: unknown): string {
  const args = (input && typeof input === "object" ? input : {}) as Record<string, unknown>;
  const week = typeof args.week === "number" ? args.week : null;
  const named = (key: string) => (typeof args[key] === "string" ? (args[key] as string) : null);
  switch (tool) {
    case "standings":
      return "Reading the standings";
    case "week_results":
      return week ? `Reading week ${week}` : "Reading the week";
    case "week_moves":
      return week ? `Reading the moves of week ${week}` : "Reading the moves of the week";
    case "season_moves":
      return "Reading every move of the season";
    case "team_roster":
      return named("team") ? `Reading the roster of ${named("team")}` : "Reading a roster";
    case "player_log":
      return named("player") ? `Reading the game log of ${named("player")}` : "Reading a game log";
    default:
      return "Reading the league data";
  }
}

type Part = UIMessage["parts"][number];

/* The tool name of a tool part: "tool-<name>" for a static tool, and `toolName` for a dynamic one. */
function toolOf(part: Part): { name: string; input: unknown; done: boolean } | null {
  if (part.type === "dynamic-tool") return { name: part.toolName, input: part.input, done: part.state === "output-available" || part.state === "output-error" };
  if (!part.type.startsWith("tool-")) return null;
  const tool = part as Part & { input?: unknown; state?: string };
  return { name: part.type.slice("tool-".length), input: tool.input, done: tool.state === "output-available" || tool.state === "output-error" };
}

function dataOf<T>(part: Part, kind: string): T | null {
  return part.type === `data-${kind}` ? ((part as { data: unknown }).data as T) : null;
}

/* The view of the assistant message of the stream. The data part "fix" splits the first text from the rewrite. A text
   shows only once its check passes, so no word that the manager reads is ever pulled back (H10). The API sends a text
   only after its check, and the view holds it back too, so a stream in the other order shows no early word. */
export function viewOf(message: UIMessage | undefined): FreeView {
  const view: FreeView = { steps: [], first: "", second: null, check: null, suggestion: null, closest: null };
  for (const part of message?.parts ?? []) {
    const tool = toolOf(part);
    if (tool) view.steps.push({ line: stepLine(tool.name, tool.input), done: tool.done });
    else if (part.type === "text") {
      if (view.second === null) view.first += part.text;
      else view.second += part.text;
    } else if (part.type === "data-fix") view.second = "";
    else {
      const check = dataOf<{ state: CheckState }>(part, "check");
      if (check) view.check = check.state;
      const suggestion = dataOf<{ topic: string; team: number | null }>(part, "suggestion");
      if (suggestion) view.suggestion = suggestion;
      const miss = dataOf<{ closest: string[] }>(part, "miss");
      if (miss) view.closest = miss.closest;
    }
  }
  if (view.second !== null || view.check !== "checked") view.first = "";
  if (view.second !== null && view.check !== "checked") view.second = "";
  return view;
}

/* The text that the manager reads now: the rewrite once it starts, else the first text. */
export const shownText = (view: FreeView) => (view.second ?? view.first).trim();

/* A kept Answer of the API comes back whole: its text with no step of a model run before it, and its check. A live
   run starts each text with a step. */
export const isKept = (message: UIMessage | undefined) =>
  !!message?.parts.some((part) => part.type === "text") && !message.parts.some((part) => part.type === "step-start");

/* The time that each held state of a view first showed: "Checking" of the first text, the fixing line, and "Checking"
   of the rewrite. */
export type Pace = { checkFirst: number | null; fixing: number | null; checkSecond: number | null };
export const newPace = (): Pace => ({ checkFirst: null, fixing: null, checkSecond: null });

/* The view that the manager sees at `now`. A fast check sends "checking" and its end in one read, so the end waits
   until "Checking" held for `hold` ms. The rewrite waits in the same way until the fixing line held for `hold` ms
   (AT-20, AT-21). A held view shows no text, so the text shows with "Checked". `pace` keeps the time that each held
   state first showed. `wake` is the time of the next change, or
   null when the view shows the stream as it is. */
export function pacedView<V extends FreeView>(view: V, pace: Pace, now: number, hold: number): { view: V; wake: number | null } {
  const held = (key: keyof Pace) => {
    pace[key] ??= now;
    return now - pace[key] < hold ? pace[key] + hold : null;
  };
  if (view.check === null && view.second === null) return { view, wake: null };
  // "Checking" of the first text holds before its end shows: "Checked", or the fade to the fixing line.
  const firstWake = held("checkFirst");
  if (firstWake !== null && (view.second !== null || view.check !== "checking")) return { view: { ...view, first: "", second: null, check: "checking" }, wake: firstWake };
  if (view.second === null) return { view, wake: null };
  // The fixing line holds before the rewrite shows.
  const fixingWake = held("fixing");
  if (fixingWake !== null) return { view: { ...view, second: "", check: "fixing" }, wake: fixingWake };
  // "Checking" of the rewrite holds before "Checked" shows.
  if (view.check !== "checking" && view.check !== "checked") return { view, wake: null };
  const secondWake = held("checkSecond");
  if (secondWake !== null && view.check === "checked") return { view: { ...view, second: "", check: "checking" }, wake: secondWake };
  return { view, wake: null };
}
