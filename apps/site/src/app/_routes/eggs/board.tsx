/**
 * The egg board of the /eggs/ route, with the eggs routes of the API of the build.
 * It renders in the browser, because the claims change at any time.
 */
"use client";

import { EggBoardScreen } from "@cpc/eggs/board/egg-board-screen";
import { boardApi } from "./api";

export function EggBoardPart() {
  return <EggBoardScreen api={boardApi} />;
}
