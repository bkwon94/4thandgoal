/**
 * The egg board of the /eggs/ route, with the eggs routes of the API of the build.
 * It renders in the browser, because the claims change at any time.
 */
"use client";

import { eggsApi } from "@cpc/eggs/lib/api";
import { EggBoardScreen } from "@cpc/eggs/board/egg-board-screen";
import { eggsTarget } from "@/lib/config";

const api = eggsApi(eggsTarget);

export function EggBoardPart() {
  return <EggBoardScreen api={api} />;
}
