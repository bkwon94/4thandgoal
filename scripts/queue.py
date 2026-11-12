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
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT = "4thandgoal"
GITHUB = "https://github.com/bkwon94/4thandgoal/blob/main"

# The statuses that Brian sets in the queue. A push writes one of them only when it makes the task.
TRIAGE_STATUSES = ("needs-triage", "needs-info", "ready-for-agent", "ready-for-human")
# The statuses that only the skills set. A push always writes them.
FLOW_STATUSES = ("in-progress", "in-review", "blocked")
OPEN_STATUSES = TRIAGE_STATUSES + FLOW_STATUSES
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
# A dead network can hang one `td` call for about 2 minutes, because the SDK retries. A push gives up sooner.
TD_TIMEOUT = 10


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


def _apps(root: Path, key: str) -> tuple[str, ...]:
    """The app of a ticket: the subfolder of a shared feature, else the App column of its row in state.md, else the
    Apps line of its PRD."""
    parts = key.split("/")
    if len(parts) > 3 and parts[2] in APPS:
        return (parts[2],)
    feature = parts[1]
    state = root / "docs/agents/state.md"
    if state.is_file():
        row = re.compile(rf"^\|\s*`?{re.escape(feature)}`?\s*\|\s*([^|]*)\|", re.MULTILINE)
        apps = _app_words(" ".join(row.findall(state.read_text())))
        if apps:
            return apps
    prd = root / ".scratch" / feature / "PRD.md"
    if prd.is_file():
        line = re.search(r"^Apps:([^.\n]*)", prd.read_text(), re.MULTILINE)
        if line:
            return _app_words(line.group(1))
    return ()


def _on_main(root: Path, key: str) -> bool:
    """Whether the file exists on the branch main of the repo at the root.

    A root that is not the top of a git repo has no main, such as a folder of fixtures inside the repo.
    """
    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=_clean_git_env())

    top = git("rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root.resolve():
        return False
    return git("cat-file", "-e", f"main:{key}").returncode == 0


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
    text = path.read_text()
    number, name = H1.search(text).groups()
    number = number or path.name.split("-")[0]
    decision = path.parent.name == "decisions"
    status = (_first(STATUS_LINE, text) or "").rstrip(".,;:")
    if decision and status == "open":
        status = DECISION_KINDS.get(_first(KIND_LINE, text), "needs-triage")
    # A ticket with no Status line is open. An odd word, which the tracker rule rejects, never becomes a label.
    if status not in OPEN_STATUSES + ("done", "wontfix"):
        status = "needs-triage"
    blocked = _first(BLOCKED_LINE, text)
    # "None (can start immediately)." and "none. Before this ticket, ..." both mean no blocker.
    if blocked and re.match(r"none\b", blocked, re.IGNORECASE):
        blocked = None
    feature = _feature(key)
    apps = _apps(root, key)
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
        line = f"4ag: {key}"
        return next((task for task in self.tasks if (task.get("description") or "").split("\n")[0] == line), None)


def project_id(projects: dict) -> str:
    """The id of the project 4thandgoal. The repo holds no Todoist id, so the script finds the project by its name."""
    for project in projects["results"]:
        if project["name"] == PROJECT:
            return project["id"]
    raise TdError("NO_PROJECT", f"Todoist has no project named {PROJECT}")


def plan_push(ticket: Ticket, queue: Queue) -> list[list[str]]:
    """The `td` commands that make the task of the ticket match its file. Each command omits the leading `td`.

    No command sets the priority or the order, because the queue owns them.
    """
    task = queue.task(ticket.key)
    closed = ticket.status in ("done", "wontfix")
    if task is None:
        # A closed ticket never enters the queue.
        return [] if closed else _plan_add(ticket, queue)

    labels = _labels(ticket, task["labels"])
    plan = [["label", "create", "--name", label] for label in labels
            if label in FLOW_LABELS and label not in queue.labels]
    update = []
    if task["content"] != ticket.title:
        update += ["--content", ticket.title]
    if task["description"] != ticket.description:
        update += ["--description", ticket.description]
    if set(labels) != set(task["labels"]):
        update += ["--labels", ",".join(labels)]
    if update:
        plan.append(["task", "update", f"id:{task['id']}", *update])
    section = queue.sections.get(ticket.feature)
    if section is None:
        plan.append(_section_create(ticket, queue))
        plan.append(["task", "move", f"id:{task['id']}", "--project", f"id:{queue.project_id}",
                     "--section", ticket.feature])
    elif task["sectionId"] != section:
        plan.append(["task", "move", f"id:{task['id']}", "--section", f"id:{section}"])
    # Only the merge sweep completes the task of a done ticket. A done decision ticket has no merge, so it completes
    # here.
    if ticket.status == "wontfix" or (ticket.status == "done" and ticket.decision):
        plan.append(["task", "complete", f"id:{task['id']}"])
    return plan


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


def _section_create(ticket: Ticket, queue: Queue) -> list[str]:
    return ["section", "create", "--name", ticket.feature, "--project", f"id:{queue.project_id}"]


def _plan_add(ticket: Ticket, queue: Queue) -> list[list[str]]:
    """Make the task. A command after a planned `section create` names the section, because its id is not known yet."""
    labels = _labels(ticket, [])
    plan = [["label", "create", "--name", label] for label in labels if label not in queue.labels]
    section = queue.sections.get(ticket.feature)
    if section is None:
        plan.append(_section_create(ticket, queue))
    plan.append(["task", "add", ticket.title, "--project", f"id:{queue.project_id}",
                 "--section", f"id:{section}" if section else ticket.feature,
                 "--labels", ",".join(labels), "--description", ticket.description])
    return plan


class TdError(Exception):
    """A failed `td` call. Every failure of `td` exits 1, so the JSON error line on stderr names the cause."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code} {message}")
        self.code = code

    @classmethod
    def from_stderr(cls, stderr: str) -> "TdError":
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
    """Run one `td` command with JSON output and return the JSON. A failure raises TdError."""
    env = dict(os.environ)
    folder = td_bin_folder(Path.home(), env)
    if folder:
        env["PATH"] = os.pathsep.join([str(folder), env.get("PATH", "")])
    td = str(folder / "td") if folder else "td"
    try:
        run = subprocess.run([td, *command, "--json"], capture_output=True, text=True, env=env, timeout=TD_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise TdError("TIMEOUT", f"td gave no answer in {TD_TIMEOUT} seconds") from None
    except FileNotFoundError:
        raise TdError("NO_TD", "td is not in an nvm Node and not on the PATH") from None
    if run.returncode != 0:
        raise TdError.from_stderr(run.stderr)
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


def report_failure(subcommand: str, target: str, error: TdError) -> int:
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
    args = parser.parse_args(argv)

    try:
        _, plan = args.plan(args)
        run_plan(plan, args.dry_run)
    except TdError as error:
        return report_failure(args.subcommand, getattr(args, "target", args.subcommand), error)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
