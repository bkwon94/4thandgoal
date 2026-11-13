# Static capture method

Implementation: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.

The collector uses Python standard-library functions and read-only Git commands.
`git show <revision>:<path>` supplies each quoted file and its original line numbers.
`git ls-tree -r --name-only <implementation>` supplies the file inventory for relative-link checks.
The checker resolves each Markdown target against its source folder, with POSIX path normalization.
Directories exist when the tree contains a file under their path.
`git diff --no-ext-diff --binary <base> <implementation>` supplies the complete feature diff.
The product diff adds the 13 approved document path arguments after `--`.
`git diff --name-status <base> <implementation>` supplies the full changed-file list.
`git rev-parse <implementation>:<path>` supplies each product blob identifier.
Byte equality compares every worktree product document with its implementation Git object.
Python AST parses product imports and extracts complete Python functions or classes without execution.
Physical line counts use `splitlines()`, which includes blank lines and excludes a phantom line after the final newline.
No dependency command, behavior test, or cold trial runs during this static capture.

## Observed counts

Resolved relative links checked: 37. Missing targets: 0.
Product byte comparisons: 13 equal. Evidence entries: 17.

```text
apps/site/src/lib/data/README.md: 23
apps/pipeline/src/cornerstone/README.md: 24
apps/api/src/cornerstone_api/README.md: 24
packages/analyzer/README.md: 24
packages/analyzer/site/form/README.md: 24
packages/week/README.md: 22
packages/week/python/src/week/sheet/README.md: 23
```
