/**
 * The turns of the Thread that each typed question carries to the API: the question and the shown answer text of each
 * earlier item, oldest first and newest last. A follow-up such as "cant choose mine" then reads like the whole question.
 */
import type { DoorAnswer } from "@/lib/data/front-door-data";
import type { ThreadItem } from "./ask-thread";
import { MISS_LEAD } from "./miss-card";
import { personalName } from "./thread";
import type { TradeAnswer } from "./trade-api";

/* One earlier turn: plain text only, so no data block, tool result, or step line leaves the browser. */
export type Turn = { question: string; answer: string };

// The hard limit of the turns of one question, as in chat_turns.py of the API: about 8,000 tokens at about 4
// characters per token. A follow-up needs only the last few turns, and a long Thread must not make each question cost
// more, so the oldest turns drop first. The API cuts past the same limit, so a client that skips this cut gains nothing.
export const TURNS_MAX_CHARS = 32_000;
// The caps of one turn on the API. A longer turn gets a 422, so the site cuts each turn to them first.
export const TURN_QUESTION_MAX = 300;
export const TURN_ANSWER_MAX = 2_000;

/* The turn of one item, or null for an item in flight. A free and a personal answer give their whole checked text,
   and a league Topic its text. Each other kind gives its one line, as the manager saw it. */
function turnOf(item: ThreadItem, answers: Record<number, DoorAnswer[]>, teamName: (team: number) => string | undefined): Turn | null {
  if (item.kind === "topic") {
    const answer = (answers[item.team] ?? []).find((candidate) => candidate.topic === item.key);
    if (!answer) return null;
    return { question: personalName(item, teamName(item.team)), answer: answer.text.join(" ") || answer.fact };
  }
  const line = turnLine(item, teamName);
  if (!line) return null;
  if (item.kind === "free" && item.result) return { question: line.name, answer: item.result.text };
  if (item.kind === "personal" && item.result) return { question: line.name, answer: item.result.text };
  return { question: line.name, answer: line.fact };
}

/* The one fact of each trade Answer: the Lean of a trade check, the count of the trade ideas, or the players to sell. */
function tradeFact(answer: TradeAnswer): string {
  switch (answer.kind) {
    case "check":
      return answer.document.lean;
    case "form":
      return "Pick the players on the Trade page";
    case "ideas": {
      const count = answer.document.trades.length;
      return count === 0 ? "No offer found" : count === 1 ? "1 offer" : `${count} offers`;
    }
    case "sell": {
      const names = answer.document.picks.map((pick) => pick.player.name);
      return names.length === 0 ? "No clear sell" : `Sell ${names.join(", ")}`;
    }
  }
}

/* The name and one plain fact of an item that is not a league Topic, or null for an item in flight: a question that
   routes, the passphrase field, or a stream that has not ended. A free and a personal answer use only the name here. */
function turnLine(item: Exclude<ThreadItem, { kind: "topic" }>, teamName: (team: number) => string | undefined): { name: string; fact: string } | null {
  switch (item.kind) {
    case "pending":
    case "passphrase":
      return null;
    case "trade":
      return item.answer ? { name: item.question, fact: tradeFact(item.answer) } : null;
    case "free":
      return item.result ? { name: item.question, fact: item.result.text } : null;
    case "personal":
      return item.result ? { name: personalName(item, teamName(item.team)), fact: item.result.text } : null;
    case "miss":
      return { name: item.question, fact: MISS_LEAD };
    case "cap":
    case "note":
      return { name: item.question, fact: item.line };
  }
}

/* The turns of `items`, each cut to the caps of the API, oldest first. The oldest turns drop first past the limit. */
export function threadTurns(items: ThreadItem[], answers: Record<number, DoorAnswer[]>, teamName: (team: number) => string | undefined): Turn[] {
  const turns = items
    .map((item) => turnOf(item, answers, teamName))
    .filter((turn): turn is Turn => turn !== null && turn.question.trim() !== "" && turn.answer.trim() !== "")
    .map((turn) => ({ question: turn.question.slice(0, TURN_QUESTION_MAX), answer: turn.answer.slice(0, TURN_ANSWER_MAX) }));
  const kept: Turn[] = [];
  let size = 0;
  for (const turn of turns.toReversed()) {
    size += turn.question.length + turn.answer.length;
    if (size > TURNS_MAX_CHARS) break;
    kept.unshift(turn);
  }
  return kept;
}

/* The turns before the item of `id`. A new question with no place yet reads every turn of the Thread. */
export function turnsBefore(
  entries: (ThreadItem & { id: number })[],
  id: number,
  answers: Record<number, DoorAnswer[]>,
  teamName: (team: number) => string | undefined,
): Turn[] {
  const at = entries.findIndex((entry) => entry.id === id);
  return threadTurns(at < 0 ? entries : entries.slice(0, at), answers, teamName);
}

