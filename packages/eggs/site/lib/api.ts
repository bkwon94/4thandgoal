/**
 * The client of the eggs routes of the API, at /clients/<slug>/eggs/, with the Zod schema of each answer.
 * The egg check and the egg board need no key. The claim sends the league passphrase. A failed call throws an EggsError.
 */
import { z } from "zod";

/* The API that a call goes to: its base URL and the slug of the client. The app builds it from its config. */
export type EggsTarget = { url: string; client: string };

/* The state of the conditions of one check, such as the theme. The API matches each condition of an egg. */
export type Conditions = Record<string, string | boolean | number | string[]>;

/* The body of the egg check: the page, the stable id of the element, the action, the stable ids of the two taps before
   the double-tap of a tap combo, the selected word of the action "select", and the state of the conditions. */
export type EggCheck = {
  page: string;
  target: string;
  action: string;
  trail?: string[];
  word?: string;
  conditions: Conditions;
};

export const checkAnswerSchema = z.union([
  z.object({ match: z.literal(false) }),
  z.object({ match: z.literal(true), claimed: z.literal(false), letter: z.string(), token: z.string() }),
  z.object({ match: z.literal(true), claimed: z.literal(true), letter: z.string() }),
]);
export type CheckAnswer = z.infer<typeof checkAnswerSchema>;

const managerSchema = z.object({ roster_id: z.number(), team: z.string() });

export const boardSchema = z.object({
  counts: z.object({ left: z.number(), found: z.number(), to_drop: z.number() }),
  weeks: z.array(z.object({ week: z.number(), slots: z.array(z.enum(["found", "out", "future"])) })),
  words: z.array(
    z.object({
      word: z.string(),
      prize: z.number(),
      // The manager whose letters fill the egg word, or null while the word is open.
      winner: managerSchema.nullable(),
      managers: z.array(managerSchema.extend({ letters: z.array(z.string()) })),
    }),
  ),
  latest: z.array(
    managerSchema.extend({ letter: z.string(), word: z.string(), claimed_at: z.string() }),
  ),
  managers: z.array(managerSchema),
  // The week, the count, and the time of the newest drop, or null before the first drop. The egg banner reads it.
  // The time carries the offset of the timezone of the client, because the API clock runs in that timezone.
  last_drop: z.object({ week: z.number(), count: z.number(), dropped_at: z.string() }).nullable(),
});
export type Board = z.infer<typeof boardSchema>;
export type Manager = z.infer<typeof managerSchema>;

export const claimAnswerSchema = z.object({
  egg_id: z.number(),
  letter: z.string(),
  roster_id: z.number(),
  word: z.string().nullable(),
  letters: z.record(z.string(), z.array(z.string())),
  // The egg word that the claim fills, or null when the word is still open or the claim is a block.
  winner: z.object({ roster_id: z.number(), word: z.string() }).nullable(),
});
export type ClaimAnswer = z.infer<typeof claimAnswerSchema>;

/* The body of the claim: the token of the check, the roster, and the egg word, or null for a block. */
export type EggClaim = { token: string; roster_id: number; word: string | null };

/* A failed call: its status, the detail of the API when the body has one, and the wait of a 429. */
export class EggsError extends Error {
  readonly status: number;
  // Seconds to wait, from the Retry-After header of a 429.
  readonly retryAfter?: number;

  constructor(status: number, message: string, retryAfter?: number) {
    super(message);
    this.name = "EggsError";
    this.status = status;
    this.retryAfter = retryAfter;
  }
}

/* The seconds of a Retry-After header, or undefined when the header is missing or is not a count of seconds. */
function retryAfterOf(response: Response): number | undefined {
  const seconds = Number(response.headers.get("Retry-After"));
  return Number.isFinite(seconds) && seconds > 0 ? seconds : undefined;
}

function eggsBase(target: EggsTarget): string {
  return `${target.url}/clients/${encodeURIComponent(target.client)}/eggs`;
}

async function answer<S extends z.ZodType>(response: Response, schema: S): Promise<z.output<S>> {
  if (!response.ok) {
    let detail = response.statusText || `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // The body is not JSON, so the status text stands.
    }
    throw new EggsError(response.status, detail, retryAfterOf(response));
  }
  const parsed = schema.safeParse(await response.json());
  if (!parsed.success) throw new EggsError(502, "The API sent an answer the site cannot read.");
  return parsed.data;
}

export async function checkEgg(target: EggsTarget, check: EggCheck): Promise<CheckAnswer> {
  const response = await fetch(`${eggsBase(target)}/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(check),
  });
  return answer(response, checkAnswerSchema);
}

export async function claimEgg(target: EggsTarget, passphrase: string, claim: EggClaim): Promise<ClaimAnswer> {
  const response = await fetch(`${eggsBase(target)}/claim`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-League-Passphrase": passphrase },
    body: JSON.stringify(claim),
  });
  return answer(response, claimAnswerSchema);
}

export async function fetchBoard(target: EggsTarget): Promise<Board> {
  return answer(await fetch(`${eggsBase(target)}/board`), boardSchema);
}

/* The port of the eggs routes that the parts call. The app gives eggsApi of its target, and a test gives the one fake
   of lib/fixtures/eggs-api.ts. */
export type EggsApi = {
  check: (check: EggCheck) => Promise<CheckAnswer>;
  claim: (passphrase: string, claim: EggClaim) => Promise<ClaimAnswer>;
  board: () => Promise<Board>;
};

export function eggsApi(target: EggsTarget): EggsApi {
  return {
    check: (check) => checkEgg(target, check),
    claim: (passphrase, claim) => claimEgg(target, passphrase, claim),
    board: () => fetchBoard(target),
  };
}
