/**
 * The client of the trade Topics of the API, the trade check, trade ideas, and sell high, with the Zod schema of each
 * part. The API streams a plain step for each stage, then the whole Answer, as `data:` lines of an event stream.
 */
import { z } from "zod";
import { analyzeResponseSchema, asOfSchema, bulletSchema, findResponseSchema, tradedPlayerSchema } from "@cpc/analyzer/lib/schemas/api";
import { AskError, type AskTarget, postClient, statusError } from "./ask-api";

/* The form of the Trade page for an unsure pick: Your team, the partner of a sure player, and each sure player. */
export const tradeFormSchema = z.object({
  asker: z.number(),
  partner: z.number().nullable(),
  gives: z.array(z.string()),
  gets: z.array(z.string()),
});
export type TradeForm = z.infer<typeof tradeFormSchema>;

/* The sell high document: Your team, and each player of its roster to sell with the headline and the Bullets of why,
   or the plain line of a roster with no clear sell. */
export const sellHighSchema = z.object({
  season: z.number(),
  team: z.object({ roster_id: z.number(), team: z.string() }),
  picks: z.array(z.object({ player: tradedPlayerSchema, headline: z.string(), bullets: z.array(bulletSchema) })),
  empty: z.string().nullable(),
  as_of: asOfSchema,
});
export type SellHigh = z.infer<typeof sellHighSchema>;

/* The whole Answer of a trade Topic: the read of a trade check, the form of an unsure pick, the trade ideas, or the
   players to sell. */
export const tradeAnswerSchema = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("check"), document: analyzeResponseSchema }),
  z.object({ kind: z.literal("form"), form: tradeFormSchema }),
  z.object({ kind: z.literal("ideas"), document: findResponseSchema }),
  z.object({ kind: z.literal("sell"), document: sellHighSchema }),
]);
export type TradeAnswer = z.infer<typeof tradeAnswerSchema>;

/* The key of the rosters that a trade Answer read, and the time of the read. The key check of the API compares it with
   the rosters now, so a trade or a claim on one of them makes the Answer stale. */
export const tradeReadSchema = z.object({ key: z.string(), at: z.string() });
export type TradeRead = z.infer<typeof tradeReadSchema>;

/* One part of the stream that the site reads. The API sends more parts, such as the player picks, for the evidence. */
const partSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("data-step"), data: z.object({ line: z.string() }) }),
  z.object({ type: z.literal("data-key"), data: tradeReadSchema }),
  z.object({ type: z.literal("data-answer"), data: tradeAnswerSchema }),
  z.object({ type: z.literal("data-error"), data: z.object({ status: z.number(), line: z.string() }) }),
  z.object({ type: z.literal("data-cap"), data: z.object({ cap: z.enum(["team", "league"]), line: z.string() }) }),
]);

/* What the stream gives the Thread, part by part. The key of the read comes before the Answer. A cap gives its calm
   line in place of the Answer. */
export type TradeEvents = {
  onStep: (line: string) => void;
  onKey: (read: TradeRead) => void;
  onAnswer: (answer: TradeAnswer) => void;
  onCap: (line: string) => void;
};

/* The body of each route: the typed question of a trade check, or the partner that a question of trade ideas names
   with the typed question. A tap of trade ideas sends no question. */
export type TradeRequest =
  | { mode: "check"; question: string; roster_id: number }
  | { mode: "ideas"; roster_id: number; partner: number | null; question?: string }
  | { mode: "sell"; roster_id: number };

/* The path of the route of each mode, after /clients/<slug>/. */
const ROUTE_PATH: Record<TradeRequest["mode"], string> = { check: "trade-check", ideas: "trade-ideas", sell: "sell-high" };

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
      if (part.data.type === "data-key") events.onKey(part.data.data);
      if (part.data.type === "data-error") throw new AskError(part.data.data.status, part.data.data.line);
      if (part.data.type === "data-answer") {
        answered = true;
        events.onAnswer(part.data.data);
      }
      if (part.data.type === "data-cap") {
        answered = true;
        events.onCap(part.data.data.line);
      }
    }
    if (done) return answered;
  }
}

/* Send one trade Topic and read its stream. A failed call or a stream with no Answer and no cap line throws an
   AskError. */
export async function streamTrade(target: AskTarget, passphrase: string, request: TradeRequest, events: TradeEvents): Promise<void> {
  const { mode, ...body } = request;
  const response = await postClient(target, passphrase, ROUTE_PATH[mode], body);
  if (!response.body) throw statusError(response);
  let answered: boolean;
  try {
    answered = await readParts(response.body, events);
  } catch (error) {
    if (error instanceof AskError) throw error;
    throw new AskError(502, "The API sent an answer the site cannot read.");
  }
  if (!answered) throw new AskError(502, "The stream ended with no Answer.");
}
