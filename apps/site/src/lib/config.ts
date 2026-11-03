/**
 * Build-time config. This is the only module that reads process.env.
 * All values have a default, so a bare build works.
 */
export const apiUrl =
  process.env.NEXT_PUBLIC_API_URL ?? "https://api.cpcfantasy.com";

// The Pages base path. Empty because the site lives at the domain root.
export const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

// The league season the teams and analyze routes read. One constant until the page needs a picker.
// An empty or non-numeric value falls back to 2026, because Number("") is 0.
const DEFAULT_SEASON = 2026;
const parsedSeason = Number(process.env.NEXT_PUBLIC_SEASON);
export const season = Number.isFinite(parsedSeason) && parsedSeason > 0 ? parsedSeason : DEFAULT_SEASON;

// The trade finder stays hidden until the page layout has room for it.
// A build with NEXT_PUBLIC_FINDER=on shows it.
export const finderOn = process.env.NEXT_PUBLIC_FINDER === "on";

// The waiver page stays hidden until the pipeline writes a full week file.
// A build with NEXT_PUBLIC_WAIVER=on builds the route and the masthead link.
export const waiverOn = process.env.NEXT_PUBLIC_WAIVER === "on";

// The GoatCounter site code. The count script loads only when it is set.
// A build with NEXT_PUBLIC_USAGE_CODE="" sends nothing.
export const usageCode = process.env.NEXT_PUBLIC_USAGE_CODE ?? "cpcfantasy";
