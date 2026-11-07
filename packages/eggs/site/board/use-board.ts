/**
 * The board of the API for the egg button and the egg banner: null until it loads, and null when the call fails.
 * The two parts are small extras of a page, so a failed call hides them and shows no error.
 */
"use client";

import { useEffect, useState } from "react";
import type { Board, EggsApi } from "../lib/api";

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
