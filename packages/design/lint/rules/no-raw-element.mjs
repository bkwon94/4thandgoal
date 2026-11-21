/**
 * The element rule of the design plugin. It fails a JSX `<button>` or `<dialog>` in site code outside the ui folder.
 * The ui folder holds the wrappers, so each button and dialog keeps the look, the focus ring, and the focus trap of its wrapper.
 */

/* Each raw element maps to the wrapper of the ui folder that replaces it. The rule cannot tell a sync action from an
   async one, so the button text names both wrappers. */
const WRAPPERS = {
  button:
    '`Button` from packages/design/site/ui/button.tsx (`variant="plain"` keeps your own classes), or `PendingButton` from packages/design/site/ui/pending-button.tsx for an async action',
  dialog: "Dialog from packages/design/site/ui/dialog.tsx",
};

/* The ui folder holds the wrappers, and a test may render a raw element to check a wrapper, so both are exempt. */
function isExempt(filename) {
  const path = filename.replaceAll("\\", "/");
  return path.includes("/site/ui/") || /\.(test|spec)\.[cm]?[jt]sx?$/.test(path);
}

export default {
  meta: {
    type: "problem",
    docs: { description: "Fails a raw <button> or <dialog> outside the ui folder." },
    messages: {
      rawElement: "A raw <{{element}}> skips the wrapper of the ui folder. Use {{wrapper}}.",
    },
    schema: [],
  },
  create(context) {
    if (isExempt(context.filename)) return {};
    return {
      JSXOpeningElement(node) {
        if (node.name.type !== "JSXIdentifier") return;
        const wrapper = WRAPPERS[node.name.name];
        if (!wrapper) return;
        context.report({
          node,
          messageId: "rawElement",
          data: { element: node.name.name, wrapper },
        });
      },
    };
  },
};
