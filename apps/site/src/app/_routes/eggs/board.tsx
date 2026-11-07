/**
 * The egg board of the /eggs/ route, with the eggs routes of the API of the build.
 * It renders in the browser, because the claims change at any time, and the first egg drop turns it on.
 */
"use client";

import type { ReactNode } from "react";
import { EggBoardScreen } from "@cpc/eggs/board/egg-board-screen";
import { boardApi } from "./api";

export function EggBoardPart({ closed, title }: { closed: ReactNode; title: string }) {
  return <EggBoardScreen api={boardApi} closed={closed} title={title} />;
}
