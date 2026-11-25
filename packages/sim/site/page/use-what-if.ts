/**
 * The state of the What-if of the sim page: the set results, the page block and the board that the page shows, and the call
 * to the API. Each tap starts a call at once and cancels the call before it. With no set result, the page shows the file.
 */
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { BoardTeam, SetResult, SimPage, WeekCard, WhatIfAnswer } from "../schema/sim-types";
import type { WhatIfApi } from "../lib/what-if-api";

/* The stored runs of an answer, which each hold its set results, and their weights. The replay picks from them. */
export type AnswerRuns = Pick<WhatIfAnswer, "teams" | "sample" | "sample_weights">;

/* The result of a tile, or null to clear the week. */
export type Choice = Pick<SetResult, "game" | "median"> | null;

type State = {
  // The set results that the page assumes, in week order.
  set: SetResult[];
  // The page block and the board of the last answer, and the set results it holds. Null with no answer, so the page
  // shows the file.
  answer: { page: SimPage; board: BoardTeam[]; set: SetResult[]; runs: AnswerRuns } | null;
  // The week card as the page showed it before its week was set, so its tiles keep the odds of each other result.
  // Null while the week of the card is not set.
  card: WeekCard | null;
  pending: boolean;
  // True after a call failed, until the next answer or a Reset.
  down: boolean;
};

/* The week card of an answer over the card held at the tap. An answer with the week set has runs of the set result
   only, so each other result keeps the odds and the root-for list of the held card. */
export function heldCard(held: WeekCard | null, shown: WeekCard | null): WeekCard | null {
  if (held === null || shown === null || shown.week !== held.week) return shown ?? held;
  const goals = Object.fromEntries(
    Object.entries(held.goals).map(([key, goal]) => {
      const now = shown.goals[key];
      const pick = <T>(mine: T[][], theirs: T[][] | undefined) =>
        mine.map((rows, i) => (theirs?.[i]?.length ? theirs[i] : rows));
      return [
        key,
        {
          ...goal,
          odds: goal.odds.map((odds, i) => now?.odds[i] ?? odds),
          root_for: pick(goal.root_for, now?.root_for),
          median_root: pick(goal.median_root, now?.median_root),
        },
      ];
    }),
  );
  return { ...held, goals };
}

const EMPTY: State = { set: [], answer: null, card: null, pending: false, down: false };

export type WhatIf = {
  set: SetResult[];
  // The page block that the page shows: the answer of the set results, or the file.
  page: SimPage;
  // The board odds of the answer that `page` shows, or null when the page shows the file.
  board: BoardTeam[] | null;
  // The week card that the page shows: the card of `page`, over the card held at the tap of its week.
  card: WeekCard | null;
  // The stored runs of the answer that `page` shows, or null when the page shows the file.
  runs: AnswerRuns | null;
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
  const cardWeek = file.week_card?.week;

  /* The held card after `set`: the card before its week was set, or null when `set` leaves the week open. */
  const holdFor = (set: SetResult[], was: State) =>
    set.some((result) => result.week === cardWeek) ? (was.card ?? shown.week_card) : null;

  /* Start the call of `set`. */
  const start = (set: SetResult[]) => {
    setState((was) => ({ ...was, set, card: holdFor(set, was), pending: true }));
    const controller = new AbortController();
    call.current = controller;
    const failed = () =>
      // The page goes back to the set results of the last answer, so each number on it agrees with its set line.
      setState((was) => {
        const kept = was.answer?.set ?? [];
        const card = kept.some((result) => result.week === cardWeek) ? was.card : null;
        return { ...was, set: kept, card, pending: false, down: true };
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
            board: answer.board,
            set,
            runs: {
              teams: answer.teams,
              sample: answer.sample,
              sample_weights: answer.sample_weights,
            },
          },
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
      if (set.length === 0) {
        setState({ ...EMPTY, down: state.down });
        return;
      }
      start(set);
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
      start(sorted);
    },
    // oxlint-disable-next-line react-hooks/exhaustive-deps -- start reads only refs, props, and setState
    [api, file.you, shown, state],
  );

  const reset = useCallback(() => {
    cancel();
    setState(EMPTY);
  }, []);

  return {
    set: state.set,
    page: shown,
    board: answered !== null && answered.board.length > 0 ? answered.board : null,
    card: heldCard(state.card, shown.week_card),
    runs: answered?.runs ?? null,
    pending: state.pending,
    down: state.down,
    choose,
    chooseAll,
    reset,
  };
}
