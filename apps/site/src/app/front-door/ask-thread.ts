/**
 * The items of the Thread, and the hard rules that turn the route of a typed question into one item. The route comes
 * from the API. This module only maps it to what the Thread shows, with the copy of each line.
 */
import type { DoorAnswer } from "@/lib/data/front-door-data";
import { AskError, type AskAnswer } from "./ask-api";
import type { Turn } from "./chat-turns";
import type { TradeAnswer, TradeRead, TradeRequest } from "./trade-api";
import type { FreeResult } from "./free-stream";
import { type PersonalBlock, type PersonalResult, type PersonalTopic, isPersonal } from "./personal-stream";
import { topicName } from "./topics";

/* One item of the Thread. A topic item shows the league Answer of `team`, with the typed question or the Topic name as
   its bubble. A note is one calm line, with an optional Topic chip of `team` (null for Your team) and an optional retry.
   A cap item holds the calm line of a cap, from the API, with the closest Topics. A trade item holds the steps of a
   trade Topic while it works, then its whole Answer with the key of the rosters it read. A trade Answer kept from before
   the key has none, so it never reads as stale. A free answer streams while its result is null, and keeps its
   checked result once the stream ends. A personal Topic of `team` streams the same way from the API, with its data
   block first. A miss of a personal Topic keeps that data block. */
export type ThreadItem =
  | { kind: "topic"; key: string; team: number; question: string | null }
  | { kind: "pending"; question: string }
  | { kind: "miss"; question: string; closest: string[]; block?: PersonalBlock }
  | { kind: "cap"; question: string; line: string; closest: string[] }
  | { kind: "note"; question: string; line: string; topic: string | null; team: number | null; retry: boolean }
  | { kind: "trade"; mode: TradeMode; question: string; steps: string[]; answer: TradeAnswer | null; read?: TradeRead }
  | { kind: "free"; question: string; result: FreeResult | null }
  | { kind: "personal"; key: PersonalTopic; team: number; question: string | null; result: PersonalResult | null };

/* The trade Topics, by the key of the Topic, and the route of the API that answers each one. */
export type TradeMode = "check" | "ideas" | "sell";
export const TRADE_TOPICS: Record<string, TradeMode> = { trade_check: "check", trade_ideas: "ideas", sell_high: "sell" };
/* The key of each trade Topic by its mode. */
export const TRADE_TOPIC_OF: Record<TradeMode, string> = { check: "trade_check", ideas: "trade_ideas", sell: "sell_high" };

/* The other team of a whole trade Answer: the partner of a trade check, the partner that trade ideas asked for, or
   null for trade ideas over every team, sell high, and the form. */
export function tradePartner(answer: TradeAnswer): number | null {
  switch (answer.kind) {
    case "check":
      return answer.document.trade.sides.find((side) => side.roster_id !== answer.document.trade.asker)?.roster_id ?? null;
    case "ideas":
      return answer.document.trade_pair.partner?.roster_id ?? null;
    case "sell":
    case "form":
      return null;
  }
}

/* The request that runs a trade Answer again for Refresh: the same question, the same partner, or Your team. Trade
   ideas send the typed question again, so ideas around one player stay around him. A tapped Topic holds its name as
   its question, and sends no question. */
export function tradeRequestOf(entry: { mode: TradeMode; question: string; answer: TradeAnswer }, rosterId: number): TradeRequest {
  if (entry.mode === "check") return { mode: "check", question: entry.question, roster_id: rosterId };
  if (entry.mode === "ideas") {
    const partner = tradePartner(entry.answer);
    if (entry.question === topicName(TRADE_TOPIC_OF.ideas)) return { mode: "ideas", roster_id: rosterId, partner };
    return { mode: "ideas", roster_id: rosterId, partner, question: entry.question };
  }
  return { mode: "sell", roster_id: rosterId };
}

/* The request of a typed question that routes to trade ideas: the team that the question names as the partner, never
   Your team, with the typed question and the earlier turns of the Thread. */
export function ideasRequestOf(route: { team: number | null }, question: string, rosterId: number, turns: Turn[]): TradeRequest {
  const partner = route.team !== null && route.team !== rosterId ? route.team : null;
  return { mode: "ideas", roster_id: rosterId, partner, question, turns };
}

/* The line of each trade Topic in "More". A fact of the API takes its place when the API serves one. */
export const TRADE_LINES: Record<string, string> = {
  trade_check: "Name a trade, get the read",
  trade_ideas: "Offers for your weak spots",
  sell_high: "Who to move while his price is up",
};

export const REFUSE_LINE = "I can't answer that. Ask about your team, another team, or the league.";
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

/* The item of a failed call. A 429 says how long to wait. Each other failure is an error, never a miss, so it offers a
   retry. The front door takes a wrong passphrase to the passphrase modal before it calls this. */
export function itemOfError(error: unknown, question: string): ThreadItem {
  if (error instanceof AskError && error.status === 429) {
    const wait = error.retryAfter ? `Try again in ${error.retryAfter} seconds.` : "Try again in a minute.";
    return { kind: "note", question, line: `That is a lot of questions at once. ${wait}`, topic: null, team: null, retry: false };
  }
  return { kind: "note", question, line: RETRY_LINE, topic: null, team: null, retry: true };
}
