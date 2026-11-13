# The quick file

The format of the quick file of `4ag:quick`, its close, and its PR body. The shape is the same as "The quick file" in `docs/agents/issue-tracker.md`.

A run of Bugs writes `.scratch/bugs/<slug>.md`. A run of Quick wins writes `.scratch/quick-wins/<slug>.md`. The file is not under `issues/`, so it is no ticket and gets no row in `docs/agents/state.md`.

## The shape

````markdown
# <Title>

Kind: bug or quick-win
Status: in-progress
Branch: `bug-<slug>` or `win-<slug>`.
Source: the queue task `<name>`, a handoff file, or the session of <date>.
Boundary: the call on the four rules, in one line.

## Items

### 1. <Item title>

Done condition: <one sentence>
Method: diagnosing-bugs, tdd, or text only.
Cause: <for a Bug, the cause the loop found>
Red: <the command, and its output>
Green: <the same command at the fixed commit, and its output>
Test verdict: PASS, FAIL, BLOCKED, or none for a text-only item.

## Comments
````

## The first write

Step 4 of the skill writes the file before the build. Fill it this way:

1. `Kind:` is `bug` or `quick-win`. One kind per file.
2. `Status:` is `in-progress`.
3. `Source:` names each queue task, such as ``the queue task `Pick owner: week_moves names the first owner of a traded pick`.`` For a handoff file, give its path. For the words of Brian, write `the session of <date>`.
4. `Boundary:` holds the call on the four rules. See [the boundary line](#the-boundary-line).
5. Each item gets a heading `### <n>. <title>`, from 1 to at most 5.
6. `Done condition:` is one sentence.
7. `Method:` is `diagnosing-bugs`, `tdd`, or `text only`.
8. Write `Cause: pending`, `Red: pending`, `Green: pending`, and `Test verdict: pending`. A Quick win has no `Cause:` line.
9. `## Comments` is empty.

## The boundary line

One line, with the call and a reason for each rule:

```markdown
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.
```

At a boundary stop, name the rule that fails:

```markdown
Boundary: fails rule 3, no moved seam. The fix needs a new field in `page.json`.
```

## The Cause line

A Bug gets one line: the cause that the loop of `diagnosing-bugs` found, with the file and the function.

```markdown
Cause: `<function>` in `<file>` reads <what it reads>, so <what goes wrong>.
```

## The Red and Green blocks

Each block names the commit, the command, and the output. The output is cut to the lines that show the failure or the pass.

````markdown
Red: at `<red commit>`, `<command>`

```text
<the output, with the failed assertion and the wrong value>
```

Green: at `<fix commit>`, `<command>`

```text
<the output, with the pass>
```
````

The rules:

1. The red commit holds the loop and no fix. The fix commit holds the fix.
2. The command of Green is the command of Red, character for character.
3. The output of Red shows the bug of the done condition. For a Quick win, it shows the old behavior that the done condition names. An import error, a syntax error, a missing file, or a typo is not the bug.
4. The output of Green shows the pass.
5. A loop uses real data or the one fake of a port (ADR 0015). It adds no mock.

### When the hook runs the loop

The prek hook runs `make check-fast`. For the site, that runs the unit tests, so a red test fails the hook. Never use `--no-verify`. Do this instead:

1. Commit the loop and the fix together. This is the fix commit.
2. Get the red output on the parent of the fix commit, with the loop file of the fix commit. Run `git checkout <fix commit> -- <loop file>` on a detached checkout of the parent in a scratch worktree, then the command.
3. Write the Red line as: ``Red: at `<parent commit>` with `<loop file>` of `<fix commit>`, `<command>` ``.
4. Remove the scratch worktree.

### A phone-only bug

A bug that shows only on the phone of Brian gets its red output from one screenshot of a LAN probe page. Put the screenshot under `.scratch/bugs/<slug>/`. The Red block names the page, the commit it served, and the path of the screenshot. The Green block names a second screenshot of the same page at the fix commit.

### A text-only item

A text-only item changes only text or config, which no test can show. The orchestrator edits it and fills it this way:

```markdown
Red: none, text only.
Green: at `<commit>`, the diff of the text.
Test verdict: none
```

## The Test verdict line

Only the quick Judge gives a Test verdict. The orchestrator copies each line of its reply word for word. See [`judge.md`](judge.md).

```markdown
Test verdict: PASS
Test verdict: FAIL <one sentence of reason>
Test verdict: BLOCKED <one sentence of reason>
Test verdict: none
```

## The close

The last commit before the push closes the file. Only the merge puts `done` on `main`.

1. Set `Status: done`.
2. Check that each Bug has a `Cause:` line and each item has a `Test verdict:` line.
3. Add one close comment under `## Comments`, in the shape of "The close comment" in `docs/agents/issue-tracker.md`. Each line is one sentence:
   1. The merge: "Closes with the squash merge of the PR of `<branch>`. Commits: `<sha>`, `<sha>`. Date: <date>."
   2. The proof: the test count, and that the loop of each item went red, then green.
   3. The notes for a later run, if any.
   4. The files read: "Read N files: path, path, path."
4. Do not touch `docs/agents/state.md`.

## The PR

The title is `Bug: <title>` for a run of Bugs, or `Quick win: <title>` for a run of Quick wins.

The body:

````markdown
## The quick run

<one or two sentences: what was wrong or what changes, in terms of code and behavior.>

Quick file: `<path of the quick file>`. Branch: `<branch>`. No spec and no `ACCEPTANCE.md` exist, so the check `verdict` does not apply (ADR 0033).

## The items

1. **<item title>**
   - Done condition: <done condition>
   - Method: <method>
   - Test verdict: <the Test verdict line of the item, word for word>

## The Test verdicts

The quick Judge, a fresh subagent that did not build the work, gave each Test verdict from the done condition and the red and green evidence only. A text-only item has no Test verdict. Brian merges.
````

### No manager name

The repo is public, so the PR title and body name no league manager and no team (ADR 0021). Write each item in terms of code and behavior, never a person. The quick file may hold a name. The PR may not.

Run this check at the worktree root, with the body file and the title. Rewrite the body until it prints `Hits: none.`

```sh
python3 - <body file> "<title>" <<'EOF'
import json, pathlib, re, sys
text = (pathlib.Path(sys.argv[1]).read_text() + "\n" + sys.argv[2]).lower()
names = set()
for path in pathlib.Path("clients").glob("*/data/**/users.json"):
    for user in json.loads(path.read_text()):
        names.add(user.get("display_name") or "")
        names.add((user.get("metadata") or {}).get("team_name") or "")
names.discard("")
hits = sorted(name for name in names if re.search(rf"\b{re.escape(name.lower())}\b", text))
print(f"Checked {len(names)} names. Hits: {', '.join(hits) or 'none'}.")
EOF
```
