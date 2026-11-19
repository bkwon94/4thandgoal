/**
 * The client of the What-if route of the API, POST /clients/<slug>/sim/what-if, and the port that the sim page calls.
 * A failed call throws a WhatIfError. A cancelled call throws the AbortError of fetch, which the page ignores.
 */
import { whatIfAnswerSchema } from "../schema/what-if";
import type { SetResult, WhatIfAnswer } from "../schema/sim-types";

/* The API that a call goes to: its base URL and the slug of the client. The app builds it from its config. */
export type WhatIfTarget = { url: string; client: string };

/* One What-if: Your team and its set results, at most one for each week left. */
export type WhatIfAsk = { you: number; set: SetResult[] };

/* The port of the route. The signal cancels the call, so the server stops the work of a tap that a new tap replaced. */
export type WhatIfApi = (ask: WhatIfAsk, signal: AbortSignal) => Promise<WhatIfAnswer>;

/* A failed call: its status, or 0 when no answer came, such as when the API is down. */
export class WhatIfError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "WhatIfError";
    this.status = status;
  }
}

async function detailOf(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") return body.detail;
  } catch {
    // The body is not JSON, so the status text stands.
  }
  return response.statusText || `Request failed with status ${response.status}`;
}

export function whatIfApi(target: WhatIfTarget): WhatIfApi {
  const url = `${target.url}/clients/${encodeURIComponent(target.client)}/sim/what-if`;
  return async (ask, signal) => {
    let response: Response;
    try {
      response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ask),
        signal,
      });
    } catch (error) {
      if (signal.aborted) throw error;
      throw new WhatIfError(0, "The API sent no answer.");
    }
    if (!response.ok) throw new WhatIfError(response.status, await detailOf(response));
    const parsed = whatIfAnswerSchema.safeParse(await response.json());
    if (!parsed.success) throw new WhatIfError(502, "The API sent an answer the site cannot read.");
    return parsed.data;
  };
}
