/**
 * The state of the What-if of the sim page: the set results, the page block that the page shows, and the call to the API.
 * Each tap starts a call at once and cancels the call before it. With no set result, the page shows the file.
 */
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { SetResult, SimPage, WhatIfAnswer } from "../schema/sim-types";
import type { WhatIfApi } from "../lib/what-if-api";

type PageWeek = SimPage["weeks"][number];

/* The stored runs of an answer, which each hold its set results, and their weights. The replay picks from them. */
export type AnswerRuns = Pick<WhatIfAnswer, "teams" | "sample" | "sample_weights">;

/* The result of a tile, or null to clear the week. */
export type Choice = Pick<SetResult, "game" | "median"> | null;

type State = {
  // The set results that the page assumes, in week order.
  set: SetResult[];
  // The page block of the last answer, and the set results it holds. Null with no answer, so the page shows the file.
  answer: { page: SimPage; set: SetResult[]; runs: AnswerRuns } | null;
  // The block of each set week as the page showed it at the tap, so its tiles keep the odds of each other result.
  held: Record<number, PageWeek>;
  pending: boolean;
  // True after a call failed, until the next answer or a Reset.
  down: boolean;
};

/* The held block of `week` with the odds of the answer on its set result. The answer holds the result of the tap and
   each other set result, so the pressed tile shows the header odds of that answer, not the noisy odds of the split. */
function withOdds(
  held: State["held"],
  week: number,
  choice: NonNullable<Choice>,
  page: SimPage,
): State["held"] {
  const block = held[week];
  if (block === undefined) return held;
  const results = block.results.map((result) =>
    result.game === choice.game && result.median === choice.median
      ? { ...result, playoff: page.playoff, about: false }
      : result,
  );
  return { ...held, [week]: { ...block, results } };
}

const EMPTY: State = { set: [], answer: null, held: {}, pending: false, down: false };

export type WhatIf = {
  set: SetResult[];
  // The page block that the page shows: the answer of the set results, or the file.
  page: SimPage;
  // The stored runs of the answer that `page` shows, or null when the page shows the file.
  runs: AnswerRuns | null;
  // The block of a week as the page shows it: the held block of a set week, or the week of `page`.
  weekOf: (week: number) => PageWeek | undefined;
  pending: boolean;
  down: boolean;
  choose: (week: number, choice: Choice) => void;
  // Set each week of `set` at once in place of the set results, as "Try it" of a Week plan does.
  chooseAll: (set: SetResult[]) => void;
  reset: () => void;
};

/* `file` is the page block of sim.json. Without `api`, a tap fails at once, as with the API down. */
export function useWhatIf(file: SimPage, api: WhatIfApi | undefined): WhatIf {
  const [state, setState] = useState<State>(EMPTY);
  const call = useRef<AbortController | null>(null);

  const cancel = () => {
    call.current?.abort();
    call.current = null;
  };
  useEffect(() => cancel, []);

  const answered = state.set.length > 0 && state.answer !== null ? state.answer : null;
  const shown = answered?.page ?? file;

  /* Start the call of `set`. `heldOf` gives the held blocks after the answer, from the state then and its page. */
  const start = (
    set: SetResult[],
    held: State["held"],
    heldOf: (was: State, page: SimPage) => State["held"],
  ) => {
    setState((was) => ({ ...was, set, held, pending: true }));
    const controller = new AbortController();
    call.current = controller;
    const failed = () =>
      // The page goes back to the set results of the last answer, so each number on it agrees with its set line.
      setState((was) => {
        const kept = was.answer?.set ?? [];
        const keep = new Set(kept.map((result) => result.week));
        const left = Object.fromEntries(
          Object.entries(was.held).filter(([key]) => keep.has(Number(key))),
        );
        return { ...was, set: kept, held: left, pending: false, down: true };
      });
    if (api === undefined) {
      failed();
      return;
    }
    api({ you: file.you, set }, controller.signal).then(
      (answer) => {
        if (controller.signal.aborted) return;
        call.current = null;
        setState((was) => ({
          ...was,
          answer: {
            page: answer.page,
            set,
            runs: {
              teams: answer.teams,
              sample: answer.sample,
              sample_weights: answer.sample_weights,
            },
          },
          held: heldOf(was, answer.page),
          pending: false,
          down: false,
        }));
      },
      () => {
        // A cancelled call gives way to the call of the new tap, so only a call that still counts fails the page.
        if (controller.signal.aborted) return;
        call.current = null;
        failed();
      },
    );
  };

  const choose = useCallback(
    (week: number, choice: Choice) => {
      cancel();
      const rest = state.set.filter((result) => result.week !== week);
      const set =
        choice === null ? rest : [...rest, { week, ...choice }].sort((a, b) => a.week - b.week);
      const held = { ...state.held };
      delete held[week];
      if (choice !== null) {
        const block = state.held[week] ?? shown.weeks.find((entry) => entry.week === week);
        if (block !== undefined) held[week] = block;
      }
      if (set.length === 0) {
        setState({ ...EMPTY, down: state.down });
        return;
      }
      start(set, held, (was, page) =>
        choice === null ? was.held : withOdds(was.held, week, choice, page),
      );
    },
    // oxlint-disable-next-line react-hooks/exhaustive-deps -- start reads only refs, props, and setState
    [api, file.you, shown, state],
  );

  const chooseAll = useCallback(
    (set: SetResult[]) => {
      cancel();
      const sorted = [...set].sort((a, b) => a.week - b.week);
      if (sorted.length === 0) {
        setState({ ...EMPTY, down: state.down });
        return;
      }
      const held: State["held"] = {};
      for (const result of sorted) {
        const block =
          state.held[result.week] ?? shown.weeks.find((entry) => entry.week === result.week);
        if (block !== undefined) held[result.week] = block;
      }
      start(sorted, held, (was) => was.held);
    },
    // oxlint-disable-next-line react-hooks/exhaustive-deps -- start reads only refs, props, and setState
    [api, file.you, shown, state],
  );

  const reset = useCallback(() => {
    cancel();
    setState(EMPTY);
  }, []);

  const weekOf = (week: number) =>
    state.held[week] ?? shown.weeks.find((entry) => entry.week === week);

  return {
    set: state.set,
    page: shown,
    runs: answered?.runs ?? null,
    weekOf,
    pending: state.pending,
    down: state.down,
    choose,
    chooseAll,
    reset,
  };
}
