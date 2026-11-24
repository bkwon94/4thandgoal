/**
 * The client for the site API. Each call sends the league passphrase in the X-League-Passphrase header.
 * Each call goes to the routes of one client, /clients/<slug>/. A failed call throws an ApiError, and the caller decides.
 */
import { z, type ZodType } from "zod";
import type { AnalyzeResponse, FindResponse, FinderTrade } from "./analyze-types";
import {
  analyzeResponseSchema,
  findResponseSchema,
  finderTradeSchema,
  playerSchema,
  teamSchema,
  teamsResponseSchema,
  tradeWireResponseSchema,
  wireTradeSchema,
} from "./schemas/api";

/* The API that a call goes to: its base URL, the slug of the client, and the season the routes read.
   The page builds it from the config of the app, so the package reads no env. */
export type ApiTarget = { url: string; client: string; season: number };

/* The base of the routes of the client of the target. */
function clientBase(target: ApiTarget): string {
  return `${target.url}/clients/${encodeURIComponent(target.client)}`;
}

export type TeamPlayer = z.infer<typeof playerSchema>;
export type Team = z.infer<typeof teamSchema>;
export type WireTrade = z.infer<typeof wireTradeSchema>;

export class ApiError extends Error {
  readonly status: number;
  // Seconds to wait, from the Retry-After header of a 429.
  readonly retryAfter?: number;
  // The message from the body of the response. It is unset when the body has none, so the status text in message does not pass as a reason.
  readonly detail?: string;

  constructor(status: number, message: string, retryAfter?: number, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.retryAfter = retryAfter;
    this.detail = detail;
  }
}

/* A body is { detail: string } or { detail: { message } }. The 410 of a closed trade route is { closed: true, line }, and
   its line is the detail. Any other body gives no detail. */
async function errorDetail(response: Response): Promise<string | undefined> {
  try {
    const body = await response.json();
    const detail = body?.detail;
    if (typeof detail === "string") return detail;
    if (typeof detail?.message === "string") return detail.message;
    if (body?.closed === true && typeof body.line === "string") return body.line;
  } catch {
    // The body is not JSON, so it has no detail.
  }
  return undefined;
}

/* A body that fails its schema is a 502 with the path of each bad field.
   The fault is upstream, so toErrorLine gives it a line of its own.
   The client throws it here, so a component never gets a wrong shape. */
function parseBody<S extends ZodType>(schema: S, body: unknown, route: string): z.output<S> {
  const result = schema.safeParse(body);
  if (result.success) return result.data;
  const issues = result.error.issues.map(
    (issue) => `${issue.path.join(".") || "(root)"}: ${issue.message}`,
  );
  throw new ApiError(502, `The API sent a wrong body for ${route}. ${issues.join("; ")}`);
}

/* Builds the ApiError for a failed response. Every call of the client uses it. */
export async function toApiError(response: Response): Promise<ApiError> {
  const retryAfter = Number(response.headers.get("Retry-After"));
  const detail = await errorDetail(response);
  return new ApiError(
    response.status,
    // Without a detail, the message falls back to the status text.
    detail ?? (response.statusText || `Request failed with status ${response.status}`),
    Number.isFinite(retryAfter) && retryAfter > 0 ? retryAfter : undefined,
    detail,
  );
}

// A wait longer than this reads in hours, because 50000 seconds means nothing to a reader.
const HOUR_SECONDS = 3600;

/* The wait as plain words. Hours round up, so the reader never tries again too early. Over an hour rounds up to 2 or more. */
function waitText(seconds: number): string {
  if (seconds <= HOUR_SECONDS) return `Try again in ${seconds} seconds.`;
  return `Try again in ${Math.ceil(seconds / HOUR_SECONDS)} hours.`;
}

/* The text of a 429. The wait is optional, because the Retry-After header may be missing. */
export function retryText(seconds?: number): string {
  return `Too many requests. ${seconds ? waitText(seconds) : "Try again soon."}`;
}

/* What the reader sees for a failed call. Each error box shows Try Again under it. */
export type ErrorView = { message: string };

/* Maps a failed call to what the reader sees. The trade form and the finder share it, so the same failure reads the same on both.
   The caller words the timeout line, because it names the work that ran long. */
export function toErrorLine(error: unknown, timedOut: boolean, timeoutMessage: string): ErrorView {
  if (timedOut) return { message: timeoutMessage };
  if (error instanceof ApiError) {
    if (error.status === 422) return { message: error.message };
    // A wrong body is a fault of the API, so the line does not show the paths of the bad fields.
    if (error.status === 502) return { message: "The API sent an answer the site cannot read." };
    if (error.status === 429) return { message: retryText(error.retryAfter) };
    // The API words the closed line, so a page from before the Lock shows it in place of a grade.
    if (error.status === 410 && error.detail) return { message: error.detail };
    // The API says why it is down in its detail, so the reader sees that reason when it exists.
    if (error.status === 503) {
      return {
        message: error.detail ?? "The analyzer is down for the moment. Try again in a few minutes.",
      };
    }
  }
  return { message: "The API did not answer. Try again." };
}

export async function fetchTeams(target: ApiTarget, passphrase: string): Promise<Team[]> {
  const response = await fetch(`${clientBase(target)}/teams?season=${target.season}`, {
    headers: { "X-League-Passphrase": passphrase },
  });
  if (!response.ok) throw await toApiError(response);
  return parseBody(teamsResponseSchema, await response.json(), "/teams").teams;
}

/* The accepted trades of the current leg, newest first, from the Trade Wire route. */
export async function fetchTradeWire(target: ApiTarget, passphrase: string): Promise<WireTrade[]> {
  const response = await fetch(`${clientBase(target)}/deadline/trades`, {
    headers: { "X-League-Passphrase": passphrase },
  });
  if (!response.ok) throw await toApiError(response);
  return parseBody(tradeWireResponseSchema, await response.json(), "/deadline/trades").trades;
}

/* A given player and the roster id of the side he goes to. See ADR 0008. */
export type AnalyzeGive = { player_id: string; to: number };

/* One side of the trade: a roster and the players it gives. */
export type AnalyzeSide = { roster_id: number; gives: AnalyzeGive[] };

export type AnalyzeRequest = {
  season: number;
  // The roster id of the team that asks for the grade.
  asker: number;
  // The asker's side comes first.
  sides: AnalyzeSide[];
};

/* Posts a JSON body with the passphrase and reads the JSON answer. It checks the answer against the schema. The caller owns the AbortSignal and sets the timeout. */
async function postJson<S extends ZodType>(
  target: ApiTarget,
  path: string,
  schema: S,
  passphrase: string,
  body: unknown,
  signal: AbortSignal,
): Promise<z.output<S>> {
  const response = await fetch(`${clientBase(target)}${path}`, {
    method: "POST",
    headers: { "X-League-Passphrase": passphrase, "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!response.ok) throw await toApiError(response);
  return parseBody(schema, await response.json(), path);
}

/* The caller owns the AbortSignal, because a cold week can take 20 seconds and the caller sets the timeout. */
export function postAnalyze(
  target: ApiTarget,
  passphrase: string,
  body: AnalyzeRequest,
  signal: AbortSignal,
): Promise<AnalyzeResponse> {
  return postJson(target, "/analyze", analyzeResponseSchema, passphrase, body, signal);
}

/* The body of the find route: the season, the roster that asks, and the partner roster. With no partner, the search
   runs over every other team. With a limit, each offer brings back a player at aim_position, the same field of the
   Limit that a typed question of trade ideas sets. With a Trade block of 1 to 3 player ids of the asker, each offer
   sends at least one of them. */
export type FindRequest = {
  season: number;
  asker: number;
  partner?: number;
  limit?: { aim_position: string };
  trade_block?: string[];
};

/* What the find stream gives the finder before its document: each step line, live while its step works, the roster id
   of each team as the search reads it, and each trade of the pick as soon as it stands, with its place in the pick
   order and the most trades that the pick can keep, and the trades of the Shortlist by their players before the pick
   starts (decision 20). `onTradesCount` gives the count of trades that the pick keeps, before the first trade and
   again each time a drop changes it, so the count line shows the real count from the first card. `onTradesDone` says
   that the pick has no more trades, so the count line can go before the document comes. The document stays the truth. */
export type FindEvents = {
  onStep: (line: string, live: boolean) => void;
  onTeam: (rosterId: number) => void;
  onTrade?: (index: number, most: number, trade: FinderTrade) => void;
  onShortlist?: (trades: ShortlistTrade[]) => void;
  onTradesCount?: (count: number) => void;
  onTradesDone?: () => void;
};

/* One player of a Shortlist trade: his full name, and his short name for a narrow line, such as "Walker". */
const shortlistPlayerSchema = z.object({ name: z.string(), last: z.string() });
/* One trade of the Shortlist that the pick weighs, from the side of the asker: the players he gives, then the players
   he gets. The stream sends the Shortlist before the pick, so the wait of step 5 can name each trade (decision 20). */
const shortlistTradeSchema = z.object({
  offer_id: z.string(),
  gives: z.array(shortlistPlayerSchema),
  gets: z.array(shortlistPlayerSchema),
});
export type ShortlistTrade = z.infer<typeof shortlistTradeSchema>;

/* One part of the find stream that the site reads. The stream sends more parts, such as the start, and the reader skips them. */
const findPartSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("data-step"),
    data: z.object({ line: z.string(), live: z.boolean().optional() }),
  }),
  z.object({ type: z.literal("data-team"), data: z.object({ roster_id: z.number() }) }),
  z.object({
    type: z.literal("data-trade"),
    data: z.object({ index: z.number(), most: z.number(), trade: finderTradeSchema }),
  }),
  z.object({
    type: z.literal("data-shortlist"),
    data: z.object({ trades: z.array(shortlistTradeSchema) }),
  }),
  z.object({ type: z.literal("data-trades-count"), data: z.object({ count: z.number() }) }),
  z.object({ type: z.literal("data-trades-done"), data: z.object({}) }),
  z.object({
    type: z.literal("data-answer"),
    data: z.object({ kind: z.literal("find"), document: findResponseSchema }),
  }),
  z.object({
    type: z.literal("data-error"),
    data: z.object({ status: z.number(), line: z.string() }),
  }),
]);

/* The find press as a stream: each step and each team read go to `events` as they come, and the document ends it.
   The finder grades every small swap of the pair, so a cold call can be slow. The caller owns the AbortSignal, as with postAnalyze.
   The stream reads the body of the find route. An error part throws an ApiError with its status and its line, so the
   finder shows the same error line as for a failed response. A stream with no document is a 502.
   The document returns at once, and the rest of the body drains to its end with no part read. The API closes the
   stream right after the document, so the drain ends at once, and a later abort of the page cuts no open stream that
   the API logs as a failure. */
export async function streamFind(
  target: ApiTarget,
  passphrase: string,
  body: FindRequest,
  events: FindEvents,
  signal: AbortSignal,
): Promise<FindResponse> {
  const response = await fetch(`${clientBase(target)}/find-stream`, {
    method: "POST",
    headers: { "X-League-Passphrase": passphrase, "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!response.ok) throw await toApiError(response);
  if (!response.body) throw new ApiError(502, "The find stream sent no body.");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    buffer += value ? decoder.decode(value, { stream: !done }) : "";
    const blocks = buffer.split("\n\n");
    buffer = done ? "" : (blocks.pop() ?? "");
    for (const block of blocks) {
      const line = block.trim();
      if (!line.startsWith("data: ") || line === "data: [DONE]") continue;
      const part = findPartSchema.safeParse(JSON.parse(line.slice("data: ".length)));
      if (!part.success) continue;
      const { type, data } = part.data;
      if (type === "data-step") events.onStep(data.line, data.live ?? false);
      if (type === "data-team") events.onTeam(data.roster_id);
      if (type === "data-trade") events.onTrade?.(data.index, data.most, data.trade);
      if (type === "data-shortlist") events.onShortlist?.(data.trades);
      if (type === "data-trades-count") events.onTradesCount?.(data.count);
      if (type === "data-trades-done") events.onTradesDone?.();
      if (type === "data-error") throw new ApiError(data.status, data.line, undefined, data.line);
      if (type === "data-answer") {
        void drain(reader);
        return data.document;
      }
    }
    if (done) throw new ApiError(502, "The find stream ended with no document.");
  }
}

/* Read the rest of a stream to its end and drop it. An abort or a network error during the drain only ends it,
   because the caller has its document already. */
async function drain(reader: ReadableStreamDefaultReader<Uint8Array>): Promise<void> {
  try {
    while (!(await reader.read()).done);
  } catch {
    // The caller has its document, so a failed drain changes nothing.
  }
}
