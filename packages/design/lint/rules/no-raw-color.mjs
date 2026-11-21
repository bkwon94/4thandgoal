/**
 * The no-raw-color rule: it fails a hex, rgb(), hsl(), or oklch() literal in a string of a .tsx file.
 * A color comes from a role token, so a theme change reaches each part (ADR 0038).
 */

const RAW_COLOR =
  /(?<![\w&])#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4})\b|\b(?:rgba?|hsla?|oklch)\(/i;

const MESSAGE = "Use a role token of apps/site/src/app/globals.css, not a raw color literal.";

export default {
  meta: { type: "problem", messages: {} },
  create(context) {
    // Only .tsx files are in scope. The canvas code in .ts files, such as mesh-canvas.ts, paints a canvas that no role
    // token reaches, so it may hold a raw color, such as the "#000" of a mask.
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
