/**
 * The local lint plugin of the design rules. It uses the ESLint plugin shape, so Oxlint runs it through jsPlugins.
 * Canary `bun lint` runs the same file, so the rules move to `bun lint` with no rewrite (ADR 0038).
 */
import noRawElement from "./rules/no-raw-element.mjs";

export default {
  meta: { name: "design" },
  rules: {
    "no-raw-element": noRawElement,
  },
};
