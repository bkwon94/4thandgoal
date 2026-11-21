/**
 * The one fake of the What-if port for the site tests, over two answers that the local API gave on week-sim.json.
 * The fake keeps each call and its signal, so a test reads what the page sent and which call it cancelled.
 */
import winAboveJson from "./what-if-win-above.json";
import lossBelowJson from "./what-if-loss-below.json";
import { whatIfAnswerSchema } from "../schema/what-if";
import type { WhatIfAnswer } from "../schema/sim-types";
import { WhatIfError, type WhatIfApi, type WhatIfAsk } from "../lib/what-if-api";

/* The parse runs at import, so a stale fixture fails at once. Bo Girds, roster 6, sets week 11 in each. */
export const winAbove = whatIfAnswerSchema.parse(winAboveJson);
export const lossBelow = whatIfAnswerSchema.parse(lossBelowJson);

const ANSWERS: WhatIfAnswer[] = [winAbove, lossBelow];

const keyOf = (ask: WhatIfAsk) => JSON.stringify({ you: ask.you, set: ask.set });

export type FakeWhatIfApi = WhatIfApi & { calls: { ask: WhatIfAsk; signal: AbortSignal }[] };

/* The fake answers a call with the recorded answer of its set results, one tick later, as a fetch does. A cancelled
   call throws the AbortError of fetch. A set with no recorded answer is a 422 of the fake. */
export function fakeWhatIfApi(): FakeWhatIfApi {
  const calls: FakeWhatIfApi["calls"] = [];
  const api: WhatIfApi = async (ask, signal) => {
    calls.push({ ask, signal });
    await Promise.resolve();
    if (signal.aborted) throw new DOMException("The call was cancelled.", "AbortError");
    const answer = ANSWERS.find((entry) => keyOf(entry) === keyOf(ask));
    if (answer === undefined)
      throw new WhatIfError(422, `The fake has no answer for ${keyOf(ask)}.`);
    return answer;
  };
  return Object.assign(api, { calls });
}
