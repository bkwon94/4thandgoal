/**
 * The page part of the eggs package: the egg hunt on every page, with the eggs routes of the API of the build.
 * The registry of the client build imports it only when the client takes eggs, so another client ships no listener.
 */
"use client";

import { eggsApi } from "@cpc/eggs/lib/api";
import { EggHunt } from "@cpc/eggs/hunt/egg-hunt";
import { eggsTarget } from "@/lib/config";

// One port for the whole visit, so the listener mounts once.
const api = eggsApi(eggsTarget);

export function PagePart() {
  return <EggHunt api={api} />;
}
