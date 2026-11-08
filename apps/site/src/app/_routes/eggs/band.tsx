/**
 * The band part of the eggs package: the egg button in the top band of every page, with the API of the build.
 * The registry of the client build imports it only when the client takes eggs, so another client shows no egg button.
 */
"use client";

import { EggButtonScreen } from "@cpc/eggs/board/egg-button";
import { eggsHref } from "@/lib/routes";
import { boardApi } from "./api";

export function BandPart() {
  return <EggButtonScreen api={boardApi} href={eggsHref()} />;
}
