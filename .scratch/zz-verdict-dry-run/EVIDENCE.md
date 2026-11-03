# Dry run: the pipeline README names the verdict check: evidence

Spec: `.scratch/zz-verdict-dry-run/PRD.md`. Acceptance tests: `.scratch/zz-verdict-dry-run/ACCEPTANCE.md`.
Built from: `d79caa6`, on 2026-11-03. The agent gives no Test verdict. Brian gives one for each test.

## AT-1: The pipeline README names the verdict check

App: pipeline
Then: the output holds one line that names the check `verdict` and ADR 0020 (dry run)
Files: `evidence/AT-1/output.txt`
Observation: the command prints one line, line 5, which names the check `verdict` and ADR 0020.

## AT-2: The home page stays as it is

App: site
Then: the home page shows the week 8 report, with no new text (dry run)
Files: `evidence/AT-2/375-light.png`, `evidence/AT-2/375-dark.png`, `evidence/AT-2/768-light.png`, `evidence/AT-2/768-dark.png`, `evidence/AT-2/1280-light.png`, `evidence/AT-2/1280-dark.png`
Observation: the home page shows the season 2026 index, with Week 8 first under Weekly Reports, and no text about the verdict check.
