/**
 * The home banner of the eggs package: the egg banner under the top band of the home page, with the API of the build.
 * The registry of the client build imports it only when the client takes eggs, so another client shows no banner.
 */
"use client";

import { EggBannerScreen } from "@cpc/eggs/board/egg-banner";
import { eggsHref } from "@/lib/routes";
import { boardApi } from "./api";

export function HomeBanner() {
  return <EggBannerScreen api={boardApi} href={eggsHref()} />;
}
