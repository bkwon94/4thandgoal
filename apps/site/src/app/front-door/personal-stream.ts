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
});
export type PersonalBlock = z.infer<typeof personalBlockSchema>;

/* What the stream shows so far: the view of the free answer, plus the data block and the key of the Answer. */
export type PersonalView = FreeView & { block: PersonalBlock | null; key: string | null };

/* The checked Answer that the browser keeps: the data block, the text, and the key that the API kept it under. */
export const personalResultSchema = z.object({ block: personalBlockSchema, text: z.string(), key: z.string() });
export type PersonalResult = z.infer<typeof personalResultSchema>;

export function personalViewOf(message: UIMessage | undefined): PersonalView {
  let block: PersonalBlock | null = null;
  let key: string | null = null;
  for (const part of message?.parts ?? []) {
    if (part.type === "data-block") {
      const parsed = personalBlockSchema.safeParse((part as { data: unknown }).data);
      if (parsed.success) block = parsed.data;
    } else if (part.type === "data-key") {
      const data = (part as { data: { key?: unknown } }).data;
      if (typeof data?.key === "string") key = data.key;
    }
  }
  return { ...viewOf(message), block, key };
}
