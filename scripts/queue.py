"""
Makes the Todoist project 4thandgoal, the queue, match the tracker in .scratch/. Each subcommand plans its td calls.
Skills call it with python3. It uses only the Python standard library. See .scratch/todoist-queue/PRD.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

PROJECT = "4thandgoal"
REPO = "bkwon94/4thandgoal"
GITHUB = f"https://github.com/{REPO}/blob/main"

# The statuses that Brian sets in the queue. A push writes one of them only when it makes the task.
TRIAGE_STATUSES = ("needs-triage", "needs-info", "ready-for-agent", "ready-for-human")
# The statuses that only the skills set. A push always writes them.
FLOW_STATUSES = ("in-progress", "in-review", "blocked")
OPEN_STATUSES = TRIAGE_STATUSES + FLOW_STATUSES
# The statuses of a closed ticket. Only the flow sets them.
CLOSED_STATUSES = ("done", "wontfix")
APPS = ("site", "pipeline", "api")
# A push replaces only these labels on a task, and keeps every other label that Brian adds.
FLOW_LABELS = OPEN_STATUSES + ("wontfix", "decision") + APPS

# An open decision ticket waits on Brian or on an agent by its kind. A grill and a prototype need Brian. A research and
# a spec ticket are work that an agent clears.
DECISION_KINDS = {"grill": "ready-for-human", "prototype": "ready-for-human", "research": "ready-for-agent",
                  "spec": "ready-for-agent"}

# The metadata lines of a ticket, such as "**Status:** ready-for-agent".
STATUS_LINE = re.compile(r"^\*\*Status:\*\*\s*(\S*)", re.MULTILINE)
KIND_LINE = re.compile(r"^\*\*Kind:\*\*\s*(\S*)", re.MULTILINE)
BLOCKED_LINE = re.compile(r"^\*\*Blocked by:\*\*\s*(.*?)\s*$", re.MULTILINE)
WHAT_TO_BUILD = re.compile(r"^\*\*What to build:\*\*\s*(.+)$", re.MULTILINE)
# A paragraph that is not prose: a heading, a metadata line such as "**Kind:** grill", or a pointer such as "Map: x".
NOT_PROSE = re.compile(r"^(#|\*\*[^*]+:\*\*|[A-Z][A-Za-z ]*: |[-*] |\d+\. )")
H1 = re.compile(r"^#\s+(?:(\d+):\s*)?(.+?)\s*$", re.MULTILINE)
SUMMARY_LIMIT = 500
# A dead network can hang one `td` call for about 2 minutes, because the SDK retries. A push gives up sooner. A `gh`
# call has the same limit.
CALL_TIMEOUT = 10


@dataclass(frozen=True)
class Ticket:
    """One ticket or decision ticket, as the push reads it from its file."""
    key: str
    feature: str
    title: str
    status: str
    decision: bool
    apps: tuple[str, ...]
    description: str


def _feature(key: str) -> str:
    """The feature slug, the folder under .scratch/, which names the section of the task."""
    return key.split("/")[1]


def _app_words(text: str) -> tuple[str, ...]:
    """The app labels that a text names, in the order of APPS. `both` names the site and the pipeline."""
    words = set(re.findall(r"[a-z]+", text.lower()))
    if "both" in words:
        words |= {"site", "pipeline"}
    return tuple(app for app in APPS if app in words)


# A reader gives the text of a file by its path from the repo root, or None when the file does not exist. It reads the
# checkout, or a branch for a feature on a live spec branch.
Reader = Callable[[str], "str | None"]


def checkout_reader(root: Path) -> Reader:
    """Read the files of the checkout at the root."""
    def read(path: str) -> str | None:
        file = root / path
        return file.read_text() if file.is_file() else None
    return read


def branch_reader(root: Path, branch: str) -> Reader:
    """Read the files of a branch of the repo at the root, with no checkout of that branch."""
    def read(path: str) -> str | None:
        show = subprocess.run(["git", "-C", str(root), "show", f"{branch}:{path}"], capture_output=True, text=True,
                              env=_clean_git_env())
        return show.stdout if show.returncode == 0 else None
    return read


def _apps(read: Reader, key: str) -> tuple[str, ...]:
    """The app of a ticket: the subfolder of a shared feature, else the App column of its row in state.md, else the
    Apps line of its PRD."""
    parts = key.split("/")
    if len(parts) > 3 and parts[2] in APPS:
        return (parts[2],)
    feature = parts[1]
    state = read("docs/agents/state.md")
    if state is not None:
        row = re.compile(rf"^\|\s*`?{re.escape(feature)}`?\s*\|\s*([^|]*)\|", re.MULTILINE)
        apps = _app_words(" ".join(row.findall(state)))
        if apps:
            return apps
    prd = read(f".scratch/{feature}/PRD.md")
    if prd is not None:
        line = re.search(r"^Apps:([^.\n]*)", prd, re.MULTILINE)
        if line:
            return _app_words(line.group(1))
    return ()


def _on_main(root: Path, key: str) -> bool:
    """Whether the file exists on the branch main of the repo at the root.

    A root that is not the top of a git repo has no main, such as a folder of fixtures inside the repo.
    """
    return _is_repo_top(root) and _git(root, "cat-file", "-e", f"main:{key}").returncode == 0


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=_clean_git_env())


def _is_repo_top(root: Path) -> bool:
    """Whether the root is the top of a git repo, and not a folder inside one."""
    top = _git(root, "rev-parse", "--show-toplevel")
    return top.returncode == 0 and Path(top.stdout.strip()).resolve() == root.resolve()


def _clean_git_env() -> dict[str, str]:
    """The environment with no GIT_ variable. A git hook sets GIT_DIR and GIT_INDEX_FILE, which would point the call at
    the repo of the hook in place of the root."""
    return {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}


def _summary(text: str) -> str | None:
    """The inline `**What to build:**` text, or else the first paragraph of prose of the body, cut to 500 characters."""
    match = WHAT_TO_BUILD.search(text)
    if match:
        summary = match.group(1)
    else:
        paragraphs = (p.strip() for p in re.split(r"\n\s*\n", text))
        summary = next((p for p in paragraphs if p and not NOT_PROSE.match(p)), None)
        if summary is None:
            return None
    summary = " ".join(summary.split())
    return summary if len(summary) <= SUMMARY_LIMIT else summary[:SUMMARY_LIMIT - 3] + "..."


def load_ticket(root: Path, path: Path) -> Ticket:
    """Read the ticket at the path. The key is its path from the root, as the first line of the task description."""
    key = path.resolve().relative_to(root.resolve()).as_posix()
    return ticket_of(root, key, path.read_text(), checkout_reader(root))


def ticket_of(root: Path, key: str, text: str, read: Reader) -> Ticket:
    """The ticket with the key and the text. The reader gives state.md and the PRD from the same place as the text."""
    path = Path(key)
    number, name = H1.search(text).groups()
    number = number or path.name.split("-")[0]
    decision = _is_decision(path)
    status = (_first(STATUS_LINE, text) or "").rstrip(".,;:")
    if decision and status == "open":
        status = DECISION_KINDS.get(_first(KIND_LINE, text), "needs-triage")
    # A ticket with no Status line is open. An odd word, which the tracker rule rejects, never becomes a label.
    if status not in OPEN_STATUSES + CLOSED_STATUSES:
        status = "needs-triage"
    blocked = _first(BLOCKED_LINE, text)
    # "None (can start immediately)." and "none. Before this ticket, ..." both mean no blocker.
    if blocked and re.match(r"none\b", blocked, re.IGNORECASE):
        blocked = None
    feature = _feature(key)
    apps = _apps(read, key)
    lines = [
        f"4ag: {key}",
        f"App: {', '.join(apps)}" if apps else None,
        f"Blocked by: {blocked}" if blocked else None,
        f"{GITHUB}/{key}" if _on_main(root, key) else f"On the spec branch {feature}.",
        _summary(text),
    ]
    return Ticket(
        key=key, feature=feature, title=f"Decision {number}: {name}" if decision else f"{number} {name}",
        status=status, decision=decision, apps=apps, description="\n".join(line for line in lines if line),
    )


def _is_decision(path: Path) -> bool:
    """Whether the ticket at the path is a decision ticket, a file in a decisions/ folder."""
    return path.parent.name == "decisions"


def _first(pattern: re.Pattern, text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1) if match else None


@dataclass
class Queue:
    """The project, its sections, its open tasks, and the labels, as `td` reads them."""
    project_id: str
    sections: dict[str, str]
    tasks: list[dict]
    labels: set[str]

    @classmethod
    def from_json(cls, projects: str, sections: str, tasks: str, labels: str) -> "Queue":
        """The queue from the text of four `td` reads, as a test reads it from the saved files."""
        return cls.from_data(json.loads(projects), json.loads(sections), json.loads(tasks), json.loads(labels))

    @classmethod
    def from_data(cls, projects: dict, sections: dict, tasks: dict, labels: dict) -> "Queue":
        return cls(
            project_id=project_id(projects),
            sections={section["name"]: section["id"] for section in sections["results"]},
            tasks=tasks["results"],
            labels={label["name"] for label in labels["results"]} | set(labels.get("sharedLabels") or []),
        )

    def task(self, key: str) -> dict | None:
        """The open task whose description starts with the key line of the ticket.

        No Todoist filter reads a description, so the match is local, on the one read of the open tasks.
        """
        return task_of(self.tasks, key)


def task_of(tasks: list[dict], key: str) -> dict | None:
    """The task whose description starts with the key line of the ticket, `4ag: <key>`."""
    line = f"4ag: {key}"
    return next((task for task in tasks if (task.get("description") or "").split("\n")[0] == line), None)


def project_id(projects: dict) -> str:
    """The id of the project 4thandgoal. The repo holds no Todoist id, so the script finds the project by its name."""
    for project in projects["results"]:
        if project["name"] == PROJECT:
            return project["id"]
    raise QueueError("NO_PROJECT", f"Todoist has no project named {PROJECT}")


def plan_push(ticket: Ticket, queue: Queue) -> list[list[str]]:
    """The `td` commands that make the task of the ticket match its file. Each command omits the leading `td`.

    No command sets the priority or the order, because the queue owns them.
    """
    task = queue.task(ticket.key)
    closed = ticket.status in CLOSED_STATUSES
    if task is None:
        # A closed ticket never enters the queue.
        return [] if closed else _plan_add(ticket, queue)

    labels = _labels(ticket, task["labels"])
    plan = [["label", "create", "--name", label] for label in labels
            if label in FLOW_LABELS and label not in queue.labels]
    update = []
    if task["content"] != ticket.title:
        update += ["--content", ticket.title]
    if _bare_links(task["description"]) != ticket.description:
        update += ["--description", ticket.description]
    if set(labels) != set(task["labels"]):
        update += ["--labels", ",".join(labels)]
    if update:
        plan.append(["task", "update", f"id:{task['id']}", *update])
    section = queue.sections.get(ticket.feature)
    if section is None:
        plan.append(_section_create(ticket.feature, queue))
        plan.append(["task", "move", f"id:{task['id']}", "--project", f"id:{queue.project_id}",
                     "--section", ticket.feature])
    elif task["sectionId"] != section:
        plan.append(["task", "move", f"id:{task['id']}", "--section", f"id:{section}"])
    # Only the merge sweep completes the task of a done ticket. A done decision ticket has no merge, so it completes
    # here.
    if ticket.status == "wontfix" or (ticket.status == "done" and ticket.decision):
        plan.append(["task", "complete", f"id:{task['id']}"])
    return plan


# Todoist stores a bare URL in a description as a markdown link with the title of the page, `[<title>](<url>)`.
TITLED_LINK = re.compile(r"\[[^\]\n]*\]\((https?://[^)\s]+)\)")


def _bare_links(description: str) -> str:
    """The description with each titled link back as its bare URL, as the push writes it."""
    return TITLED_LINK.sub(r"\1", description)


def _labels(ticket: Ticket, current: list[str]) -> list[str]:
    """The labels of the task: the labels of Brian outside the flow, then the status, `decision`, and the apps.

    A flow status in the file always wins. A triage status that Brian set in the queue wins over a triage status
    in the file, because the queue owns the triage. A flow label in the queue gives way to the file, because only
    the skills set a flow label, and a file back at a triage status means a skill moved the ticket on.
    """
    others = [label for label in current if label not in FLOW_LABELS]
    queued = next((label for label in current if label in OPEN_STATUSES), None)
    if ticket.status in TRIAGE_STATUSES and queued in TRIAGE_STATUSES:
        status = queued
    elif ticket.status == "done":
        # A done decision ticket completes with no status label. A done ticket keeps its label until the sweep.
        status = None if ticket.decision else queued
    else:
        status = ticket.status
    flow = [status] if status else []
    return others + flow + (["decision"] if ticket.decision else []) + list(ticket.apps)


def _section_create(feature: str, queue: Queue) -> list[str]:
    return ["section", "create", "--name", feature, "--project", f"id:{queue.project_id}"]


def _plan_add(ticket: Ticket, queue: Queue) -> list[list[str]]:
    """Make the task. A command after a planned `section create` names the section, because its id is not known yet."""
    labels = _labels(ticket, [])
    plan = [["label", "create", "--name", label] for label in labels if label not in queue.labels]
    section = queue.sections.get(ticket.feature)
    if section is None:
        plan.append(_section_create(ticket.feature, queue))
    plan.append(["task", "add", ticket.title, "--project", f"id:{queue.project_id}",
                 "--section", f"id:{section}" if section else ticket.feature,
                 "--labels", ",".join(labels), "--description", ticket.description])
    return plan


# The kinds of a wait task, each with its title. The section names the feature, so the title does not.
WAIT_TITLES = {"approve-prd": "Approve PRD", "approve-acceptance": "Approve ACCEPTANCE",
               "approve-tickets": "Approve tickets", "merge-pr": "Merge PR #{}"}
PULL = f"https://github.com/{REPO}/pull"


def plan_wait(feature: str, kind: str, number: int | None, done: bool, queue: Queue) -> list[list[str]]:
    """The `td` commands that open the wait task of one step that waits on Brian, or complete it when done is set.

    The key of a wait task is `<feature>/wait/<kind>`. A feature can wait on two PRs at once, so the title of the task
    tells two merge-pr tasks apart.
    """
    key = f"{feature}/wait/{kind}"
    title = WAIT_TITLES[kind].format(number)
    task = next((task for task in queue.tasks if _key(task) == key and (number is None or task["content"] == title)),
                None)
    if done:
        return [["task", "complete", f"id:{task['id']}"]] if task else []
    if task:
        return []
    lines = [f"4ag: {key}"]
    if kind == "merge-pr":
        lines.append(f"{PULL}/{number}")
    plan = [["label", "create", "--name", "ready-for-human"]] if "ready-for-human" not in queue.labels else []
    section = queue.sections.get(feature)
    if section is None:
        plan.append(_section_create(feature, queue))
    plan.append(["task", "add", title, "--project", f"id:{queue.project_id}",
                 "--section", f"id:{section}" if section else feature,
                 "--labels", "ready-for-human", "--description", "\n".join(lines)])
    return plan


MERGE_PR_TITLE = re.compile(r"^Merge PR #(\d+)$")


def _key(task: dict) -> str | None:
    """The key of a task, from the first line of its description, such as `4ag: <path>`."""
    line = (task.get("description") or "").split("\n")[0]
    return line[len("4ag: "):] if line.startswith("4ag: ") else None


def _wait_feature(task: dict) -> str | None:
    """The feature of an open `Merge PR #N` wait task, or None for any other task."""
    key = _key(task) or ""
    if not MERGE_PR_TITLE.match(task["content"]) or not key.endswith("/wait/merge-pr"):
        return None
    return key.split("/")[0]


def merge_prs(queue: Queue) -> list[int]:
    """The number of the PR of each open `Merge PR #N` wait task, in the order of the queue."""
    return [int(MERGE_PR_TITLE.match(task["content"]).group(1)) for task in queue.tasks if _wait_feature(task)]


def pr_state(text: str) -> str:
    """The state of a PR, MERGED, CLOSED, or OPEN, from the output of `gh pr view N --json state`."""
    return json.loads(text)["state"]


def _done_on_main(root: Path, key: str) -> bool:
    """Whether the ticket is `done` on the branch main of the repo at the root.

    The sweep reads main and not the checkout, because only a merge sets `done`. A root with no main holds no done
    ticket.
    """
    if not _on_main(root, key):
        return False
    text = subprocess.run(["git", "-C", str(root), "show", f"main:{key}"], capture_output=True, text=True,
                          env=_clean_git_env()).stdout
    return (_first(STATUS_LINE, text) or "").rstrip(".,;:") == "done"


def plan_sweep(root: Path, queue: Queue, states: dict[int, str]) -> list[list[str]]:
    """The `td` commands that close the tasks of each merged spec PR, given the state of the PR of each wait task.

    For a merged PR, the task of each ticket that is `done` on main completes, then the wait task. A ticket still open
    on main, such as a follow-up, keeps its task. A section is archived only after every task in it is complete,
    because an archive also archives the open tasks. A PR closed without a merge gives its wait task `blocked`. An open
    PR changes nothing. A feature that the root does not hold is skipped, so a sweep with a temp root never touches a
    real feature.
    """
    plan: list[list[str]] = []
    completed: set[str] = set()
    swept: list[str] = []

    def complete(task: dict) -> None:
        if task["id"] not in completed:
            completed.add(task["id"])
            plan.append(["task", "complete", f"id:{task['id']}"])

    for wait in queue.tasks:
        feature = _wait_feature(wait)
        if feature is None or not (root / ".scratch" / feature).is_dir():
            continue
        state = states.get(int(MERGE_PR_TITLE.match(wait["content"]).group(1)))
        if state == "MERGED":
            for task in queue.tasks:
                key = _key(task) or ""
                if key.startswith(f".scratch/{feature}/") and _done_on_main(root, key):
                    complete(task)
            complete(wait)
            if feature not in swept:
                swept.append(feature)
        elif state == "CLOSED":
            labels = [label for label in wait["labels"] if label not in OPEN_STATUSES] + ["blocked"]
            if set(labels) != set(wait["labels"]):
                plan.append(["task", "update", f"id:{wait['id']}", "--labels", ",".join(labels)])

    for feature in swept:
        section = queue.sections.get(feature)
        if section and all(task["id"] in completed for task in queue.tasks if task["sectionId"] == section):
            plan.append(["section", "archive", f"id:{section}"])
    return plan


def _feature_tickets(root: Path, feature: str) -> list[Path]:
    """The tickets and decision tickets of a feature, also those in the site/ and pipeline/ subfolders of a shared
    feature."""
    folder = root / ".scratch" / feature
    return sorted(path for path in folder.rglob("*.md") if _is_ticket(path.relative_to(root).as_posix()))


def plan_pull(root: Path, feature: str, queue: Queue, completed: dict,
              comments: Callable[[str], dict]) -> list[tuple[str, str]]:
    """The tickets of the feature whose Status line the queue changes, as (key, status) pairs.

    The queue owns the triage, so a triage label from Brian becomes the status of a ticket. A closed ticket keeps its
    status, because only the flow closes a ticket.
    """
    plan = []
    for path in _feature_tickets(root, feature):
        key = path.relative_to(root).as_posix()
        status = (_first(STATUS_LINE, path.read_text()) or "").rstrip(".,;:")
        if status in CLOSED_STATUSES:
            continue
        task = queue.task(key)
        if task is None:
            # An open task of the same ticket wins over a completed one, because Brian reopened it.
            done = task_of(completed["results"], key)
            if done is not None:
                plan.append((key, "done" if _says_done(comments(done["id"])) else "wontfix"))
            continue
        # A decision ticket has no triage status in its file, only open, done, or wontfix.
        if _is_decision(path):
            continue
        label = next((label for label in task["labels"] if label in TRIAGE_STATUSES), None)
        if label and label != status:
            plan.append((key, label))
    return plan


def _says_done(comments: dict) -> bool:
    """Whether a comment on a task holds the word done, as in "done in #34"."""
    return any(re.search(r"\bdone\b", comment.get("content") or "", re.IGNORECASE) for comment in comments["results"])


def write_statuses(root: Path, plan: list[tuple[str, str]], dry_run: bool) -> None:
    """Print each planned status, and write it into the Status line of its ticket unless this is a dry run.

    The new status replaces the whole line, because the text after the first word belongs to the old status.
    """
    for key, status in plan:
        path = root / key
        text = path.read_text()
        print(f"pull {key}: {(_first(STATUS_LINE, text) or 'none').rstrip('.,;:')} -> {status}")
        if not dry_run:
            path.write_text(re.sub(r"^\*\*Status:\*\*.*$", f"**Status:** {status}", text, count=1, flags=re.MULTILINE))
    print(f"{len(plan)} file{'' if len(plan) == 1 else 's'}{' planned, none written' if dry_run else ' written'}.")


IDEAS = "Ideas"
# The filter of the steps that wait on Brian. Its query reads the project and the label, not a description.
WAITS_FILTER = ("Waits on Brian", f"#{PROJECT} & @ready-for-human")
# A ticket or a decision ticket is a file such as `03-the-skill-sync.md`. A research ticket keeps its notes beside it
# in `03-the-skill-sync.notes.md`, which is not a ticket.
TICKET_FILE = re.compile(r"^\d+-[^.]+\.md$")


def spec_branches(root: Path) -> list[str]:
    """The local branches that hold a feature folder of their own name, `.scratch/<branch>/`, in name order.

    A root that is not the top of a git repo has no branch, such as a folder of fixtures inside the repo.
    """
    if not _is_repo_top(root):
        return []
    refs = _git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    return sorted(branch for branch in refs.stdout.split()
                  if _git(root, "cat-file", "-e", f"{branch}:.scratch/{branch}").returncode == 0)


def _is_ticket(key: str) -> bool:
    parts = key.split("/")
    return parts[-2] in ("issues", "decisions") and TICKET_FILE.match(parts[-1]) is not None


def _branch_tickets(root: Path, branch: str) -> list[str]:
    """The keys of the tickets and decision tickets of the feature on its spec branch."""
    files = _git(root, "ls-tree", "-r", "--name-only", branch, "--", f".scratch/{branch}/").stdout.split("\n")
    return sorted(key for key in files if key and _is_ticket(key))


def plan_import(root: Path, queue: Queue, filters: dict, prs: dict[str, list[dict]]) -> list[list[str]]:
    """The `td` commands that load the open work into the queue, given the PRs of each spec branch from `gh`.

    First come the labels of the flow, the Ideas section, and the filter, each only when it is missing. Then a push
    of each ticket and decision ticket, and a wait task for each open PR of a live spec. A live spec branch has no
    merged PR, and its feature reads from the branch. Each other feature reads from the checkout. A squash merge leaves
    the commits of the branch off main, so only `gh` tells a merged branch.
    """
    plan = [["label", "create", "--name", label] for label in FLOW_LABELS if label not in queue.labels]
    if IDEAS not in queue.sections:
        plan.append(_section_create(IDEAS, queue))
    name, query = WAITS_FILTER
    if not any(item["name"] == name for item in filters["results"]):
        plan.append(["filter", "create", "--name", name, "--query", query])
    # The pushes below see each label of the flow, because the first commands make the missing ones.
    pushes = Queue(queue.project_id, queue.sections, queue.tasks, queue.labels | set(FLOW_LABELS))

    live = [branch for branch in spec_branches(root)
            if branch in prs and not any(pr["state"] == "MERGED" for pr in prs[branch])]
    checkout = root / ".scratch"
    features = {path.name for path in checkout.iterdir() if path.is_dir()} if checkout.is_dir() else set()
    for feature in sorted(features | set(live)):
        if feature in live:
            read = branch_reader(root, feature)
            keys = _branch_tickets(root, feature)
        else:
            read = checkout_reader(root)
            keys = [path.relative_to(root).as_posix() for path in _feature_tickets(root, feature)]
        for key in keys:
            plan += plan_push(ticket_of(root, key, read(key), read), pushes)
        for pr in prs.get(feature, []) if feature in live else []:
            if pr["state"] == "OPEN":
                plan += plan_wait(feature, "merge-pr", pr["number"], False, pushes)

    # Each push plans the section of a new feature, so the second plan of the same section drops out.
    unique: list[list[str]] = []
    for command in plan:
        if command[:2] != ["section", "create"] or command not in unique:
            unique.append(command)
    return unique


class QueueError(Exception):
    """A failed `td` or `gh` call. Every failure of `td` exits 1, so the JSON error line on stderr names the cause."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code} {message}")
        self.code = code

    @classmethod
    def from_stderr(cls, stderr: str) -> "QueueError":
        for line in reversed(stderr.strip().splitlines()):
            try:
                error = json.loads(line)["error"]
                return cls(error.get("code", "ERROR"), error.get("message", ""))
            except (ValueError, KeyError, TypeError):
                continue
        return cls("ERROR", " ".join(stderr.split()) or "td failed with no message")


def _version(folder: Path) -> tuple[int, ...]:
    return tuple(int(n) for n in re.findall(r"\d+", folder.parent.name))


def td_bin_folder(home: Path, env: dict[str, str]) -> Path | None:
    """The bin folder of the newest nvm Node that holds `td`. QUEUE_TD_BIN overrides it.

    No shell PATH holds `td`, because nvm loads lazily, and the shebang of `td` needs `node` on the PATH.
    """
    if env.get("QUEUE_TD_BIN"):
        return Path(env["QUEUE_TD_BIN"])
    folders = [td.parent for td in (home / ".nvm/versions/node").glob("*/bin/td")]
    return max(folders, key=_version) if folders else None


def run_td(command: list[str]) -> dict:
    """Run one `td` command with JSON output and return the JSON. A failure raises QueueError."""
    env = dict(os.environ)
    folder = td_bin_folder(Path.home(), env)
    if folder:
        env["PATH"] = os.pathsep.join([str(folder), env.get("PATH", "")])
    td = str(folder / "td") if folder else "td"
    try:
        run = subprocess.run([td, *command, "--json"], capture_output=True, text=True, env=env, timeout=CALL_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise QueueError("TIMEOUT", f"td gave no answer in {CALL_TIMEOUT} seconds") from None
    except FileNotFoundError:
        raise QueueError("NO_TD", "td is not in an nvm Node and not on the PATH") from None
    if run.returncode != 0:
        raise QueueError.from_stderr(run.stderr)
    return json.loads(run.stdout) if run.stdout.strip() else {}


def read_queue() -> Queue:
    """Four reads of `td`: the project, its sections, its open tasks, and the labels."""
    projects = run_td(["project", "list", "--search", PROJECT])
    project = f"id:{project_id(projects)}"
    return Queue.from_data(
        projects,
        run_td(["section", "list", "--project", project]),
        run_td(["task", "list", "--project", project, "--all"]),
        run_td(["label", "list", "--all"]),
    )


# The folders where Homebrew puts `gh`. A run from a clean environment, such as `env -i`, has no PATH to find it.
GH_FOLDERS = ("/opt/homebrew/bin", "/usr/local/bin")


def run_gh(args: list[str], what: str) -> str:
    """Run one `gh` command and return its output. Each call names the repo, so it works from a temp root with no
    remote. A failure raises QueueError, so it warns like a failed `td` call."""
    gh = shutil.which("gh") or shutil.which("gh", path=os.pathsep.join(GH_FOLDERS)) or "gh"
    try:
        run = subprocess.run([gh, *args, "--repo", REPO], capture_output=True, text=True, timeout=CALL_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise QueueError("GH_TIMEOUT", f"gh gave no answer about {what} in {CALL_TIMEOUT} seconds") from None
    except FileNotFoundError:
        raise QueueError("NO_GH", "gh is not on the PATH") from None
    if run.returncode != 0:
        raise QueueError("GH_ERROR", " ".join(run.stderr.split()) or f"gh failed about {what} with no message")
    return run.stdout


def read_pr_state(number: int) -> str:
    """The state of one PR, from `gh`."""
    return pr_state(run_gh(["pr", "view", str(number), "--json", "state"], f"PR #{number}"))


def read_prs(branch: str) -> list[dict]:
    """The number and the state of each PR from the branch, from `gh`."""
    return json.loads(run_gh(["pr", "list", "--head", branch, "--state", "all", "--json", "number,state"],
                             f"the PRs of {branch}"))


def report_failure(subcommand: str, target: str, error: QueueError) -> int:
    """Print one warning line and return 0. A failed Todoist call never stops the work of a skill."""
    print(f"warning: the queue {subcommand} of {target} failed: {error}. The queue is behind the tracker.")
    return 0


def run_plan(plan: list[list[str]], dry_run: bool) -> None:
    """Print each planned command, and run it unless this is a dry run."""
    for command in plan:
        print("td " + shlex.join(command))
        if not dry_run:
            run_td(command)
    print(f"{len(plan)} command{'' if len(plan) == 1 else 's'}{' planned, none sent' if dry_run else ' sent'}.")


def _ticket_path(root: Path, given: str) -> Path:
    """The path of a ticket, given as an absolute path, a path from the root, or a path from the current folder."""
    path = Path(given)
    if path.is_absolute():
        return path
    return root / path if (root / path).is_file() else Path.cwd() / path


def push(args: argparse.Namespace) -> tuple[str, list[list[str]]]:
    ticket = load_ticket(args.root, _ticket_path(args.root, args.path))
    # A failed read below names the ticket by its key in the warning.
    args.target = ticket.key
    return ticket.key, plan_push(ticket, read_queue())


def wait(args: argparse.Namespace) -> tuple[str, list[list[str]]]:
    args.target = f"{args.feature}/wait/{args.kind}"
    return args.target, plan_wait(args.feature, args.kind, args.number, args.done, read_queue())


def sweep(args: argparse.Namespace) -> tuple[str, list[list[str]]]:
    # A failed read names what the sweep reads in the warning.
    args.target = "each open Merge PR task"
    queue = read_queue()
    return "sweep", plan_sweep(args.root, queue, {number: read_pr_state(number) for number in merge_prs(queue)})


def import_(args: argparse.Namespace) -> tuple[str, list[list[str]]]:
    args.target = "the open work"
    queue = read_queue()
    filters = run_td(["filter", "list"])
    return "import", plan_import(args.root, queue, filters,
                                 {branch: read_prs(branch) for branch in spec_branches(args.root)})


# The completed-task read of `td` covers at most 93 days per call.
COMPLETED_DAYS = 90


def pull(args: argparse.Namespace) -> tuple[str, list[tuple[str, str]]]:
    """Every read comes before the first write, so a failed read changes no file."""
    args.target = args.feature
    args.run = lambda plan, dry_run: write_statuses(args.root, plan, dry_run)
    queue_id = project_id(run_td(["project", "list", "--search", PROJECT]))
    project = f"id:{queue_id}"
    queue = Queue(queue_id, {}, run_td(["task", "list", "--project", project, "--all"])["results"], set())
    today = date.today()
    completed = run_td(["completed", "list", "--project", project, "--since",
                        (today - timedelta(days=COMPLETED_DAYS)).isoformat(), "--until",
                        (today + timedelta(days=1)).isoformat(), "--all"])
    return args.feature, plan_pull(args.root, args.feature, queue, completed,
                                   lambda task_id: run_td(["comment", "list", f"id:{task_id}", "--all"]))


def main(argv: list[str]) -> int:
    # Each subcommand shares --dry-run and --root, and returns its target and its plan.
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--dry-run", action="store_true", help="print the td commands and send nothing")
    shared.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="read the tracker under this folder in place of the repo root")
    parser = argparse.ArgumentParser(description="Make the Todoist queue match the tracker in .scratch/.")
    subcommands = parser.add_subparsers(dest="subcommand", required=True)
    push_parser = subcommands.add_parser("push", parents=[shared], help="make the task of one ticket match its file")
    push_parser.add_argument("path", help="the path of a ticket or a decision ticket")
    push_parser.set_defaults(plan=push)
    wait_parser = subcommands.add_parser("wait", parents=[shared], help="open or complete the wait task of one step")
    wait_parser.add_argument("feature", help="the feature slug, which names the section")
    wait_parser.add_argument("kind", choices=WAIT_TITLES, help="the step that waits on Brian")
    wait_parser.add_argument("number", nargs="?", type=int, help="the number of the PR, for merge-pr")
    wait_parser.add_argument("--done", action="store_true", help="complete the wait task")
    wait_parser.set_defaults(plan=wait)
    sweep_parser = subcommands.add_parser("sweep", parents=[shared], help="close the tasks of each merged spec PR")
    sweep_parser.set_defaults(plan=sweep)
    pull_parser = subcommands.add_parser("pull", parents=[shared],
                                         help="write the triage in the queue into the Status lines of a feature")
    pull_parser.add_argument("feature", help="the feature slug, the folder under .scratch/")
    pull_parser.set_defaults(plan=pull)
    import_parser = subcommands.add_parser("import", parents=[shared],
                                           help="load the open work, the labels, Ideas, and the filter into the queue")
    import_parser.set_defaults(plan=import_)
    args = parser.parse_args(argv)
    if args.subcommand == "wait" and args.kind == "merge-pr" and args.number is None and not args.done:
        wait_parser.error("merge-pr needs the number of the PR")

    try:
        _, plan = args.plan(args)
        # A subcommand that writes files in place of `td` commands sets its own runner.
        getattr(args, "run", run_plan)(plan, args.dry_run)
    except QueueError as error:
        return report_failure(args.subcommand, getattr(args, "target", args.subcommand), error)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
