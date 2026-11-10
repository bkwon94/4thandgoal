/**
 * The client of the Suggestions route and of the key check of the API. The Suggestions bring the live fact of each
 * Topic and the Topics that are urgent for Your team. The key check says which kept personal Answers are stale.
 */
import { z } from "zod";
import { AskError, type AskTarget } from "./ask-api";
import { PERSONAL_TOPICS } from "./personal-stream";

/* The Suggestions of Your team: the fact of each Topic, and the urgent Topics, most urgent first. The API sends more,
   such as the lift of each Topic, for the log of a run. */
export const suggestionsSchema = z.object({
  facts: z.record(z.string(), z.string()),
  urgent: z.array(z.string()),
});
export type ServedSuggestions = z.infer<typeof suggestionsSchema>;

/* One personal Answer of the Thread, as the key check reads it. `team` is null for Your team. */
export type KeyItem = { topic: (typeof PERSONAL_TOPICS)[number]; roster_id: number; team: number | null; key: string };

/* The answer of the key check for one Answer: whether its key is current, and when the API kept it. */
export const currentSchema = z.object({
  answers: z.array(z.object({ key: z.string(), current: z.boolean(), kept_at: z.string().nullable() })),
});
export type KeyState = z.infer<typeof currentSchema>["answers"][number];

async function post<T>(target: AskTarget, passphrase: string, path: string, body: unknown, schema: z.ZodType<T>): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${target.url}/clients/${encodeURIComponent(target.client)}/${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-League-Passphrase": passphrase },
      body: JSON.stringify(body),
    });
  } catch {
    throw new AskError(0, "The call did not reach the site.");
  }
  if (!response.ok) throw new AskError(response.status, response.statusText);
  const parsed = schema.safeParse(await response.json());
  if (!parsed.success) throw new AskError(502, "The API sent an answer the site cannot read.");
  return parsed.data;
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

/* Whether the key of each personal Answer is still the key of its facts now. The check costs nothing. */
export async function checkCurrent(target: AskTarget, passphrase: string, answers: KeyItem[]): Promise<KeyState[]> {
  return (await post(target, passphrase, "personal/current", { answers }, currentSchema)).answers;
}

/* The stale line of an Answer, with the day that the API kept it. An Answer with no kept time still says the roster
   changed. */
export function staleLine(keptAt: string | null): string {
  const day = keptAt ? new Date(keptAt).toLocaleDateString("en-US", { weekday: "long" }) : null;
  return day && day !== "Invalid Date" ? `Your roster changed since ${day}.` : "Your roster changed.";
}
