/**
 * The client of the ask route of the API, at /clients/<slug>/ask, with the Zod schema of its answer. The call sends the
 * league passphrase. A failed call throws an AskError with its status, so the Thread can show the right line.
 */
import { z } from "zod";
import type { SitePage } from "@/app/site-pages";
import type { PackageName } from "@/lib/client-values";
import type { Turn } from "./chat-turns";

/* The API that a call goes to: its base URL and the slug of the client. The app builds it from its config. */
export type AskTarget = { url: string; client: string };

/* The page of a Site answer that asks about the whole site, so the Thread shows the list view. */
export const ALL_PAGES = "all";
/* The page of a Site answer that asks about a page the client lacks, so the Thread shows the none case. */
export const MISSING_PAGE = "missing";
/* The page of a Site answer: a page key, ALL_PAGES, or MISSING_PAGE. */
export type SiteAnswerPage = PackageName | typeof ALL_PAGES | typeof MISSING_PAGE;

/* Each package name, so a page key from the API reads as a PackageName. The Record type fails the typecheck when a
   package name is missing here. */
const PAGE_KEYS: Record<PackageName, true> = {
  week: true,
  rankings: true,
  managers: true,
  waiver: true,
  analyzer: true,
  sim: true,
  midseason: true,
  eggs: true,
};

const isPageKey = (value: string): value is PackageName => Object.hasOwn(PAGE_KEYS, value);

/* The page of the API as a SiteAnswerPage. A value that is no page key reads as MISSING_PAGE, so the Thread shows the
   none case and not an error. */
function sitePageOf(value: string): SiteAnswerPage {
  if (value === ALL_PAGES || value === MISSING_PAGE) return value;
  return isPageKey(value) ? value : MISSING_PAGE;
}

/* The route of one question: a Topic, a free answer, an honest miss, a calm refusal, the calm line of a cap in place
   of a free answer, a Site answer, or the closed line of a trade question after the Lock. `team` is the roster id of the team that the question names, or null for Your
   team. `closest` holds the 3 closest Topics of a miss and of a cap. `line` is the line of a cap or the closed line, else null. `page` is
   the page of a Site answer, else null. */
export const askAnswerSchema = z.object({
  route: z.enum(["topic", "free", "miss", "refuse", "cap", "site", "closed"]),
  line: z.string().nullable().default(null),
  topic: z.string().nullable(),
  team: z.number().nullable(),
  closest: z.array(z.string()),
  suggestion: z.string().nullable(),
  page: z
    .string()
    .nullable()
    .default(null)
    .transform((value) => (value === null ? null : sitePageOf(value))),
});
export type AskAnswer = z.infer<typeof askAnswerSchema>;

/* One page of the client in the ask route: its package name, its label, and its blurb, so the route can answer a
   question about the site. */
export type AskPage = Pick<SitePage, "key" | "label" | "blurb">;

/* The pages of the ask route: each page of the Site answer with only its key, its label, and its blurb. The link and
   the Tool mark stay in the site. */
export const askPagesOf = (pages: SitePage[]): AskPage[] =>
  pages.map(({ key, label, blurb }) => ({ key, label, blurb }));

/* The body of the ask route: the question as typed, the roster id of Your team, the latest week of the site, the
   earlier turns of the Thread, oldest first, and the pages of the client. */
export type AskQuestion = {
  question: string;
  roster_id: number;
  week: number;
  turns?: Turn[];
  pages?: AskPage[];
};

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
export async function postClient(
  target: AskTarget,
  passphrase: string,
  path: string,
  body: unknown,
): Promise<Response> {
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
  return new AskError(
    response.status,
    response.statusText,
    Number.isFinite(seconds) && seconds > 0 ? seconds : undefined,
  );
}

/* The JSON body of a response, read with its schema. A body that the schema rejects throws an AskError of status 502. */
export async function readBody<T>(response: Response, schema: z.ZodType<T>): Promise<T> {
  const parsed = schema.safeParse(await response.json());
  if (!parsed.success) throw new AskError(502, "The API sent an answer the site cannot read.");
  return parsed.data;
}

export async function askRoute(
  target: AskTarget,
  passphrase: string,
  body: AskQuestion,
): Promise<AskAnswer> {
  return readBody(await postClient(target, passphrase, "ask", body), askAnswerSchema);
}
