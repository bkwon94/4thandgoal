/**
 * The client of the trade Topics of the API, the trade check and trade ideas, with the Zod schema of each part. The
 * API streams a plain step for each stage, then the whole Answer, as `data:` lines of an event stream.
 */
import { z } from "zod";
import { analyzeResponseSchema, findResponseSchema } from "@cpc/analyzer/lib/schemas/api";
import { AskError, type AskTarget } from "./ask-api";

/* The form of the Trade page for an unsure pick: Your team, the partner of a sure player, and each sure player. */
export const tradeFormSchema = z.object({
  asker: z.number(),
  partner: z.number().nullable(),
  gives: z.array(z.string()),
  gets: z.array(z.string()),
});
export type TradeForm = z.infer<typeof tradeFormSchema>;

/* The whole Answer of a trade Topic: the read of a trade check, the form of an unsure pick, or the trade ideas. */
export const tradeAnswerSchema = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("check"), document: analyzeResponseSchema }),
  z.object({ kind: z.literal("form"), form: tradeFormSchema }),
  z.object({ kind: z.literal("ideas"), document: findResponseSchema }),
]);
export type TradeAnswer = z.infer<typeof tradeAnswerSchema>;

/* One part of the stream that the site reads. The API sends more parts, such as the player picks, for the evidence. */
const partSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("data-step"), data: z.object({ line: z.string() }) }),
  z.object({ type: z.literal("data-answer"), data: tradeAnswerSchema }),
  z.object({ type: z.literal("data-error"), data: z.object({ status: z.number(), line: z.string() }) }),
]);

/* What the stream gives the Thread, part by part. */
export type TradeEvents = { onStep: (line: string) => void; onAnswer: (answer: TradeAnswer) => void };

/* The body of each route: the typed question of a trade check, or the partner that a question of trade ideas names. */
export type TradeRequest =
  | { mode: "check"; question: string; roster_id: number }
  | { mode: "ideas"; roster_id: number; partner: number | null };

/* Read each `data:` line of `body` and give its part to `events`. A line of no known type, such as the start, is
   skipped. An error part throws an AskError with its status and its line. */
async function readParts(body: ReadableStream<Uint8Array>, events: TradeEvents): Promise<boolean> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let answered = false;
  for (;;) {
    const { value, done } = await reader.read();
    buffer += value ? decoder.decode(value, { stream: !done }) : "";
    const blocks = buffer.split("\n\n");
    buffer = done ? "" : (blocks.pop() ?? "");
    for (const block of blocks) {
      const line = block.trim();
      if (!line.startsWith("data: ") || line === "data: [DONE]") continue;
      const part = partSchema.safeParse(JSON.parse(line.slice("data: ".length)));
      if (!part.success) continue;
      if (part.data.type === "data-step") events.onStep(part.data.data.line);
      if (part.data.type === "data-error") throw new AskError(part.data.data.status, part.data.data.line);
      if (part.data.type === "data-answer") {
        answered = true;
        events.onAnswer(part.data.data);
      }
    }
    if (done) return answered;
  }
}

/* Send one trade Topic and read its stream. A failed call or a stream with no Answer throws an AskError. */
export async function streamTrade(target: AskTarget, passphrase: string, request: TradeRequest, events: TradeEvents): Promise<void> {
  const { mode, ...body } = request;
  let response: Response;
  try {
    response = await fetch(`${target.url}/clients/${encodeURIComponent(target.client)}/trade-${mode}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-League-Passphrase": passphrase },
      body: JSON.stringify(body),
    });
  } catch {
    throw new AskError(0, "The question did not reach the site.");
  }
  if (!response.ok || !response.body) {
    const seconds = Number(response.headers.get("Retry-After"));
    throw new AskError(response.status, response.statusText, Number.isFinite(seconds) && seconds > 0 ? seconds : undefined);
  }
  let answered: boolean;
  try {
    answered = await readParts(response.body, events);
  } catch (error) {
    if (error instanceof AskError) throw error;
    throw new AskError(502, "The API sent an answer the site cannot read.");
  }
  if (!answered) throw new AskError(502, "The stream ended with no Answer.");
}
