/**
 * The client of the Suggestions route and of the key check of the API. The Suggestions bring the live fact of each
 * Topic and the Topics that are urgent for Your team. The key check says which kept personal and trade Answers are stale.
 */
import { z } from "zod";
import { type AskTarget, postClient, readBody } from "./ask-api";
import { kickoffText } from "./lineup-block";
import { PERSONAL_TOPICS } from "./personal-stream";

/* The Suggestions of Your team: the fact of each Topic, the urgent Topics, most urgent first, and the kickoff in epoch
   ms of each Topic whose fact is the next kickoff. The API sends more, such as the lift of each Topic, for the log of a
   run. */
export const suggestionsSchema = z.object({
  facts: z.record(z.string(), z.string()),
  urgent: z.array(z.string()),
  kickoffs: z.record(z.string(), z.number()).default({}),
});
export type ServedSuggestions = z.infer<typeof suggestionsSchema>;

/* One personal or trade Answer of the Thread, as the key check reads it. `team` is null for Your team. The team of a
   trade Answer is its partner, or null when it read no partner. */
export type KeyItem = { topic: (typeof PERSONAL_TOPICS)[number] | "trade_check" | "trade_ideas" | "sell_high"; roster_id: number; team: number | null; key: string };

/* The answer of the key check for one Answer: whether its key is current, and when the API kept it. */
export const currentSchema = z.object({
  answers: z.array(z.object({ key: z.string(), current: z.boolean(), kept_at: z.string().nullable() })),
});
export type KeyState = z.infer<typeof currentSchema>["answers"][number];

async function post<T>(target: AskTarget, passphrase: string, path: string, body: unknown, schema: z.ZodType<T>): Promise<T> {
  return readBody(await postClient(target, passphrase, path, body), schema);
}

/* The Suggestions of Your team for the order of the day and the opened Topics. On open, the API also builds the
   Answer of the top Suggestion when it is a personal Topic, so the first tap shows it at once. */
export function fetchSuggestions(
  target: AskTarget,
  passphrase: string,
  body: { roster_id: number; order: string[]; opened: Record<string, string> },
): Promise<ServedSuggestions> {
  return post(target, passphrase, "suggestions", body, suggestionsSchema);
}

/* Whether the key of each Answer is still the key of its data now. The check costs nothing. */
export async function checkCurrent(target: AskTarget, passphrase: string, answers: KeyItem[]): Promise<KeyState[]> {
  return (await post(target, passphrase, "personal/current", { answers }, currentSchema)).answers;
}

/* The fact that a Suggestion shows: the kickoff fact in the time zone of the browser, such as "Next kickoff Sun 10:00
   AM" in Los Angeles. The API writes the time in the league zone, so the opened Topics keep the fact of the API. */
export function shownFacts(facts: Record<string, string>, kickoffs: Record<string, number>): Record<string, string> {
  return { ...facts, ...Object.fromEntries(Object.entries(kickoffs).map(([key, ms]) => [key, `Next kickoff ${kickoffText(ms)}`])) };
}

/* The stale line of an Answer, with the day that the API kept it. An Answer with no kept time still says the roster
   changed. */
export function staleLine(keptAt: string | null): string {
  const day = keptAt ? new Date(keptAt).toLocaleDateString("en-US", { weekday: "long" }) : null;
  return day && day !== "Invalid Date" ? `Your roster changed since ${day}.` : "Your roster changed.";
}
