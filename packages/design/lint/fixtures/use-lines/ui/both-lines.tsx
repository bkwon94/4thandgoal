/**
 * A lint fixture: a primitive that exports a component and has both use lines in its top docstring.
 * Use it when: a test needs a file that passes the doc rule.
 * Do not use it when: a test needs a file that fails the doc rule.
 */
export function BothLines() {
  return <p>Both lines</p>;
}
