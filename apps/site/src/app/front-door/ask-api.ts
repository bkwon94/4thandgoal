/**
 * The client of the ask route of the API, at /clients/<slug>/ask, with the Zod schema of its answer. The call sends the
 * league passphrase. A failed call throws an AskError with its status, so the Thread can show the right line.
 */
import { z } from "zod";

/* The API that a call goes to: its base URL and the slug of the client. The app builds it from its config. */
export type AskTarget = { url: string; client: string };

/* The route of one question: a Topic, a free answer, an honest miss, or a calm refusal. `team` is the roster id of the
   team that the question names, or null for Your team. `closest` holds the 3 closest Topics of a miss. */
export const askAnswerSchema = z.object({
  route: z.enum(["topic", "free", "miss", "refuse"]),
  topic: z.string().nullable(),
  team: z.number().nullable(),
  closest: z.array(z.string()),
  suggestion: z.string().nullable(),
});
export type AskAnswer = z.infer<typeof askAnswerSchema>;

/* The body of the ask route: the question as typed, the roster id of Your team, and the latest week of the site. */
export type AskQuestion = { question: string; roster_id: number; week: number };

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

export async function askRoute(target: AskTarget, passphrase: string, body: AskQuestion): Promise<AskAnswer> {
  let response: Response;
  try {
    response = await fetch(`${target.url}/clients/${encodeURIComponent(target.client)}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-League-Passphrase": passphrase },
      body: JSON.stringify(body),
    });
  } catch {
    throw new AskError(0, "The question did not reach the site.");
  }
  if (!response.ok) {
    const seconds = Number(response.headers.get("Retry-After"));
    throw new AskError(response.status, response.statusText, Number.isFinite(seconds) && seconds > 0 ? seconds : undefined);
  }
  const parsed = askAnswerSchema.safeParse(await response.json());
  if (!parsed.success) throw new AskError(502, "The API sent an answer the site cannot read.");
  return parsed.data;
}
