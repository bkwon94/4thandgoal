/**
 * The local lint plugin of the design rules. It uses the ESLint plugin shape, so Oxlint runs it through jsPlugins.
 * Canary `bun lint` runs the same file, so the rules move to `bun lint` with no rewrite (ADR 0038).
 */

import noArbitraryValue from "./rules/no-arbitrary-value.mjs";
import noRawColor from "./rules/no-raw-color.mjs";
import useLines from "./rules/use-lines.mjs";

export default {
  meta: { name: "design" },
  rules: {
    "no-arbitrary-value": noArbitraryValue,
    "no-raw-color": noRawColor,
    "use-lines": useLines,
  },
};
