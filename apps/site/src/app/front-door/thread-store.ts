/**
 * The Thread of each team in local storage: the entries that the manager opened this fantasy week, oldest first.
 * The week of the latest build keys each Thread, so the Tuesday build starts an empty one (decision 05).
 */
import type { ThreadItem } from "./ask-thread";
import { personalResultSchema } from "./personal-stream";
import { tradeAnswerSchema } from "./trade-api";

// Its own key, so the Thread never mixes with Your team or the opened Topics.
export const THREAD_KEY = "cpc.thread";

/* One entry of the Thread that the browser keeps. A Topic entry names its Topic and its team, and its Answer reads
   from the published week. A miss, a cap line, and a note keep their lines. A question in flight and the passphrase card stay out,
   because they mean nothing after a reload. A trade Answer stays once it is whole, because a reread must cost nothing,
   and its steps in flight stay out. A free answer stays once it ends with its checked result, so a reload shows it
   with no new stream and no cost. A personal Answer stays once it ends checked, for the same reason. */
export type ThreadEntry =
  | Extract<ThreadItem, { kind: "topic" | "miss" | "cap" | "note" | "trade" }>
  | (Extract<ThreadItem, { kind: "free" }> & { result: NonNullable<Extract<ThreadItem, { kind: "free" }>["result"]> })
  | (Extract<ThreadItem, { kind: "personal" }> & { result: NonNullable<Extract<ThreadItem, { kind: "personal" }>["result"]> });

const KEPT = new Set(["topic", "miss", "cap", "note"]);

/* An entry that means something after a reload. A kept trade Answer must still read as one, so an old shape drops.
   A free answer stays only with its checked result. */
function kept(item: ThreadItem): item is ThreadEntry {
  if (item.kind === "trade") return tradeAnswerSchema.safeParse(item.answer).success;
  if (item.kind === "free") return item.result !== null;
  if (item.kind === "personal") return personalResultSchema.safeParse(item.result).success;
  return KEPT.has(item.kind);
}

type Threads = Record<string, { week: number; entries: ThreadEntry[] }>;

function readAll(): Threads {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(THREAD_KEY) ?? "{}");
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? (parsed as Threads) : {};
  } catch {
    // Blocked storage or a bad value reads as an empty Thread.
    return {};
  }
}

function writeAll(all: Threads): void {
  try {
    localStorage.setItem(THREAD_KEY, JSON.stringify(all));
  } catch {
    // The page still shows the Thread for this visit. The next load shows it empty.
  }
}

/* The Thread of one team in this week. A Thread of an older week reads as empty. */
export function getThread(teamId: number, week: number): ThreadEntry[] {
  const entry = readAll()[String(teamId)];
  if (!entry || entry.week !== week || !Array.isArray(entry.entries)) return [];
  return entry.entries.filter((item) => item && typeof item === "object" && kept(item));
}

/* Keep the Thread of one team for this week. Only the kinds that mean something after a reload stay. */
export function saveThread(teamId: number, week: number, items: ThreadItem[]): void {
  const entries = items.filter(kept);
  writeAll({ ...readAll(), [String(teamId)]: { week, entries } });
}

/* Clear empties the Thread of this week for one team. The Threads of the other teams stay. */
export function clearThread(teamId: number, week: number): void {
  writeAll({ ...readAll(), [String(teamId)]: { week, entries: [] } });
}
