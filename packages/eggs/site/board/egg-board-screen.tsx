/**
 * The egg board page part: it reads the board from the API at each visit, because the claims change at any time.
 * The page of the app mounts it under the top band. Before the first egg drop it shows the closed content of the app.
 */
"use client";

import { useEffect, useState, type ReactNode } from "react";
import type { Board, EggsApi } from "../lib/api";
import { EggBoard } from "./egg-board";
import { huntIsOn } from "./use-board";

type EggBoardScreenProps = {
  api: EggsApi;
  // The content before the first drop, and when the call fails. The app gives its 404 screen, so the page holds no egg copy.
  closed: ReactNode;
  // The title of the page once the hunt is on. The page loads with the title of the closed content.
  title: string;
};

export function EggBoardScreen({ api, closed, title }: EggBoardScreenProps) {
  const [board, setBoard] = useState<Board | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    api.board().then(setBoard, () => setFailed(true));
  }, [api]);

  const on = huntIsOn(board);
  useEffect(() => {
    if (on) document.title = title;
  }, [on, title]);

  // A failed call reads as before the first drop, so a stranger learns nothing of the hunt from an error.
  if (failed || (board !== null && !on)) return closed;
  // Nothing shows while the board loads, so the page never shows egg copy before it knows the hunt is on.
  if (board === null) return null;
  return <EggBoard board={board} />;
}
