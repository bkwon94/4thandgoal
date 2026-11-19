/**
 * The mode of the analyzer, one half of the switch in its hero: Grade a trade, or Find a trade.
 * The query of a link names it, such as /analyze/?mode=find, so a link of the Trade Wire opens the right half.
 */

export type AnalyzerMode = "grade" | "find";

/* Find needs the finder flag, so with the flag off every link opens Grade. A missing or unknown mode opens Grade. */
export function readMode(search: string, finderOn: boolean): AnalyzerMode {
  const mode = new URLSearchParams(search).get("mode");
  return mode === "find" && finderOn ? "find" : "grade";
}

/* The query with its mode set, so the address names the half on the screen and a reload or a share keeps it. */
export function withMode(search: string, mode: AnalyzerMode): string {
  const query = new URLSearchParams(search);
  query.set("mode", mode);
  return `?${query.toString()}`;
}
