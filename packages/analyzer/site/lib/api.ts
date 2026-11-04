/**
 * The client for the site API. Each call sends the league passphrase in the X-League-Passphrase header.
 * Each call goes to the routes of one client, /clients/<slug>/. A failed call throws an ApiError, and the caller decides.
 */
import type { z, ZodType } from "zod";
import type { AnalyzeResponse, FindResponse } from "./analyze-types";
import { analyzeResponseSchema, findResponseSchema, playerSchema, teamSchema, teamsResponseSchema } from "./schemas/api";

/* The API that a call goes to: its base URL, the slug of the client, and the season the routes read.
   The page builds it from the config of the app, so the package reads no env. */
export type ApiTarget = { url: string; client: string; season: number };

/* The base of the routes of the client of the target. */
function clientBase(target: ApiTarget): string {
  return `${target.url}/clients/${encodeURIComponent(target.client)}`;
}

export type TeamPlayer = z.infer<typeof playerSchema>;
export type Team = z.infer<typeof teamSchema>;

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

/* A body is { detail: string } or { detail: { message } }. Any other body gives no detail. */
async function errorDetail(response: Response): Promise<string | undefined> {
  try {
    const body = await response.json();
    const detail = body?.detail;
    if (typeof detail === "string") return detail;
    if (typeof detail?.message === "string") return detail.message;
  } catch {
    // The body is not JSON, so it has no detail.
  }
  return undefined;
}

/* A body that fails its schema is a 502 with the path of each bad field.
   The fault is upstream, and a retry cannot fix a wrong shape, so toErrorLine offers no retry for it.
   The client throws it here, so a component never gets a wrong shape. */
function parseBody<S extends ZodType>(schema: S, body: unknown, route: string): z.output<S> {
  const result = schema.safeParse(body);
  if (result.success) return result.data;
  const issues = result.error.issues.map((issue) => `${issue.path.join(".") || "(root)"}: ${issue.message}`);
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

/* What the reader sees for a failed call, and whether a retry button shows. */
export type ErrorView = { message: string; retry: boolean };

/* Maps a failed call to what the reader sees. The trade form and the finder share it, so the same failure reads the same on both.
   A timeout and an unknown failure offer a retry. The caller words the timeout line, because it names the work that ran long. */
export function toErrorLine(error: unknown, timedOut: boolean, timeoutMessage: string): ErrorView {
  if (timedOut) return { message: timeoutMessage, retry: true };
  if (error instanceof ApiError) {
    if (error.status === 422) return { message: error.message, retry: false };
    // A wrong body is a fault of the API, so a retry cannot fix it.
    if (error.status === 502) return { message: "The API sent an answer the site cannot read.", retry: false };
    if (error.status === 429) return { message: retryText(error.retryAfter), retry: false };
    // The API says why it is down in its detail, so the reader sees that reason when it exists.
    if (error.status === 503) {
      return { message: error.detail ?? "The analyzer is down for the moment. Try again in a few minutes.", retry: true };
    }
  }
  return { message: "The API did not answer. Try again.", retry: true };
}

export async function fetchTeams(target: ApiTarget, passphrase: string): Promise<Team[]> {
  const response = await fetch(`${clientBase(target)}/teams?season=${target.season}`, {
    headers: { "X-League-Passphrase": passphrase },
  });
  if (!response.ok) throw await toApiError(response);
  return parseBody(teamsResponseSchema, await response.json(), "/teams").teams;
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

/* The body of the find route: the season, the roster that asks, and the partner roster. */
export type FindRequest = { season: number; asker: number; partner: number };

/* The finder grades every small swap of the pair, so a cold call can be slow. The caller owns the AbortSignal, as with postAnalyze. */
export function postFind(target: ApiTarget, passphrase: string, body: FindRequest, signal: AbortSignal): Promise<FindResponse> {
  return postJson(target, "/find", findResponseSchema, passphrase, body, signal);
}
