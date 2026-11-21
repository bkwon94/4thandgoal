/**
 * A lint fixture: a part that exports a component and has no use line in its top docstring.
 * Do not use it when: a test needs a part that passes the doc rule.
 */
export function NoUseLine() {
  return <p>No use line</p>;
}
