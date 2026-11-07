/**
 * The page part of the eggs package: the egg hunt on every page, with the eggs routes of the API of the build.
 * The registry of the client build imports it only when the client takes eggs, so another client ships no listener.
 */
"use client";

import { EggHunt } from "@cpc/eggs/hunt/egg-hunt";
import { boardApi } from "./api";

// One port for the whole visit, so the listener mounts once. The hunt reads the board of the shared port, so its check
// of the first drop shares the one board call of the egg button and the egg banner.
export function PagePart() {
  return <EggHunt api={boardApi} />;
}
