/**
 * The egg board page part: it reads the board from the API at each visit, because the claims change at any time.
 * The page of the app mounts it under the top band.
 */
"use client";

import { useEffect, useState } from "react";
import type { Board, EggsApi } from "../lib/api";
import { EggBoard } from "./egg-board";

export function EggBoardScreen({ api }: { api: EggsApi }) {
  const [board, setBoard] = useState<Board | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    api.board().then(setBoard, () => setFailed(true));
  }, [api]);

  if (failed) return <p className="text-body">The egg board did not load. Try again in a few minutes.</p>;
  if (board === null) return <p className="text-body text-mute">The egg board loads.</p>;
  return <EggBoard board={board} />;
}
