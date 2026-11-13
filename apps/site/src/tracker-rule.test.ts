/**
 * Holds docs/agents/state.md to the rule of ADR 0016: one row for each feature with an open ticket, and no other row.
 * An open ticket is a tracked .scratch/<feature>/issues/*.md or .scratch/<feature>/<app>/issues/*.md file whose Status is not done and not wontfix.
 */
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { describe, expect, it } from "vitest";
import { type Offense, report } from "./rule-report";

/* The tracker and the state file sit at the repo root, so the rule asks git for the root and not the folder of the app. */
const ROOT = execFileSync("git", ["rev-parse", "--show-toplevel"], { encoding: "utf8", env: cleanGitEnv() }).trim();
const STATE_FILE = "docs/agents/state.md";
/* A shared feature keeps a site and a pipeline subfolder, so a ticket path may name the app between the feature and issues. */
const TICKET_PATH = /^\.scratch\/([^/]+)\/(?:(site|pipeline)\/)?issues\/([^/]+)\.md$/;
const CLOSED = new Set(["done", "wontfix"]);

const RULE = `each feature with an open ticket has one row in ${STATE_FILE}, and no other feature has a row`;
const ADR = "docs/adr/0016-the-rules-are-checks.md";
const RULE_ID = "tracker/state-file";

/* The nine statuses of a ticket. The first word of a Status line must be one of them. */
const STATUSES = [
  "needs-triage", "needs-info", "ready-for-agent", "ready-for-human", "in-progress", "in-review", "blocked", "done", "wontfix",
];
const STATUS_RULE = "the first word of the Status line of a ticket is one of the nine statuses";
const STATUS_RULE_ID = "tracker/status";

type Ticket = { path: string; source: string };

/* An open ticket of a feature. The app is the subfolder of a shared feature, or null for a feature with no subfolder. */
type OpenTicket = { feature: string; app: string | null; name: string };

/* A row of the state file: the feature, the App cell, and the line. */
type Row = { feature: string; app: string; line: number };

/* Under the prek hook, git sets GIT_DIR, GIT_INDEX_FILE, and GIT_WORK_TREE, so git in another folder would read the real repo. */
function cleanGitEnv(): NodeJS.ProcessEnv {
  const env = { ...process.env };
  delete env.GIT_DIR;
  delete env.GIT_INDEX_FILE;
  delete env.GIT_WORK_TREE;
  return env;
}

/*
 * The rule reads tracked tickets only, through git ls-files, so the hook and CI see the same set.
 * An untracked draft ticket in one checkout does not change the verdict.
 */
function trackedTickets(root: string): Ticket[] {
  return execFileSync("git", ["ls-files", ".scratch"], { cwd: root, encoding: "utf8", env: cleanGitEnv() })
    .split("\n")
    .filter((path) => TICKET_PATH.test(path))
    .map((path) => ({ path, source: readFileSync(join(root, path), "utf8") }));
}

/*
 * The first word of the first Status line, plain or bold, in lowercase with no trailing punctuation. So "Done." and
 * "done, deployed 2026-10-22" read as done. A ticket with no Status line is open. The pipeline rule and
 * scripts/queue.py read it the same way.
 */
function status(source: string): string {
  const match = source.match(/^(?:\*\*)?Status:(?:\*\*)?[ \t]*(\S*)/m);
  return match ? match[1].toLowerCase().replace(/[.,;:]+$/, "") : "none";
}

/*
 * The lowest open ticket of each feature and app. The paths sort, so the lowest number comes first.
 * A shared feature can have an open ticket in each subfolder, so it can give two entries.
 */
function openTickets(tickets: Ticket[]): OpenTicket[] {
  const open = new Map<string, OpenTicket>();
  for (const { path, source } of [...tickets].sort((a, b) => a.path.localeCompare(b.path))) {
    const [, feature, app, name] = path.match(TICKET_PATH) ?? [];
    const key = `${feature}/${app ?? ""}`;
    if (feature && !CLOSED.has(status(source)) && !open.has(key)) open.set(key, { feature, app: app ?? null, name });
  }
  return [...open.values()];
}

/*
 * A row covers a ticket when it names the feature, and its App names the subfolder of the ticket or is both.
 * A ticket with no subfolder gives the rule no app, so any row of its feature covers it.
 */
function covers(row: Row, ticket: OpenTicket): boolean {
  return row.feature === ticket.feature && (ticket.app === null || row.app === ticket.app || row.app === "both");
}

/* Each table row below the header and the separator, with its line. The first cell is the feature and the second is the App, with backticks removed. */
function rows(source: string): Row[] {
  return source
    .split("\n")
    .map((text, index) => ({ text: text.trim(), line: index + 1 }))
    .filter(({ text }) => text.startsWith("|"))
    .slice(2)
    .map(({ text, line }) => {
      const cells = text.split("|").map((cell) => cell.trim().replace(/`/g, ""));
      return { feature: cells[1], app: cells[2] ?? "", line };
    });
}

/* The rule takes the ticket list and the state file source apart from the disk, so a test can pass its own. */
function offenses(tickets: Ticket[], stateSource: string): Offense[] {
  const open = openTickets(tickets);
  const listed = rows(stateSource);
  const at = { path: STATE_FILE, ruleId: RULE_ID, rule: RULE, adr: ADR };
  const missing = open
    .filter((ticket) => !listed.some((row) => covers(row, ticket)))
    .map(({ feature, app, name }) => ({
      ...at,
      line: 1,
      what: `${feature} has the open ticket ${app ? `${app}/${name}` : name}, and the state file has no row for it.`,
      fix: app ? `add a row to ${STATE_FILE} with the App ${app}.` : `add a row to ${STATE_FILE}.`,
    }));
  const stale = listed
    .filter((row) => !open.some((ticket) => covers(row, ticket)))
    .map(({ feature, app, line }) => ({
      ...at,
      line,
      what: `The row for ${feature} with the App ${app} names a feature with no open ticket there.`,
      fix: "remove the row, because the feature is done.",
    }));
  return [...missing, ...stale];
}

/* One offense for each ticket whose Status has a first word outside the nine statuses. A ticket with no Status line is legal and open. */
function statusOffenses(tickets: Ticket[]): Offense[] {
  return tickets.flatMap(({ path, source }) => {
    const word = status(source);
    if (word === "none" || STATUSES.includes(word)) return [];
    const line = source.split("\n").findIndex((text) => /^(?:\*\*)?Status:/.test(text)) + 1;
    return [{
      path,
      line,
      ruleId: STATUS_RULE_ID,
      what: `The ticket has the status ${word || "none"}, and it is not one of the nine statuses.`,
      rule: STATUS_RULE,
      adr: ADR,
      fix: `set the first word of the Status line to one of: ${STATUSES.join(", ")}.`,
    }];
  });
}

function fakeTicket(path: string, statusLine: string): Ticket {
  return { path, source: `# A ticket\n\n${statusLine}\n` };
}

const TABLE = "| Feature | App | Next ticket | Blocked by | Hold |\n| --- | --- | --- | --- | --- |\n";

describe("the tracker rule", () => {
  it("finds the tracked tickets", () => {
    // An empty list would pass with no ticket read.
    const paths = trackedTickets(ROOT).map(({ path }) => path);
    expect(paths).toContain(".scratch/agent-habits/site/issues/02-a-state-file-lists-each-open-feature-and-its-next-step.md");
  });

  it("finds one row in the state file for each feature with an open ticket, and no other row", () => {
    const found = offenses(trackedTickets(ROOT), readFileSync(join(ROOT, STATE_FILE), "utf8"));
    if (found.length > 0) throw new Error(report(found));
  });

  it("reads a done, a wontfix, and a done with a note as closed, and a PRD as no ticket", () => {
    const tickets = [
      fakeTicket(".scratch/a/issues/01-x.md", "**Status:** done"),
      fakeTicket(".scratch/a/issues/02-y.md", "**Status:** wontfix"),
      fakeTicket(".scratch/a/issues/03-z.md", "**Status:** done, deployed 2026-10-22"),
      fakeTicket(".scratch/b/PRD.md", "Status: ready-for-agent"),
    ];
    expect(offenses(tickets, TABLE)).toEqual([]);
  });

  it("reads a plain Status line and a capital Done as closed, the same as the pipeline rule", () => {
    const tickets = [
      fakeTicket(".scratch/a/issues/01-x.md", "Status: Done"),
      fakeTicket(".scratch/a/issues/02-y.md", "**Status:** Done;"),
    ];
    expect(offenses(tickets, TABLE)).toEqual([]);
    expect(statusOffenses(tickets)).toEqual([]);
    const odd = statusOffenses([fakeTicket(".scratch/a/issues/03-z.md", "Status: backlog")]);
    expect(odd.map(({ line, ruleId }) => ({ line, ruleId }))).toEqual([{ line: 3, ruleId: "tracker/status" }]);
  });

  it("finds one offense at line 1 for a feature with an open ticket and no row", () => {
    const tickets = [fakeTicket(".scratch/a/issues/01-x.md", "**Status:** done"), fakeTicket(".scratch/a/issues/02-y.md", "**Status:** triage")];
    const found = offenses(tickets, TABLE);
    expect(found.map(({ line, ruleId, what }) => ({ line, ruleId, what }))).toEqual([
      { line: 1, ruleId: "tracker/state-file", what: "a has the open ticket 02-y, and the state file has no row for it." },
    ]);
  });

  it("finds one offense at the line of a row with no open ticket", () => {
    const tickets = [fakeTicket(".scratch/a/issues/01-x.md", "**Status:** ready-for-agent"), fakeTicket(".scratch/b/issues/01-x.md", "**Status:** done")];
    const state = `# State\n\n${TABLE}| \`a\` | site | 01 | none | |\n| \`b\` | site | 02 | none | |\n`;
    const found = offenses(tickets, state);
    expect(found.map(({ line, ruleId, fix }) => ({ line, ruleId, fix }))).toEqual([
      { line: 6, ruleId: "tracker/state-file", fix: "remove the row, because the feature is done." },
    ]);
  });

  it("finds a ticket at backlog, names it, and passes a ticket with no Status line", () => {
    const tickets = [
      fakeTicket(".scratch/zz-rule/issues/01-zz.md", "**Status:** backlog"),
      { path: ".scratch/zz-rule/issues/02-zz.md", source: "# A ticket\n\nNo status yet.\n" },
      fakeTicket(".scratch/zz-rule/issues/03-zz.md", "**Status:** done 2026-10-24"),
    ];
    const found = statusOffenses(tickets);
    expect(found.map(({ path, line, ruleId }) => ({ path, line, ruleId }))).toEqual([
      { path: ".scratch/zz-rule/issues/01-zz.md", line: 3, ruleId: "tracker/status" },
    ]);
    expect(found[0].what).toContain("backlog");
  });

  it("gives each tracked ticket one of the nine statuses", () => {
    const found = statusOffenses(trackedTickets(ROOT));
    if (found.length > 0) throw new Error(report(found));
  });

  it("finds one offense in a tracker folder on disk with one open ticket and an empty state file", () => {
    // The folder goes through the same git ls-files read as the real tree, so a break in the read also fails here.
    const dir = mkdtempSync(join(tmpdir(), "tracker-rule-"));
    try {
      const path = ".scratch/waiver/issues/01-the-route.md";
      mkdirSync(dirname(join(dir, path)), { recursive: true });
      writeFileSync(join(dir, path), "# 01: The route\n\n**Status:** ready-for-agent\n");
      mkdirSync(join(dir, "docs/agents"), { recursive: true });
      writeFileSync(join(dir, STATE_FILE), "");
      // Under the prek hook, git sets these three keys. With them, git add here would write to the index of the real repo.
      const env = cleanGitEnv();
      execFileSync("git", ["init", "--quiet"], { cwd: dir, env });
      execFileSync("git", ["add", "."], { cwd: dir, env });
      const found = offenses(trackedTickets(dir), readFileSync(join(dir, STATE_FILE), "utf8"));
      expect(found.map(({ path, line, ruleId }) => ({ path, line, ruleId }))).toEqual([
        { path: STATE_FILE, line: 1, ruleId: "tracker/state-file" },
      ]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("counts a subfolder ticket for its feature and app, so a row of the other app does not cover it", () => {
    // A shared feature keeps a site and a pipeline subfolder. The row for the site does not cover an open pipeline ticket.
    const dir = mkdtempSync(join(tmpdir(), "tracker-rule-"));
    try {
      const tickets = {
        ".scratch/waiver/site/issues/01-the-route.md": "**Status:** done",
        ".scratch/waiver/pipeline/issues/09-usage-floor.md": "**Status:** needs-triage",
      };
      for (const [path, statusLine] of Object.entries(tickets)) {
        mkdirSync(dirname(join(dir, path)), { recursive: true });
        writeFileSync(join(dir, path), `# A ticket\n\n${statusLine}\n`);
      }
      const env = cleanGitEnv();
      execFileSync("git", ["init", "--quiet"], { cwd: dir, env });
      execFileSync("git", ["add", "."], { cwd: dir, env });
      const found = offenses(trackedTickets(dir), `${TABLE}| \`waiver\` | site | 01 | none | |\n`);
      expect(found.map(({ line, what }) => ({ line, what }))).toEqual([
        { line: 1, what: "waiver has the open ticket pipeline/09-usage-floor, and the state file has no row for it." },
        { line: 3, what: "The row for waiver with the App site names a feature with no open ticket there." },
      ]);
      expect(offenses(trackedTickets(dir), `${TABLE}| \`waiver\` | pipeline | 09 | none | |\n`)).toEqual([]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
