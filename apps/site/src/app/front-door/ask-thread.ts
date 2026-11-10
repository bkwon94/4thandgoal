/**
 * The items of the Thread, and the hard rules that turn the route of a typed question into one item. The route comes
 * from the API. This module only maps it to what the Thread shows, with the copy of each line.
 */
import type { DoorAnswer } from "@/lib/data/front-door-data";
import { AskError, type AskAnswer } from "./ask-api";
import type { TradeAnswer } from "./trade-api";
import type { FreeResult } from "./free-stream";
import { type PersonalResult, type PersonalTopic, isPersonal } from "./personal-stream";
import { topicName } from "./topics";

/* One item of the Thread. A topic item shows the league Answer of `team`, with the typed question or the Topic name as
   its bubble. A note is one calm line, with an optional Topic chip of `team` (null for Your team) and an optional retry.
   A cap item holds the calm line of a cap, from the API, with the closest Topics. A trade item holds the steps of a
   trade Topic while it works, then its whole Answer. A free answer streams while its result is null, and keeps its
   checked result once the stream ends. A personal Topic of `team` streams the same way from the API, with its data
   block first. */
export type ThreadItem =
  | { kind: "topic"; key: string; team: number; question: string | null }
  | { kind: "pending"; question: string }
  | { kind: "passphrase"; question: string; wrong: boolean }
  | { kind: "miss"; question: string; closest: string[] }
  | { kind: "cap"; question: string; line: string; closest: string[] }
  | { kind: "note"; question: string; line: string; topic: string | null; team: number | null; retry: boolean }
  | { kind: "trade"; mode: TradeMode; question: string; steps: string[]; answer: TradeAnswer | null }
  | { kind: "free"; question: string; result: FreeResult | null }
  | { kind: "personal"; key: PersonalTopic; team: number; question: string | null; result: PersonalResult | null };

/* The trade Topics, by the key of the Topic, and the route of the API that answers each one. */
export type TradeMode = "check" | "ideas" | "sell";
export const TRADE_TOPICS: Record<string, TradeMode> = { trade_check: "check", trade_ideas: "ideas", sell_high: "sell" };
/* The line of each trade Topic in "More". A fact of the API takes its place when the API serves one. */
export const TRADE_LINES: Record<string, string> = {
  trade_check: "Name a trade, get the read",
  trade_ideas: "Offers for your weak spots",
  sell_high: "Who to move while his price is up",
};

export const REFUSE_LINE = "That is not a question the front door answers. Ask about your team, another team, or the league.";
export const RETRY_LINE = "The question did not go through. Ask again.";

/* The item of a route. A Topic route opens the Answer of the team that the question names, else of Your team. A Topic
   with no Answer in this build, such as a live Topic, says that it opens soon. */
export function itemOfRoute(
  route: AskAnswer,
  question: string,
  yourTeam: number,
  answers: Record<number, DoorAnswer[]>,
): ThreadItem {
  switch (route.route) {
    case "topic": {
      const team = route.team ?? yourTeam;
      const key = route.topic ?? "";
      // A personal Topic builds live on the API, for the team that the question names.
      if (isPersonal(key)) return { kind: "personal", key, team, question, result: null };
      const ready = (answers[team] ?? []).some((answer) => answer.topic === key);
      return ready
        ? { kind: "topic", key, team, question }
        : { kind: "note", question, line: `${topicName(key)} opens here soon.`, topic: null, team: null, retry: false };
    }
    case "free":
      // The stream of the free answer brings its own Suggestion after the check, so the route adds none here.
      return { kind: "free", question, result: null };
    case "miss":
      return { kind: "miss", question, closest: route.closest };
    case "refuse":
      return { kind: "note", question, line: REFUSE_LINE, topic: null, team: null, retry: false };
    case "cap":
      // The API writes the line of each cap, so the site never says a cause or a date that the API did not check.
      return { kind: "cap", question, line: route.line ?? "", closest: route.closest };
  }
}

/* The item of a failed call. A wrong passphrase asks for it again. A 429 says how long to wait. Each other failure is
   an error, never a miss, so it offers a retry. */
export function itemOfError(error: unknown, question: string): ThreadItem {
  if (error instanceof AskError && error.status === 401) return { kind: "passphrase", question, wrong: true };
  if (error instanceof AskError && error.status === 429) {
    const wait = error.retryAfter ? `Try again in ${error.retryAfter} seconds.` : "Try again in a minute.";
    return { kind: "note", question, line: `That is a lot of questions at once. ${wait}`, topic: null, team: null, retry: false };
  }
  return { kind: "note", question, line: RETRY_LINE, topic: null, team: null, retry: true };
}
