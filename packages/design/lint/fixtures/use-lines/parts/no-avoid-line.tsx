/**
 * A lint fixture: a part that exports a component and has no avoid line in its top docstring.
 * Use it when: a test needs a part that fails the doc rule.
 */
export function NoAvoidLine() {
  return <p>No avoid line</p>;
}
