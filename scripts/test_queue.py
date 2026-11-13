"""
Tests the plan of each subcommand of scripts/queue.py with real ticket files and saved real `td` JSON.
The tickets sit in scripts/fixtures/queue/root/, and the `td` output sits in scripts/fixtures/queue/td/.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
# The script is queue.py, and the standard library has a module named queue. A load by path under its own name keeps
# the two apart.
_spec = importlib.util.spec_from_file_location("queue_script", HERE / "queue.py")
queue_script = importlib.util.module_from_spec(_spec)
sys.modules["queue_script"] = queue_script
_spec.loader.exec_module(queue_script)
Queue, load_ticket, plan_push = queue_script.Queue, queue_script.load_ticket, queue_script.plan_push

FIXTURES = HERE / "fixtures" / "queue"
ROOT = FIXTURES / "root"
TD = FIXTURES / "td"
ZZ = ".scratch/zz-queue-check"


def td_json(name: str) -> str:
    return (TD / name).read_text()


def queue(tasks: str = "tasks-empty.json", sections: str = "sections-empty.json",
          labels: str = "labels-empty.json") -> Queue:
    """The queue as four real reads of `td` show it."""
    return Queue.from_json(td_json("project-list.json"), td_json(sections), td_json(tasks), td_json(labels))


@contextlib.contextmanager
def environment(**values: str):
    """Set environment variables for the length of a block, then put back the old values."""
    old = {name: os.environ.get(name) for name in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for name, value in old.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def option(command: list[str], flag: str) -> str:
    """The value after a flag of one planned command."""
    return command[command.index(flag) + 1]


class APushOfANewTicket(unittest.TestCase):

    def test_a_new_ticket_makes_its_section_and_its_task(self):
        ticket = load_ticket(ROOT, ROOT / ZZ / "issues/01-zz-ready.md")
        self.assertEqual(plan_push(ticket, queue()), [
            ["label", "create", "--name", "ready-for-agent"],
            ["section", "create", "--name", "zz-queue-check", "--project", "id:6j222rQrr58wHx9G"],
            ["task", "add", "01 ZZ ready", "--project", "id:6j222rQrr58wHx9G", "--section", "zz-queue-check",
             "--labels", "ready-for-agent", "--description",
             "4ag: .scratch/zz-queue-check/issues/01-zz-ready.md\n"
             "On the spec branch zz-queue-check.\n"
             "A throwaway ticket for the acceptance tests of the queue. It names no real work."],
        ])

    def test_a_grill_decision_ticket_waits_on_brian(self):
        add = plan_push(load_ticket(ROOT, ROOT / ZZ / "decisions/01-grill-zz-question.md"), queue())[-1]
        self.assertEqual(add[2], "Decision 01: Does the grill ZZ question need Brian?")
        self.assertEqual(option(add, "--labels"), "ready-for-human,decision")

    def test_a_research_decision_ticket_waits_on_an_agent(self):
        add = plan_push(load_ticket(ROOT, ROOT / ZZ / "decisions/02-research-zz-question.md"), queue())[-1]
        self.assertEqual(add[2], "Decision 02: What does the research ZZ question find?")
        self.assertEqual(option(add, "--labels"), "ready-for-agent,decision")
        self.assertIn("Blocked by: 01", option(add, "--description"))
        self.assertIn("A throwaway research question", option(add, "--description"))


PUSHED = {"tasks": "tasks-zz.json", "sections": "sections-zz.json", "labels": "labels-flow.json"}
# Brian set 01 to ready-for-human, added his label phone, set p1, and dragged 02 out of its section.
TRIAGED = {**PUSHED, "tasks": "tasks-zz-triaged.json"}
TASK_01 = "id:6j2Gr4hP2xQ9c5Rw"
TASK_02 = "id:6j2Gr4j3Vv8fMRgx"
DECISION_01 = "id:6j2Gr4mFg7XCJqQ2"


class APushOfATicketWithATask(unittest.TestCase):
    """The queue holds the tasks that a push of the throwaway feature makes. Some tests change a file first."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "root"
        shutil.copytree(ROOT, self.root)

    def edit(self, path: str, old: str, new: str) -> Path:
        file = self.root / ZZ / path
        text = file.read_text()
        self.assertIn(old, text)
        file.write_text(text.replace(old, new))
        return file

    def push(self, path: str, state: dict) -> list[list[str]]:
        return plan_push(load_ticket(self.root, self.root / ZZ / path), queue(**state))

    def test_a_second_push_of_each_file_plans_zero_writes(self):
        for path in ("issues/01-zz-ready.md", "issues/02-zz-blocked.md", "decisions/01-grill-zz-question.md",
                     "decisions/02-research-zz-question.md"):
            with self.subTest(path):
                self.assertEqual(self.push(path, PUSHED), [])

    def test_the_triage_label_the_extra_label_and_the_priority_of_brian_stay(self):
        self.assertEqual(self.push("issues/01-zz-ready.md", TRIAGED), [])

    def test_a_flow_status_replaces_the_triage_label_and_keeps_the_extra_label(self):
        self.edit("issues/01-zz-ready.md", "**Status:** ready-for-agent", "**Status:** in-review")
        self.assertEqual(self.push("issues/01-zz-ready.md", TRIAGED),
                         [["task", "update", TASK_01, "--labels", "phone,in-review"]])

    def test_a_triage_status_in_the_file_replaces_an_old_flow_label(self):
        # The skills set the flow labels. A file back at a triage status means a skill moved the ticket on.
        self.edit("issues/02-zz-blocked.md", "**Status:** blocked", "**Status:** ready-for-agent")
        self.assertEqual(self.push("issues/02-zz-blocked.md", PUSHED),
                         [["task", "update", TASK_02, "--labels", "ready-for-agent"]])

    def test_a_task_out_of_its_section_moves_back(self):
        self.assertEqual(self.push("issues/02-zz-blocked.md", TRIAGED),
                         [["task", "move", TASK_02, "--section", "id:6j2Gq9xWJwFvVfMx"]])

    def test_a_new_summary_updates_the_description(self):
        self.edit("issues/02-zz-blocked.md", "It names no real work.", "It names no work.")
        plan = self.push("issues/02-zz-blocked.md", PUSHED)
        self.assertEqual([command[:3] for command in plan], [["task", "update", TASK_02]])
        self.assertTrue(option(plan[0], "--description").endswith("It names no work."))

    def test_a_new_comment_in_the_file_changes_nothing(self):
        file = self.root / ZZ / "issues/02-zz-blocked.md"
        file.write_text(file.read_text() + "\n## Comments\n\n- 2026-11-12: a new note on the ticket.\n")
        self.assertEqual(self.push("issues/02-zz-blocked.md", PUSHED), [])

    def test_a_done_decision_ticket_completes_its_task(self):
        self.edit("decisions/01-grill-zz-question.md", "**Status:** open", "**Status:** done")
        self.assertEqual(self.push("decisions/01-grill-zz-question.md", PUSHED), [
            ["task", "update", DECISION_01, "--labels", "decision"],
            ["task", "complete", DECISION_01],
        ])

    def test_a_done_ticket_never_completes_from_a_push(self):
        # Only the merge sweep completes the task of a done ticket.
        self.edit("issues/02-zz-blocked.md", "**Status:** blocked", "**Status:** done")
        self.assertEqual(self.push("issues/02-zz-blocked.md", PUSHED), [])

    def test_a_wontfix_ticket_completes_with_the_label_wontfix(self):
        self.edit("issues/01-zz-ready.md", "**Status:** ready-for-agent", "**Status:** wontfix")
        self.assertEqual(self.push("issues/01-zz-ready.md", TRIAGED), [
            ["task", "update", TASK_01, "--labels", "phone,wontfix"],
            ["task", "complete", TASK_01],
        ])

    def test_a_closed_ticket_with_no_task_plans_nothing(self):
        self.assertEqual(plan_push(load_ticket(ROOT, ROOT / ZZ / "issues/03-zz-done.md"), queue()), [])

    def test_a_new_ticket_goes_into_the_section_that_exists(self):
        file = self.root / ZZ / "issues/04-zz-new.md"
        file.write_text((self.root / ZZ / "issues/01-zz-ready.md").read_text().replace("01: ZZ ready", "04: ZZ new"))
        self.assertEqual([command[:3] for command in self.push("issues/04-zz-new.md", PUSHED)],
                         [["task", "add", "04 ZZ new"]])
        self.assertEqual(option(self.push("issues/04-zz-new.md", PUSHED)[0], "--section"), "id:6j2Gq9xWJwFvVfMx")

    def test_an_odd_status_gives_needs_triage_and_makes_no_odd_label(self):
        file = self.edit("issues/01-zz-ready.md", "**Status:** ready-for-agent", "**Status:** backlog")
        file.rename(file.with_name("05-zz-odd.md"))
        add = self.push("issues/05-zz-odd.md", PUSHED)[-1]
        self.assertEqual(option(add, "--labels"), "needs-triage")

    def test_no_push_sets_the_priority(self):
        for state in (PUSHED, TRIAGED, {}):
            for path in ("issues/01-zz-ready.md", "issues/02-zz-blocked.md"):
                for command in self.push(path, state):
                    self.assertNotIn("--priority", command)
                    self.assertNotIn("--order", command)


class APullOfTheTriageOfBrian(unittest.TestCase):
    """The plan of a pull: each ticket of the feature whose Status line the queue changes, and its status."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "root"
        shutil.copytree(ROOT, self.root)
        self.ticket = self.root / ZZ / "issues/01-zz-ready.md"

    def status_line(self, line: str) -> None:
        text = self.ticket.read_text()
        self.ticket.write_text(text.replace("**Status:** ready-for-agent", line))

    def pull(self, tasks: str, completed: str = "completed-empty.json", comments: str = "comments-none.json"):
        return queue_script.plan_pull(self.root, "zz-queue-check", queue(tasks=tasks), json.loads(td_json(completed)),
                                      lambda task_id: json.loads(td_json(comments)))

    def write(self, plan: list[tuple[str, str]], dry_run: bool = False) -> list[str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            queue_script.write_statuses(self.root, plan, dry_run)
        return out.getvalue().splitlines()

    def test_a_triage_label_from_brian_becomes_the_status(self):
        self.assertEqual(self.pull("tasks-zz-triaged.json"), [(f"{ZZ}/issues/01-zz-ready.md", "ready-for-human")])

    def test_a_task_that_brian_completed_pulls_as_wontfix(self):
        self.assertEqual(self.pull("tasks-empty.json", "completed-zz-01.json"),
                         [(f"{ZZ}/issues/01-zz-ready.md", "wontfix")])

    def test_a_completed_task_with_a_done_comment_pulls_as_done(self):
        self.assertEqual(self.pull("tasks-empty.json", "completed-zz-01.json", "comments-done.json"),
                         [(f"{ZZ}/issues/01-zz-ready.md", "done")])

    def test_an_open_task_wins_over_an_old_completion_of_the_same_ticket(self):
        self.assertEqual(self.pull("tasks-zz-triaged.json", "completed-zz-01.json"),
                         [(f"{ZZ}/issues/01-zz-ready.md", "ready-for-human")])

    def test_a_closed_ticket_keeps_its_status(self):
        # A done ticket keeps its status label until the merge sweep, and only the flow reopens a closed ticket.
        for line in ("**Status:** done", "**Status:** wontfix", "**Status:** Done.", "Status: done"):
            with self.subTest(line):
                self.status_line(line)
                self.assertEqual(self.pull("tasks-zz-triaged.json"), [])
                self.assertEqual(self.pull("tasks-empty.json", "completed-zz-01.json"), [])
                self.ticket.write_text(self.ticket.read_text().replace(line, "**Status:** ready-for-agent"))

    def test_a_plain_status_line_and_a_capital_first_word_read_like_the_tracker_rules(self):
        for line, status in (("Status: Done", "done"), ("Status: in-review;", "in-review"),
                             ("**Status:** Ready-for-human,", "ready-for-human")):
            with self.subTest(line):
                self.ticket.write_text(self.ticket.read_text().replace("**Status:** ready-for-agent", line))
                self.assertEqual(load_ticket(self.root, self.ticket).status, status)
                self.ticket.write_text(self.ticket.read_text().replace(line, "**Status:** ready-for-agent"))

    def test_a_write_replaces_a_plain_status_line(self):
        self.status_line("Status: ready-for-agent")
        self.write([(f"{ZZ}/issues/01-zz-ready.md", "needs-info")])
        self.assertIn("**Status:** needs-info\n", self.ticket.read_text())
        self.assertNotIn("Status: ready-for-agent", self.ticket.read_text())

    def test_a_same_first_word_changes_nothing_and_keeps_the_text_after_it(self):
        self.status_line("**Status:** ready-for-human, since Brian asked on 2026-11-12")
        self.assertEqual(self.pull("tasks-zz-triaged.json"), [])

    def test_a_flow_label_and_a_decision_ticket_change_nothing(self):
        # 02 is blocked in the file and in the queue. Brian set both decision tasks to a triage label.
        plan = self.pull("tasks-zz-triaged.json")
        self.assertNotIn("02-zz-blocked.md", str(plan))
        self.assertNotIn("decisions", str(plan))

    def test_a_write_replaces_the_first_word_and_drops_the_text_after_it(self):
        self.status_line("**Status:** ready-for-agent (after the audit)")
        lines = self.write([(f"{ZZ}/issues/01-zz-ready.md", "needs-info")])
        self.assertIn("**Status:** needs-info\n", self.ticket.read_text())
        self.assertNotIn("after the audit", self.ticket.read_text())
        self.assertEqual(lines, [f"pull {ZZ}/issues/01-zz-ready.md: ready-for-agent -> needs-info", "1 file written."])

    def test_a_dry_run_writes_no_file(self):
        before = self.ticket.read_text()
        lines = self.write([(f"{ZZ}/issues/01-zz-ready.md", "needs-info")], dry_run=True)
        self.assertEqual(self.ticket.read_text(), before)
        self.assertEqual(lines[-1], "1 file planned, none written.")

    def test_a_failed_read_changes_no_file_and_warns_with_exit_0(self):
        before = self.ticket.read_text()
        out = io.StringIO()
        with environment(QUEUE_TD_BIN=str(self.root / "no-td")), contextlib.redirect_stdout(out):
            code = queue_script.main(["pull", "zz-queue-check", "--root", str(self.root)])
        self.assertEqual(code, 0)
        self.assertEqual(self.ticket.read_text(), before)
        self.assertEqual(len(out.getvalue().splitlines()), 1)
        self.assertTrue(out.getvalue().startswith("warning: the queue pull of zz-queue-check failed: NO_TD"))


class TheAppLabel(unittest.TestCase):

    def test_a_shared_feature_takes_the_app_of_its_subfolder(self):
        path = ".scratch/manager-pages/site/issues/11-the-bench-sentence-and-the-odds-change-words.md"
        ticket = load_ticket(ROOT, ROOT / path)
        add = plan_push(ticket, queue())[-1]
        self.assertEqual(option(add, "--section"), "manager-pages")
        self.assertEqual(option(add, "--labels"), "ready-for-human,site")
        self.assertIn("\nApp: site\n", option(add, "--description"))

    def test_both_in_the_state_row_gives_site_and_pipeline(self):
        ticket = load_ticket(ROOT, ROOT / ".scratch/todoist-queue/issues/03-push-makes-one-task-match-one-ticket.md")
        add = plan_push(ticket, queue())[-1]
        self.assertEqual(option(add, "--labels"), "ready-for-agent,site,pipeline")
        self.assertIn("\nApp: site, pipeline\n", option(add, "--description"))

    def test_a_feature_with_no_state_row_reads_the_apps_line_of_its_prd(self):
        ticket = load_ticket(ROOT, ROOT / ".scratch/front-door/issues/01-the-front-door-shell.md")
        self.assertIn("\nApp: site, pipeline, api\n", ticket.description)

    def test_a_feature_with_no_row_and_no_prd_gets_no_app(self):
        add = plan_push(load_ticket(ROOT, ROOT / ZZ / "issues/01-zz-ready.md"), queue())[-1]
        self.assertNotIn("App:", option(add, "--description"))


class TheLink(unittest.TestCase):

    def test_a_ticket_on_main_links_to_github(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            shutil.copytree(ROOT, root)
            for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t",
                                                                          "commit", "-q", "-m", "fixture"]):
                subprocess.run(["git", "-C", str(root), *args], check=True, env=queue_script._clean_git_env())
            ticket = load_ticket(root, root / ZZ / "issues/01-zz-ready.md")
        self.assertEqual(ticket.description.splitlines()[1], "https://github.com/bkwon94/4thandgoal/blob/main/"
                                                             ".scratch/zz-queue-check/issues/01-zz-ready.md")

    def test_a_ticket_off_main_names_its_spec_branch(self):
        ticket = load_ticket(ROOT, ROOT / ".scratch/todoist-queue/issues/03-push-makes-one-task-match-one-ticket.md")
        lines = ticket.description.splitlines()
        self.assertEqual(lines[:3], ["4ag: .scratch/todoist-queue/issues/03-push-makes-one-task-match-one-ticket.md",
                                     "App: site, pipeline", "On the spec branch todoist-queue."])
        self.assertNotIn("github.com", ticket.description)
        self.assertTrue(lines[3].startswith("An agent runs one command"))


class TheTdCall(unittest.TestCase):

    def test_the_newest_nvm_node_that_holds_td_wins(self):
        with tempfile.TemporaryDirectory() as home:
            for version, has_td in (("v9.11.2", True), ("v24.15.0", True), ("v25.1.0", False)):
                folder = Path(home) / ".nvm/versions/node" / version / "bin"
                folder.mkdir(parents=True)
                if has_td:
                    (folder / "td").write_text("")
            self.assertEqual(queue_script.td_bin_folder(Path(home), {}),
                             Path(home) / ".nvm/versions/node/v24.15.0/bin")

    def test_an_environment_variable_overrides_the_folder(self):
        self.assertEqual(queue_script.td_bin_folder(Path("/nowhere"), {"QUEUE_TD_BIN": "/opt/td/bin"}),
                         Path("/opt/td/bin"))

    def test_a_failed_call_names_its_error_code(self):
        error = queue_script.QueueError.from_stderr(td_json("error-auth.stderr"))
        self.assertEqual(str(error), "AUTH_ERROR HTTP 401: Unauthorized")

    def test_a_failed_push_warns_in_one_line_and_exits_0(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = queue_script.report_failure("push", ".scratch/zz-queue-check/issues/02-zz-blocked.md",
                                               queue_script.QueueError.from_stderr(td_json("error-auth.stderr")))
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().splitlines(), [
            "warning: the queue push of .scratch/zz-queue-check/issues/02-zz-blocked.md failed: AUTH_ERROR HTTP 401: "
            "Unauthorized. The queue is behind the tracker.",
        ])


WAITS = {"tasks": "tasks-zz-waits.json", "sections": "sections-zz.json", "labels": "labels-flow.json"}
PROJECT = "id:6j222rQrr58wHx9G"
SECTION_ZZ = "id:6j2Gq9xWJwFvVfMx"


class AWait(unittest.TestCase):

    def test_a_wait_makes_its_section_its_label_and_its_task(self):
        self.assertEqual(queue_script.plan_wait("zz-queue-check", "approve-prd", None, False, queue()), [
            ["label", "create", "--name", "ready-for-human"],
            ["section", "create", "--name", "zz-queue-check", "--project", PROJECT],
            ["task", "add", "Approve PRD", "--project", PROJECT, "--section", "zz-queue-check",
             "--labels", "ready-for-human", "--description", "4ag: zz-queue-check/wait/approve-prd"],
        ])

    def test_a_merge_pr_wait_goes_into_the_section_that_exists_and_links_to_the_pr(self):
        self.assertEqual(queue_script.plan_wait("zz-queue-check", "merge-pr", 34, False, queue(**PUSHED)), [
            ["task", "add", "Merge PR #34", "--project", PROJECT, "--section", SECTION_ZZ,
             "--labels", "ready-for-human", "--description",
             "4ag: zz-queue-check/wait/merge-pr\nhttps://github.com/bkwon94/4thandgoal/pull/34"],
        ])

    def test_each_kind_has_its_title(self):
        for kind, title in (("approve-acceptance", "Approve ACCEPTANCE"), ("approve-tickets", "Approve tickets")):
            with self.subTest(kind):
                self.assertEqual(queue_script.plan_wait("zz-queue-check", kind, None, False, queue(**PUSHED))[-1][2],
                                 title)

    def test_a_second_wait_plans_nothing(self):
        self.assertEqual(queue_script.plan_wait("zz-queue-check", "merge-pr", 34, False, queue(**WAITS)), [])

    def test_a_wait_on_a_second_pr_makes_a_second_task(self):
        plan = queue_script.plan_wait("zz-queue-check", "merge-pr", 35, False, queue(**WAITS))
        self.assertEqual([command[:3] for command in plan], [["task", "add", "Merge PR #35"]])

    def test_done_completes_the_wait_task(self):
        self.assertEqual(queue_script.plan_wait("zz-queue-check", "merge-pr", 16, True, queue(**WAITS)),
                         [["task", "complete", "id:6j2Gr5Fq2VxW8gPc"]])

    def test_done_with_no_wait_task_plans_nothing(self):
        self.assertEqual(queue_script.plan_wait("zz-queue-check", "approve-prd", None, True, queue(**WAITS)), [])


def gh_state(name: str) -> str:
    """The state of a PR from saved real output of `gh pr view N --json state`."""
    return queue_script.pr_state((FIXTURES / "gh" / name).read_text())


MERGED, CLOSED, OPEN = gh_state("pr-34-merged.json"), gh_state("pr-16-closed.json"), gh_state("pr-open.json")
TASK_03 = "id:6j2Gr4hVq8Xm3Pcf"
DECISION_02 = "id:6j2Gr4pW5gqH9fc7"
WAIT_34 = "id:6j2Gr5Cw7RfJ4hQm"
WAIT_16 = "id:6j2Gr5Fq2VxW8gPc"


class TheMergeSweep(unittest.TestCase):
    """The root is a git repo whose branch main holds the throwaway feature, because the sweep reads main."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "repo"
        shutil.copytree(ROOT, self.root)

    def set_status(self, path: str, old: str, new: str) -> None:
        file = self.root / ZZ / path
        text = file.read_text()
        self.assertIn(f"**Status:** {old}", text)
        file.write_text(text.replace(f"**Status:** {old}", f"**Status:** {new}"))

    def commit_main(self) -> None:
        for args in (["init", "-q", "-b", "main"], ["add", "-A"],
                     ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "fixture"]):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, env=queue_script._clean_git_env())

    def sweep(self, states: dict[int, str]) -> list[list[str]]:
        return queue_script.plan_sweep(self.root, queue(**WAITS), states)

    def test_the_saved_gh_output_reads_as_each_state(self):
        self.assertEqual((MERGED, CLOSED, OPEN), ("MERGED", "CLOSED", "OPEN"))

    def test_the_sweep_reads_each_open_merge_pr_task(self):
        self.assertEqual(queue_script.merge_prs(queue(**WAITS)), [34, 16, 13])

    def test_a_merged_pr_completes_its_done_tickets_then_its_wait_task_and_a_closed_pr_gives_blocked(self):
        self.commit_main()
        self.assertEqual(self.sweep({34: MERGED, 16: CLOSED, 13: MERGED}), [
            ["task", "complete", TASK_03],
            ["task", "complete", WAIT_34],
            ["task", "update", WAIT_16, "--labels", "phone,blocked"],
        ])

    def test_an_open_pr_changes_nothing(self):
        self.commit_main()
        self.assertEqual(self.sweep({34: OPEN, 16: OPEN, 13: OPEN}), [])

    def test_a_ticket_done_only_off_main_keeps_its_task(self):
        self.commit_main()
        self.set_status("issues/02-zz-blocked.md", "blocked", "done")
        self.assertNotIn(["task", "complete", TASK_02], self.sweep({34: MERGED, 16: OPEN, 13: OPEN}))

    def test_the_section_is_archived_after_every_task_in_it_is_complete(self):
        self.set_status("issues/01-zz-ready.md", "ready-for-agent", "done")
        self.set_status("issues/02-zz-blocked.md", "blocked", "done")
        self.set_status("decisions/01-grill-zz-question.md", "open", "done")
        self.set_status("decisions/02-research-zz-question.md", "open", "done")
        self.commit_main()
        self.assertEqual(self.sweep({34: MERGED, 16: MERGED, 13: OPEN}), [
            ["task", "complete", TASK_01],
            ["task", "complete", TASK_02],
            ["task", "complete", TASK_03],
            ["task", "complete", DECISION_01],
            ["task", "complete", DECISION_02],
            ["task", "complete", WAIT_34],
            ["task", "complete", WAIT_16],
            ["section", "archive", SECTION_ZZ],
        ])

    def test_a_closed_pr_already_blocked_plans_nothing(self):
        self.commit_main()
        blocked = queue(**WAITS)
        next(task for task in blocked.tasks if task["content"] == "Merge PR #16")["labels"] = ["blocked", "phone"]
        self.assertEqual(queue_script.plan_sweep(self.root, blocked, {34: OPEN, 16: CLOSED, 13: OPEN}), [])

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True, env=queue_script._clean_git_env())

    def commit(self) -> None:
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "next")

    def test_the_sweep_reads_origin_main_when_it_exists(self):
        # Brian merged on GitHub: origin/main has 01 done, and the local main is one commit behind.
        self.commit_main()
        self.set_status("issues/01-zz-ready.md", "ready-for-agent", "done")
        self.commit()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("reset", "-q", "--hard", "HEAD~1")
        self.assertIn(["task", "complete", TASK_01], self.sweep({34: MERGED, 16: OPEN, 13: OPEN}))

    def test_the_sweep_reads_the_local_main_with_no_origin_main(self):
        self.commit_main()
        self.set_status("issues/01-zz-ready.md", "ready-for-agent", "done")
        self.commit()
        self.assertIn(["task", "complete", TASK_01], self.sweep({34: MERGED, 16: OPEN, 13: OPEN}))
        # An origin/main that is behind wins over the local main, so 01 keeps its task.
        self.git("update-ref", "refs/remotes/origin/main", "HEAD~1")
        self.assertNotIn(["task", "complete", TASK_01], self.sweep({34: MERGED, 16: OPEN, 13: OPEN}))

    def test_a_root_with_no_main_completes_no_ticket(self):
        self.assertEqual(self.sweep({34: MERGED, 16: OPEN, 13: OPEN}), [["task", "complete", WAIT_34]])


BRANCH = FIXTURES / "branch"


def gh_prs(name: str) -> list[dict]:
    """The PRs of one branch from saved real output of `gh pr list --head <branch> --state all --json number,state`."""
    return json.loads((FIXTURES / "gh" / name).read_text())


class TheImport(unittest.TestCase):
    """The root is a git repo. Its branch main holds the fixture tickets. The branch codex-flow adds a feature that
    only it holds, and it has no PR. The branch midseason-report adds an open ticket, and its PR merged as #13."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "repo"
        shutil.copytree(ROOT, self.root)
        self.git("init", "-q", "-b", "main")
        self.commit("fixture")
        for feature in ("codex-flow", "midseason-report"):
            self.git("checkout", "-q", "-b", feature)
            shutil.copytree(BRANCH / ".scratch" / feature, self.root / ".scratch" / feature)
            self.commit(feature)
            self.git("checkout", "-q", "main")
        self.prs = {"codex-flow": gh_prs("list-codex-flow.json"), "midseason-report": gh_prs("list-midseason-report.json")}

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True, env=queue_script._clean_git_env())

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", message)

    def plan(self, state: dict | None = None, filters: str = "filters-default.json") -> list[list[str]]:
        return queue_script.plan_import(self.root, queue(**(state or {})), json.loads(td_json(filters)), self.prs)

    def adds(self, plan: list[list[str]]) -> dict[str, list[str]]:
        return {command[2]: command for command in plan if command[:2] == ["task", "add"]}

    def test_the_spec_branches_are_the_local_branches_with_a_feature_folder(self):
        self.assertEqual(queue_script.spec_branches(self.root), ["codex-flow", "midseason-report"])

    def test_a_ticket_on_a_live_spec_branch_reads_from_that_branch_with_no_link(self):
        add = self.adds(self.plan())["01 The rules move to AGENTS.md"]
        self.assertEqual(option(add, "--section"), "codex-flow")
        self.assertEqual(option(add, "--labels"), "in-review,site,pipeline")
        description = option(add, "--description")
        self.assertEqual(description.splitlines()[:4], [
            "4ag: .scratch/codex-flow/issues/01-the-rules-move-to-agents-md.md", "App: site, pipeline",
            "On the spec branch codex-flow.", description.splitlines()[3]])
        self.assertTrue(description.splitlines()[3].startswith("The repo rules live in `AGENTS.md`"))
        self.assertNotIn("github.com", description)

    def test_a_spec_branch_with_a_merged_pr_is_skipped(self):
        self.assertFalse([command for command in self.plan() if "midseason-report" in words(command)])

    def test_an_empty_queue_first_gets_the_labels_the_ideas_section_and_the_filter(self):
        plan = self.plan()
        self.assertEqual(plan[:15], [["label", "create", "--name", label] for label in (
            "needs-triage", "needs-info", "ready-for-agent", "ready-for-human", "in-progress", "in-review", "blocked",
            "wontfix", "decision", "site", "pipeline", "api")] + [
            ["section", "create", "--name", "Ideas", "--project", PROJECT],
            ["filter", "create", "--name", "Waits on Brian", "--query", "#4thandgoal & @ready-for-human"],
            ["section", "create", "--name", "codex-flow", "--project", PROJECT],
        ])
        self.assertEqual([command for command in plan[15:] if command[0] == "label"], [])

    def test_each_open_ticket_and_open_decision_ticket_enters_and_no_done_ticket(self):
        self.assertEqual(sorted(self.adds(self.plan())), [
            "01 The rules move to AGENTS.md",
            "01 ZZ ready", "02 ZZ blocked", "03 Push makes one task match one ticket",
            "09 The home page test reads a class name", "11 The bench sentence and the odds change words",
            "Decision 01: Does the grill ZZ question need Brian?",
            "Decision 02: What does the research ZZ question find?",
        ])

    def test_a_research_note_is_not_a_ticket(self):
        notes = ".scratch/todoist-queue/decisions/02-research-td-facts.notes.md"
        self.assertTrue((self.root / notes).is_file())
        self.assertNotIn(notes, words(sum(self.plan(), [])))

    def test_each_section_is_made_once(self):
        sections = [command[3] for command in self.plan() if command[:2] == ["section", "create"]]
        self.assertEqual(sections, ["Ideas", "codex-flow", "manager-pages", "site-pages", "todoist-queue",
                                    "zz-queue-check"])

    def test_an_open_pr_of_a_live_spec_makes_its_merge_wait(self):
        # No PR is open on 2026-11-12, so the open state comes from the saved `gh pr view` output of an open PR.
        self.prs["codex-flow"] = [{"number": 36, "state": OPEN}]
        self.assertEqual(self.adds(self.plan())["Merge PR #36"][-1],
                         "4ag: codex-flow/wait/merge-pr\nhttps://github.com/bkwon94/4thandgoal/pull/36")

    def test_a_link_that_todoist_turned_into_a_titled_link_plans_no_update(self):
        # Todoist stores a bare URL in a description as a markdown link with the title of the page.
        imported = queue(tasks="tasks-imported.json", sections="sections-imported.json", labels="labels-imported.json")
        ticket = load_ticket(self.root, self.root / ".scratch/site-pages/issues/09-home-test-class-name.md")
        self.assertIn("](https://github.com/", queue_script.task_of(imported.tasks, ticket.key)["description"])
        self.assertEqual(plan_push(ticket, imported), [])

    def test_a_second_import_plans_zero_writes(self):
        root = Path(self.root.parent) / "zz-only"
        root.mkdir()
        shutil.copytree(ROOT / ZZ, root / ZZ)
        imported = queue(**PUSHED)
        imported.sections.update(queue(sections="sections-imported.json").sections)
        self.assertEqual(queue_script.plan_import(root, imported, json.loads(td_json("filters-imported.json")), {}),
                         [])

    def test_a_folder_inside_the_repo_has_no_spec_branch(self):
        self.assertEqual(queue_script.spec_branches(ROOT), [])


def words(command: list[str]) -> str:
    """The words of a planned command in one line, for a search."""
    return " ".join(command)


class AQuickFile(unittest.TestCase):
    """A quick file is .scratch/bugs/<slug>.md or .scratch/quick-wins/<slug>.md. Its section name comes from a map."""

    BUGS_SECTION = "6j2Gq9xBugsSect01"
    TASK = {"id": "6j2Gr9QuickTask01", "content": "01 Fix the draw", "labels": [], "sectionId": BUGS_SECTION,
            "description": "4ag: .scratch/bugs/fix-the-draw.md\nOn the spec branch.\n"}
    WAIT = {"id": "6j2Gr9QuickWait01", "content": "Merge PR #50", "labels": ["ready-for-human"],
            "sectionId": BUGS_SECTION, "description": "4ag: bugs/wait/merge-pr\nhttps://example.com/pull/50"}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "repo"
        self.root.mkdir()

    def quick_file(self, folder: str, slug: str, status: str = "in-progress") -> Path:
        file = self.root / ".scratch" / folder / f"{slug}.md"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(f"# Fix the {slug}\n\nKind: bug\nStatus: {status}\nBranch: `bug-{slug}`.\n")
        return file

    def commit_main(self) -> None:
        for args in (["init", "-q", "-b", "main"], ["add", "-A"],
                     ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "fixture"]):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, env=queue_script._clean_git_env())

    def push(self, folder: str, slug: str, queue_: Queue) -> list[list[str]]:
        file = self.quick_file(folder, slug)
        return plan_push(load_ticket(self.root, file), queue_)

    def test_a_bugs_file_goes_into_the_section_bugs_and_makes_no_section_bugs(self):
        labels = queue().labels | set(queue_script.FLOW_LABELS)
        existing = Queue("p1", {"Bugs": self.BUGS_SECTION}, [], labels)
        add = self.push("bugs", "fix-the-draw", existing)[-1]
        self.assertEqual(option(add, "--section"), f"id:{self.BUGS_SECTION}")
        self.assertNotIn(["section", "create"], [command[:2] for command in self.push("bugs", "fix-the-draw", existing)])

    def test_a_bugs_file_makes_the_section_with_its_mapped_name(self):
        plan = self.push("bugs", "fix-the-draw", queue())
        self.assertIn(["section", "create", "--name", "Bugs", "--project", "id:6j222rQrr58wHx9G"], plan)
        self.assertEqual(option(plan[-1], "--section"), "Bugs")

    def test_two_quick_wins_files_make_the_section_quick_wins_once(self):
        first = self.push("quick-wins", "one", queue())
        second = self.push("quick-wins", "two", queue())
        # The first push makes the section. The queue read after it holds the section, so the second push does not.
        made = Queue("p1", {"Quick Wins": "6j2Gq9xQuickWins1"}, [], queue().labels | set(queue_script.FLOW_LABELS))
        third = self.push("quick-wins", "two", made)
        self.assertEqual(sum(command[:2] == ["section", "create"] for command in first), 1)
        self.assertEqual(sum(command[:2] == ["section", "create"] for command in second), 1)
        self.assertEqual(sum(command[:2] == ["section", "create"] for command in third), 0)
        self.assertEqual(option(first[-1], "--section"), "Quick Wins")
        self.assertEqual(option(third[-1], "--section"), "id:6j2Gq9xQuickWins1")

    def test_a_moved_quick_task_goes_to_its_mapped_section(self):
        file = self.quick_file("quick-wins", "move-me")
        task = {**self.TASK, "content": "Fix the move-me", "sectionId": "other",
                "description": "4ag: .scratch/quick-wins/move-me.md"}
        plan = plan_push(load_ticket(self.root, file), Queue("p1", {}, [task], queue().labels))
        self.assertIn(["task", "move", f"id:{task['id']}", "--project", "id:p1", "--section", "Quick Wins"], plan)

    def test_a_quick_file_has_no_number_and_its_title_is_its_h1_alone(self):
        ticket = load_ticket(self.root, self.quick_file("bugs", "pick-owner"))
        self.assertEqual(ticket.title, "Fix the pick-owner")

    def test_a_sweep_completes_the_done_quick_task_and_its_wait_task_and_never_archives_bugs(self):
        self.quick_file("bugs", "fix-the-draw", status="done")
        self.commit_main()
        both = Queue("p1", {"Bugs": self.BUGS_SECTION}, [self.TASK, self.WAIT], set())
        self.assertEqual(queue_script.plan_sweep(self.root, both, {50: "MERGED"}), [
            ["task", "complete", f"id:{self.TASK['id']}"],
            ["task", "complete", f"id:{self.WAIT['id']}"],
        ])

    def test_a_sweep_never_archives_quick_wins(self):
        self.quick_file("quick-wins", "one", status="done")
        self.commit_main()
        task = {**self.TASK, "sectionId": "qw", "description": "4ag: .scratch/quick-wins/one.md"}
        wait = {**self.WAIT, "sectionId": "qw", "description": "4ag: quick-wins/wait/merge-pr"}
        plan = queue_script.plan_sweep(self.root, Queue("p1", {"Quick Wins": "qw"}, [task, wait], set()),
                                       {50: "MERGED"})
        self.assertEqual(plan, [["task", "complete", f"id:{task['id']}"], ["task", "complete", f"id:{wait['id']}"]])


class ATake(unittest.TestCase):
    """`take` claims the open task of a name in Bugs or Quick Wins by putting the key line first in its description."""

    NAME = "Pick owner: week_moves names the first owner of a traded pick"
    PATH = ".scratch/bugs/pick-owner.md"
    TASK = {"id": "6j2Gr9TakeTask01", "content": NAME, "labels": ["bug"], "sectionId": "bugs-id",
            "description": "It shows the first owner.\nSee week 8."}
    SECTIONS = {"Bugs": "bugs-id", "Quick Wins": "qw-id", "Ideas": "ideas-id"}

    def take(self, name: str, tasks: list[dict]):
        return queue_script.plan_take(name, self.PATH, Queue("p1", self.SECTIONS, tasks, set()))

    def test_a_take_plans_one_update_with_the_key_line_first_and_the_old_description_kept(self):
        task, plan = self.take(self.NAME, [self.TASK])
        self.assertEqual(task, self.TASK)
        self.assertEqual(plan, [["task", "update", "id:6j2Gr9TakeTask01", "--description",
                                 f"4ag: {self.PATH}\nIt shows the first owner.\nSee week 8."]])

    def test_a_take_of_a_task_with_no_description_writes_the_key_line_alone(self):
        _, plan = self.take(self.NAME, [{**self.TASK, "description": ""}])
        self.assertEqual(option(plan[0], "--description"), f"4ag: {self.PATH}")

    def test_a_take_in_quick_wins_finds_its_task(self):
        _, plan = self.take(self.NAME, [{**self.TASK, "sectionId": "qw-id"}])
        self.assertEqual(len(plan), 1)

    def test_a_take_of_a_task_outside_the_two_sections_plans_nothing(self):
        self.assertEqual(self.take(self.NAME, [{**self.TASK, "sectionId": "ideas-id"}]), (None, []))

    def test_a_take_of_an_unknown_name_plans_nothing(self):
        self.assertEqual(self.take("No such task", [self.TASK]), (None, []))

    def test_a_take_of_a_task_with_the_key_line_plans_nothing(self):
        keyed = {**self.TASK, "description": f"4ag: {self.PATH}\nIt shows the first owner."}
        self.assertEqual(self.take(self.NAME, [keyed])[1], [])

    def run_main(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = queue_script.main(list(argv))
        return code, out.getvalue()

    def test_a_take_prints_the_title_and_the_description_and_honors_dry_run_and_root(self):
        read = lambda: Queue("p1", self.SECTIONS, [self.TASK], set())
        original, queue_script.read_queue = queue_script.read_queue, read
        self.addCleanup(setattr, queue_script, "read_queue", original)
        code, out = self.run_main("take", self.NAME, self.PATH, "--dry-run", "--root", str(ROOT))
        self.assertEqual(code, 0)
        self.assertIn(self.NAME, out)
        self.assertIn("It shows the first owner.", out)
        self.assertIn("td task update id:6j2Gr9TakeTask01 --description", out)
        self.assertIn("1 command planned, none sent.", out)

    def test_a_take_of_an_unknown_name_prints_one_warning_and_exits_0(self):
        read = lambda: Queue("p1", self.SECTIONS, [self.TASK], set())
        original, queue_script.read_queue = queue_script.read_queue, read
        self.addCleanup(setattr, queue_script, "read_queue", original)
        code, out = self.run_main("take", "No such task", ".scratch/bugs/none.md", "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(len([line for line in out.splitlines() if line.startswith("warning:")]), 1)
        self.assertNotIn("td ", out)


class TheCommandLine(unittest.TestCase):

    def test_a_merge_pr_wait_needs_the_pr_number(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit_:
            queue_script.main(["wait", "zz-queue-check", "merge-pr"])
        self.assertEqual(exit_.exception.code, 2)

    def test_an_unknown_kind_is_an_error(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit_:
            queue_script.main(["wait", "zz-queue-check", "approve-all"])
        self.assertEqual(exit_.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
