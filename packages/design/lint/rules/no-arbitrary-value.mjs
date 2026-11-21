/**
 * The value rule: it fails an arbitrary color or spacing value, such as `bg-[...]`, in a className, a cn(...), or a template.
 * Variants, layout values, and motion values stay allowed (decision 03 of design-checks-speed, ADR 0038).
 */

/* The utilities of the color and spacing groups. A class fails when its utility, after the variants, is one of these
   with a bracket value. The list is exact, so `grid-cols-[...]` and `transition-[...]` stay allowed. */
const GROUPS = [
  "bg",
  "text",
  "border",
  "border-x",
  "border-y",
  "border-t",
  "border-r",
  "border-b",
  "border-l",
  "border-s",
  "border-e",
  "ring",
  "ring-offset",
  "fill",
  "stroke",
  "shadow",
  "p",
  "px",
  "py",
  "pt",
  "pr",
  "pb",
  "pl",
  "ps",
  "pe",
  "m",
  "mx",
  "my",
  "mt",
  "mr",
  "mb",
  "ml",
  "ms",
  "me",
  "gap",
  "gap-x",
  "gap-y",
  "inset",
  "inset-x",
  "inset-y",
  "top",
  "right",
  "bottom",
  "left",
  "start",
  "end",
];

/* The utility, an optional "-" for a negative value, then a bracket value and an optional opacity modifier. */
const ARBITRARY = new RegExp(`^!?-?(${GROUPS.join("|")})-\\[[^\\]]*\\]!?(/\\S+)?$`);

/* The utility of a class is the part after the last ":" that sits outside brackets, so `data-[state=open]:` is a variant. */
function utilityOf(className) {
  let depth = 0;
  let start = 0;
  for (let i = 0; i < className.length; i++) {
    const char = className[i];
    if (char === "[") depth++;
    else if (char === "]") depth--;
    else if (char === ":" && depth === 0) start = i + 1;
  }
  return className.slice(start);
}

/* A test may set an arbitrary value to check a part, so a test file is exempt, as in the element rule. */
function isTestFile(filename) {
  return /\.(test|spec)\.[cm]?[jt]sx?$/.test(filename.replaceAll("\\", "/"));
}

/* A string holds classes when it sits in a `className` prop, such as `contentClassName`, or in a `cn(...)` call, at any
   depth, so a ternary or a `&&` inside them counts. Any other plain string is not a class string, so it passes. */
function inClassPlace(node) {
  for (let parent = node.parent; parent; parent = parent.parent) {
    if (parent.type === "JSXAttribute") {
      const name = parent.name.type === "JSXIdentifier" ? parent.name.name : "";
      return name === "className" || name.endsWith("ClassName");
    }
    if (parent.type === "CallExpression" && parent.callee.type === "Identifier" && parent.callee.name === "cn") {
      return true;
    }
  }
  return false;
}

/* Each class of a string, with its offset in the string. */
function* classesOf(text) {
  for (const match of text.matchAll(/\S+/g)) yield { name: match[0], offset: match.index };
}

export default {
  meta: {
    type: "problem",
    docs: { description: "Fail an arbitrary Tailwind value in the color and spacing groups." },
    messages: {
      arbitrary:
        "`{{name}}` is an arbitrary value in the color and spacing groups. Use a role token or a scale step of apps/site/src/app/globals.css. For a true one-off, put `// oxlint-disable-next-line design/no-arbitrary-value -- <reason>` on the line above.",
    },
  },
  create(context) {
    if (isTestFile(context.filename)) return {};
    const sourceCode = context.sourceCode;

    /* The raw text starts at the node, so an offset in the raw text gives the line of the class itself. A string with an
       escape has no exact copy in the raw text, so its error sits at the start of the node. */
    function check(node, text) {
      const index = sourceCode.getText(node).indexOf(text);
      for (const { name, offset } of classesOf(text)) {
        if (!ARBITRARY.test(utilityOf(name))) continue;
        if (index < 0) {
          context.report({ node, messageId: "arbitrary", data: { name } });
          continue;
        }
        const base = node.range[0] + index + offset;
        const loc = { start: sourceCode.getLocFromIndex(base), end: sourceCode.getLocFromIndex(base + name.length) };
        context.report({ node, loc, messageId: "arbitrary", data: { name } });
      }
    }

    return {
      Literal(node) {
        if (typeof node.value === "string" && inClassPlace(node)) check(node, node.value);
      },
      TemplateElement(node) {
        check(node, node.value.raw);
      },
    };
  },
};
