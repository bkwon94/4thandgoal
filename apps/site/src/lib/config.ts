/**
 * Build-time config. This is the only module that reads process.env, and it passes on the client values of the build.
 * A value that changes with the deploy is an env value. A value that changes with the league comes from client.toml.
 */
// Relative import, not the @ alias: next.config imports this module, and its loader does not resolve the alias.
// A type import only, so the next.config loader never loads the analyzer package.
import type { ApiTarget } from "@cpc/analyzer/lib/api";
import { clientValues } from "../generated/client-values";

export const apiUrl =
  process.env.NEXT_PUBLIC_API_URL ?? "https://api.cpcfantasy.com";

// The Pages base path. Empty because the site lives at the domain root.
export const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

// The league season the teams and analyze routes read: the latest season of the client.
export const season = clientValues.season;

// The API of the analyzer: the base URL, the slug of the client of the build, and the season. Each call goes to
// /clients/<slug>/ of the API.
export const apiTarget: ApiTarget = { url: apiUrl, client: clientValues.slug, season };

// The trade finder, from finder under [values.analyzer] of client.toml.
export const finderOn = clientValues.finder;

// The GoatCounter site code, from usage_code of client.toml. The count script loads only when it is set.
export const usageCode = clientValues.usageCode;

// The sets of brand.toml in paint order. Their count decides the first paint and the theme button.
export const brandSets = clientValues.brand.sets;
