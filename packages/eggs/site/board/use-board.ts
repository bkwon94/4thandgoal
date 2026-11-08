/**
 * The board of the API for the egg button, the egg banner, and the hunt: null until it loads, when the call fails,
 * and before the first egg drop. The first drop turns the hunt on, so until then nothing of the hunt shows.
 */
"use client";

import { useEffect, useState } from "react";
import type { Board, EggsApi } from "../lib/api";

/* True once an egg has dropped. The board names no last drop before the first drop. */
export function huntIsOn(board: Board | null): board is Board {
  return board !== null && board.last_drop !== null;
}

/* The board once the hunt is on, else null. A failed call reads as off, so the page shows no part of the hunt. */
export function useHuntBoard(api: EggsApi): Board | null {
  const board = useBoard(api);
  return huntIsOn(board) ? board : null;
}

export function useBoard(api: EggsApi): Board | null {
  const [board, setBoard] = useState<Board | null>(null);
  useEffect(() => {
    let live = true;
    api.board().then(
      (answer) => {
        if (live) setBoard(answer);
      },
      () => {
        // The part stays hidden. The page works with no egg button badge and no banner.
      },
    );
    return () => {
      live = false;
    };
  }, [api]);
  return board;
}
