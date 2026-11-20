/**
 * The doc rule: the top docstring of a component file has a `Use it when:` line and a `Do not use it when:` line.
 * The config turns it on for the ui and parts folders only, and it skips the test files.
 */

const REQUIRED_LINES = ["Use it when:", "Do not use it when:"];

export default {
  meta: {
    type: "problem",
    docs: { description: "Require the two use lines in the top docstring of a component file." },
    schema: [],
  },
  create(context) {
    // The agent that picks a part reads this docstring, so a test file needs no use lines.
    if (/\.test\.[cm]?[jt]sx?$/.test(context.filename)) return {};
    return {
      Program(node) {
        const [docstring] = context.sourceCode.getAllComments();
        const lines =
          docstring?.type === "Block"
            ? docstring.value.split("\n").map((line) => line.replace(/^\s*\*?\s?/, ""))
            : [];
        for (const required of REQUIRED_LINES) {
          if (!lines.some((line) => line.startsWith(required))) {
            context.report({
              node,
              message: `The top docstring has no line that starts with "${required}". Add it, and name the part to use instead where one exists.`,
            });
          }
        }
      },
    };
  },
};
