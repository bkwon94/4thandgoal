/**
 * The client of the ask route of the API, at /clients/<slug>/ask, with the Zod schema of its answer. The call sends the
 * league passphrase. A failed call throws an AskError with its status, so the Thread can show the right line.
 */
import { z } from "zod";
import type { Turn } from "./chat-turns";

/* The API that a call goes to: its base URL and the slug of the client. The app builds it from its config. */
export type AskTarget = { url: string; client: string };

/* The route of one question: a Topic, a free answer, an honest miss, a calm refusal, the calm line of a cap in place
   of a free answer, or a Site answer. `team` is the roster id of the team that the question names, or null for Your
   team. `closest` holds the 3 closest Topics of a miss and of a cap. `line` is the line of a cap, else null. `page` is
   the page of a Site answer: a page key, `all`, or `missing`, else null. */
export const askAnswerSchema = z.object({
  route: z.enum(["topic", "free", "miss", "refuse", "cap", "site"]),
  line: z.string().nullable().default(null),
  topic: z.string().nullable(),
  team: z.number().nullable(),
  closest: z.array(z.string()),
  suggestion: z.string().nullable(),
  page: z.string().nullable().default(null),
});
export type AskAnswer = z.infer<typeof askAnswerSchema>;

/* One page of the client in the ask route: its package name, its label, and its blurb, so the route can answer a
   question about the site. */
export type AskPage = { key: string; label: string; blurb: string };

/* The body of the ask route: the question as typed, the roster id of Your team, the latest week of the site, the
   earlier turns of the Thread, oldest first, and the pages of the client. */
export type AskQuestion = { question: string; roster_id: number; week: number; turns?: Turn[]; pages?: AskPage[] };

/* A failed call: its status, and the wait of a 429 in seconds. A status of 0 is a call that never reached the API. */
export class AskError extends Error {
  readonly status: number;
  readonly retryAfter?: number;

  constructor(status: number, message: string, retryAfter?: number) {
    super(message);
    this.name = "AskError";
    this.status = status;
    this.retryAfter = retryAfter;
  }
}

/* Send one POST to `path` under /clients/<slug>/ of the API, with the league passphrase. A call that never reaches the
   API throws an AskError of status 0. A failed status throws its AskError, with the wait of the Retry-After header. */
export async function postClient(target: AskTarget, passphrase: string, path: string, body: unknown): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`${target.url}/clients/${encodeURIComponent(target.client)}/${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-League-Passphrase": passphrase },
      body: JSON.stringify(body),
    });
  } catch {
    throw new AskError(0, "The question did not reach the site.");
  }
  if (!response.ok) throw statusError(response);
  return response;
}

/* The AskError of a failed status. A 429 carries its wait in seconds when the Retry-After header gives one. */
export function statusError(response: Response): AskError {
  const seconds = Number(response.headers.get("Retry-After"));
  return new AskError(response.status, response.statusText, Number.isFinite(seconds) && seconds > 0 ? seconds : undefined);
}

/* The JSON body of a response, read with its schema. A body that the schema rejects throws an AskError of status 502. */
export async function readBody<T>(response: Response, schema: z.ZodType<T>): Promise<T> {
  const parsed = schema.safeParse(await response.json());
  if (!parsed.success) throw new AskError(502, "The API sent an answer the site cannot read.");
  return parsed.data;
}

export async function askRoute(target: AskTarget, passphrase: string, body: AskQuestion): Promise<AskAnswer> {
  return readBody(await postClient(target, passphrase, "ask", body), askAnswerSchema);
}
