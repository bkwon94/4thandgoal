/**
 * The no-raw-color rule: it fails a hex, rgb(), hsl(), or oklch() literal in a string of a .tsx file.
 * A color comes from a role token, so a theme change reaches each part (ADR 0038).
 */

const RAW_COLOR = /(?<![\w&])#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4})\b|\b(?:rgba?|hsla?|oklch)\(/i;

const MESSAGE = "Use a role token, not a raw color literal.";

export default {
  meta: { type: "problem", messages: {} },
  create(context) {
    // Only .tsx files are in scope: the canvas code in .ts files draws with computed colors.
    if (!context.filename.endsWith(".tsx")) return {};
    return {
      Literal(node) {
        if (typeof node.value === "string" && RAW_COLOR.test(node.value)) {
          context.report({ node, message: MESSAGE });
        }
      },
      TemplateElement(node) {
        if (RAW_COLOR.test(node.value.cooked ?? node.value.raw)) {
          context.report({ node, message: MESSAGE });
        }
      },
    };
  },
};
