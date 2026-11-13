# The GitHub commands of a round

Run each command in the worktree of the Spec branch. `gh api` fills `{owner}` and `{repo}` from the checkout. Write each file in a scratch folder outside the repo, `<scratch>`, not in the worktree.

## The review threads

```sh
gh api graphql -F owner='{owner}' -F name='{repo}' -F number=<PR number> -f query='
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes { isResolved path line
          comments(first: 50) { nodes { databaseId author { login } body createdAt } } }
      }
    }
  }
}'
```

A thread needs an action when `isResolved` is false and its last comment has no agent marker. The `databaseId` of its first comment is the id for the reply.

## The review bodies

```sh
gh api "repos/{owner}/{repo}/pulls/<PR number>/reviews" --jq '.[] | select(.body != "") | {id, state, body, submitted_at}'
```

A review body with no marker, later than the last round comment, needs an action.

## The PR comments

```sh
gh api --paginate "repos/{owner}/{repo}/issues/<PR number>/comments?per_page=100" \
  --jq '.[] | {id, user: {login: .user.login}, created_at, body}' | jq -s . > <scratch>/comments.json
```

The last round comment is the latest comment that holds the agent marker and starts with `Feedback round`. Its number plus one is the number of this round. With none, this is round 1.

## The Test verdicts

The verdict check reads `VERDICTS.md` of the Judge and the same comments, so use its script:

```sh
python3 scripts/verdict.py .scratch/<slug>/ACCEPTANCE.md --verdicts .scratch/<slug>/VERDICTS.md --evidence .scratch/<slug>/EVIDENCE.md --comments <scratch>/comments.json --owner "$(gh repo view --json owner --jq .owner.login)"
```

Each offense names its rule:

- `verdict/brian-fail` names a test with FAIL or BLOCKED from Brian. Its line in his latest Test verdicts comment holds his note. It needs an action.
- `verdict/not-pass` names a test with FAIL or BLOCKED from the Judge. Its line in `VERDICTS.md` holds the reason of the Judge.
- `verdict/stale-acceptance` or `verdict/stale-evidence` means the file changed after the Judge read it. Run a fresh Judge.
- `verdict/missing`, `verdict/unknown`, `verdict/duplicate`, or `verdict/no-verdicts` means `VERDICTS.md` does not match `ACCEPTANCE.md`. Run a fresh Judge on those tests.

A comment of Brian with no FAIL and no BLOCKED gives no offense. Brian never needs to post PASS.

## Replies

Write each reply to a file. End it with the agent marker `<!-- cpc:agent -->` on its own last line.

- A reply in a review thread: `gh api "repos/{owner}/{repo}/pulls/<PR number>/comments/<databaseId>/replies" -F body=@<file>`.
- A reply to a PR comment or a review body: `gh pr comment <PR number> --body-file <file>`. Quote the first line of the comment, so Brian sees which one it answers.
- The round comment: `gh pr comment <PR number> --body-file <file>`.

An evidence link names the commit: `<repo url>/blob/<short sha>/.scratch/<slug>/evidence/AT-<n>/`.
