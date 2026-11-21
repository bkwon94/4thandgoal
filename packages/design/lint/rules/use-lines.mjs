/**
 * The doc rule: the top docstring of a component file has a `Use it when:` line and a `Do not use it when:` line.
 * The config turns it on for the ui and parts folders only, and it skips the test files and a file with no component export.
 */

const REQUIRED_LINES = ["Use it when:", "Do not use it when:"];

/* A component name is PascalCase with a lowercase letter, so a constant such as `SHEET_CLASS` is not a component. */
const COMPONENT_NAME = /^[A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*$/;

/* The names that a value export of the program gives, and a flag for a default export. A type export gives no name. */
function exportsComponent(program) {
  for (const statement of program.body) {
    if (statement.type === "ExportDefaultDeclaration") return true;
    if (statement.type !== "ExportNamedDeclaration" || statement.exportKind === "type") continue;
    const names = [];
    const declaration = statement.declaration;
    if (declaration?.type === "FunctionDeclaration" || declaration?.type === "ClassDeclaration") {
      names.push(declaration.id?.name);
    } else if (declaration?.type === "VariableDeclaration") {
      for (const declarator of declaration.declarations) names.push(declarator.id.name);
    }
    for (const specifier of statement.specifiers ?? []) {
      if (specifier.exportKind !== "type") names.push(specifier.exported.name);
    }
    if (names.some((name) => name && COMPONENT_NAME.test(name))) return true;
  }
  return false;
}

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
        // The doc tells an agent which part to pick, so a file that exports no component needs no use lines.
        if (!exportsComponent(node)) return;
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
