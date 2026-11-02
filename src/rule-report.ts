/**
 * Prints each offense of a rule test in one shape: the location and rule id, what is wrong, the rule, and the fix.
 * Only the rule tests import it, and it imports no app code, so the build never bundles it.
 */

/* The line is a number for a source file. A JSON parse gives no line, so a published file gives the field path. */
export type Offense = {
  path: string;
  line: number | string;
  ruleId: string;
  what: string;
  rule: string;
  adr: string;
  fix: string;
};

/* An agent can fix the offense from these four lines without the ADR. */
function format(offense: Offense): string {
  return [
    `${offense.path}:${offense.line}  ${offense.ruleId}`,
    `  ${offense.what}`,
    `  Rule: ${offense.rule} (${offense.adr}).`,
    `  Fix: ${offense.fix}`,
  ].join("\n");
}

/* The count comes first, so a reader knows the size of the work before the list. */
export function report(offenses: Offense[]): string {
  const count = `${offenses.length} ${offenses.length === 1 ? "offense" : "offenses"}.`;
  return [count, ...offenses.map(format)].join("\n\n");
}
