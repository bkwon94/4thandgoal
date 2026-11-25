/**
 * Reads the Trades closed value that a client build wrote into src/generated/client-values.ts.
 * The build decides it from its own clock, so check-export reads it here and never asks the real clock.
 */

/* True or false, as the build wrote it. Throws when the text has no such value, so a changed file format fails loud. */
export function tradesClosedOfBuild(generatedText) {
  const match = /"tradesClosed":\s*(true|false)\b/.exec(generatedText);
  if (match === null) throw new Error("the generated client values hold no tradesClosed value");
  return match[1] === "true";
}
