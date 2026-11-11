/**
 * A personal Topic as the Thread reads it: the data block from code, then the text and the check of the stream that the
 * free answer reads too. The block comes first in the stream, so the card shows the numbers before any word.
 */
import type { UIMessage } from "ai";
import { z } from "zod";
import { topicRowSchema, topicStatSchema } from "@/lib/data/topics-schema";
import { type FreeView, viewOf } from "./free-stream";

/* The 3 personal Topics, which the API builds live for one team. */
export const PERSONAL_TOPICS = ["weak_spots", "stack_up", "waiver_targets"] as const;
export type PersonalTopic = (typeof PERSONAL_TOPICS)[number];
export const isPersonal = (key: string): key is PersonalTopic => (PERSONAL_TOPICS as readonly string[]).includes(key);

/* The line of each personal Topic in "More". The fact of a personal Topic comes with its Answer, so the line says what
   it does. */
export const PERSONAL_LINES: Record<PersonalTopic, string> = {
  weak_spots: "Where your lineup is soft",
  stack_up: "Your roster against the league",
  waiver_targets: "Adds that fit your weak spots",
};

/* The data block of a personal Topic, in the shape of the data block of a league Topic. */
export const personalBlockSchema = z.object({
  topic: z.enum(PERSONAL_TOPICS),
  team: z.number(),
  fact: z.string(),
  stats: z.array(topicStatSchema),
  rows: z.array(topicRowSchema),
  // When the numbers are from, such as "as of today" for the live grade of How you stack up.
  as_of: z.string().optional(),
});
export type PersonalBlock = z.infer<typeof personalBlockSchema>;

/* The calm line of a cap from the API, with the closest Topics. Past a cap, the API makes no Claude call. */
export type PersonalCap = { line: string; closest: string[] };

/* What the stream shows so far: the view of the free answer, plus the data block, the key of the Answer, and the cap
   line in place of the text. */
export type PersonalView = FreeView & { block: PersonalBlock | null; key: string | null; cap: PersonalCap | null };

/* The checked Answer that the browser keeps: the data block, the text, and the key that the API kept it under. */
export const personalResultSchema = z.object({ block: personalBlockSchema, text: z.string(), key: z.string() });
export type PersonalResult = z.infer<typeof personalResultSchema>;

export function personalViewOf(message: UIMessage | undefined): PersonalView {
  let block: PersonalBlock | null = null;
  let key: string | null = null;
  let cap: PersonalCap | null = null;
  for (const part of message?.parts ?? []) {
    if (part.type === "data-block") {
      const parsed = personalBlockSchema.safeParse((part as { data: unknown }).data);
      if (parsed.success) block = parsed.data;
    } else if (part.type === "data-key") {
      const data = (part as { data: { key?: unknown } }).data;
      if (typeof data?.key === "string") key = data.key;
    } else if (part.type === "data-cap") {
      const data = (part as { data: { line?: unknown; closest?: unknown } }).data;
      if (typeof data?.line === "string" && Array.isArray(data.closest)) cap = { line: data.line, closest: data.closest.map(String) };
    }
  }
  return { ...viewOf(message), block, key, cap };
}
