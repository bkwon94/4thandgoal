/**
 * The stable id of an element that the egg hunt can name, and the marks of the state that an egg check reads.
 * A content package tags its elements with these names, so no content package imports the eggs package.
 */

/* The attribute of each element that an egg check can name. The value derives from the data that the element
   renders, such as the chapter, the roster, and the row, so a new render of the same data keeps the id. Every element
   of each class of target carries one on every page, with an egg or not, so no id marks an egg. */
export const STABLE_ID = "data-stable-id";

/* The attribute of an element whose open state is a condition, such as a "Show all", a chip, or a fold. The element
   is open when it has aria-expanded, aria-pressed, aria-selected, or aria-checked true, the open attribute, or a
   data-state of open or on. */
export const OPEN_ID = "data-open-id";

/* The marks of the outcome of the sim replay, on its root: the roster id of the champion, and the seed of each roster
   as "roster:seed" with a space between. */
export const SIM_CHAMPION = "data-sim-champion";
export const SIM_SEEDS = "data-sim-seeds";

/* The marks of the analyzer result, on its root: the trade key and the answer word of the decision. */
export const TRADE_KEY = "data-trade-key";
export const TRADE_ANSWER = "data-trade-answer";

/* The mark of the 404 page. */
export const NOT_FOUND = "data-not-found";

/* The stable id of the data that an element renders, as a string. Each part is in lower case, and each run of marks
   that is not a letter or a digit is one dash. */
export function stableKey(...parts: (string | number)[]): string {
  return parts
    .map((part) => String(part).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, ""))
    .filter((part) => part !== "")
    .join("-");
}

/* The stable id of the data that an element renders, as props to spread on the element. */
export function stableId(...parts: (string | number)[]): { [STABLE_ID]: string } {
  return { [STABLE_ID]: stableKey(...parts) };
}

/* The stable id of an element whose data is its text, such as a blurb: the prefix and a short hash of the text.
   The hash is FNV-1a of 32 bits in base 36, so the id is short and one text always gives one id. */
export function textId(prefix: string, text: string): { [STABLE_ID]: string } {
  let hash = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return stableId(prefix, hash.toString(36));
}

/* The open id of a toggle whose open state is a condition, as props to spread on the element. The parts join as in
   stableId. */
export function openId(...parts: (string | number)[]): { [OPEN_ID]: string } {
  return { [OPEN_ID]: stableKey(...parts) };
}
