/**
 * Holds docs/agents/state.md to the rule of ADR 0006: one row for each feature with an open ticket, and no other row.
 * An open ticket is a tracked .scratch/<feature>/issues/*.md file whose Status is not done and not wontfix.
 */
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { describe, expect, it } from "vitest";
import { type Offense, report } from "./rule-report";

const ROOT = process.cwd();
const STATE_FILE = "docs/agents/state.md";
const TICKET = /^\.scratch\/([^/]+)\/issues\/([^/]+)\.md$/;
const CLOSED = new Set(["done", "wontfix"]);

const RULE = `each feature with an open ticket has one row in ${STATE_FILE}, and no other feature has a row`;
const ADR = "docs/adr/0006-the-rules-are-checks.md";

type Ticket = { path: string; source: string };

/*
 * The rule reads tracked tickets only, through git ls-files, so the hook and CI see the same set.
 * An untracked draft ticket in one checkout does not change the verdict.
 */
function trackedTickets(root: string): Ticket[] {
  return execFileSync("git", ["ls-files", ".scratch"], { cwd: root, encoding: "utf8" })
    .split("\n")
    .filter((path) => TICKET.test(path))
    .map((path) => ({ path, source: readFileSync(join(root, path), "utf8") }));
}

/* The first word of the first Status line, so "done, deployed 2026-10-22" reads as done. A ticket with no Status line is open. */
function status(source: string): string {
  const match = source.match(/^(?:\*\*)?Status:(?:\*\*)?\s*([^\s,.]+)/m);
  return match ? match[1].toLowerCase() : "none";
}

/* Each feature with an open ticket, and the lowest open ticket of it. The paths sort, so the lowest number comes first. */
function openFeatures(tickets: Ticket[]): Map<string, string> {
  const open = new Map<string, string>();
  for (const { path, source } of [...tickets].sort((a, b) => a.path.localeCompare(b.path))) {
    const [, feature, name] = path.match(TICKET) ?? [];
    if (feature && !CLOSED.has(status(source)) && !open.has(feature)) open.set(feature, name);
  }
  return open;
}

/* Each table row below the header and the separator, with its line. The first cell is the feature, with its backticks removed. */
function rows(source: string): { feature: string; line: number }[] {
  return source
    .split("\n")
    .map((text, index) => ({ text: text.trim(), line: index + 1 }))
    .filter(({ text }) => text.startsWith("|"))
    .slice(2)
    .map(({ text, line }) => ({ feature: text.split("|")[1].trim().replace(/`/g, ""), line }));
}

/* The rule takes the ticket list and the state file source apart from the disk, so a test can pass its own. */
function offenses(tickets: Ticket[], stateSource: string): Offense[] {
  const open = openFeatures(tickets);
  const listed = rows(stateSource);
  const names = new Set(listed.map(({ feature }) => feature));
  const missing = [...open]
    .filter(([feature]) => !names.has(feature))
    .map(([feature, ticket]) => ({
      path: STATE_FILE,
      line: 1,
      ruleId: "tracker/state-file",
      what: `${feature} has the open ticket ${ticket}, and the state file has no row for it.`,
      rule: RULE,
      adr: ADR,
      fix: `add a row to ${STATE_FILE}.`,
    }));
  const stale = listed
    .filter(({ feature }) => !open.has(feature))
    .map(({ feature, line }) => ({
      path: STATE_FILE,
      line,
      ruleId: "tracker/state-file",
      what: `The row for ${feature} names a feature with no open ticket.`,
      rule: RULE,
      adr: ADR,
      fix: "remove the row, because the feature is done.",
    }));
  return [...missing, ...stale];
}

function ticket(path: string, statusLine: string): Ticket {
  return { path, source: `# A ticket\n\n${statusLine}\n` };
}

const TABLE = "| Feature | Next ticket | Blocked by | Hold |\n| --- | --- | --- | --- |\n";

describe("the tracker rule", () => {
  it("finds the tracked tickets", () => {
    // An empty list would pass with no ticket read.
    const paths = trackedTickets(ROOT).map(({ path }) => path);
    expect(paths).toContain(".scratch/agent-habits/issues/02-a-state-file-lists-each-open-feature-and-its-next-step.md");
  });

  it("finds one row in the state file for each feature with an open ticket, and no other row", () => {
    const found = offenses(trackedTickets(ROOT), readFileSync(join(ROOT, STATE_FILE), "utf8"));
    if (found.length > 0) throw new Error(report(found));
  });

  it("reads a done, a wontfix, and a done with a note as closed, and a PRD as no ticket", () => {
    const tickets = [
      ticket(".scratch/a/issues/01-x.md", "**Status:** done"),
      ticket(".scratch/a/issues/02-y.md", "**Status:** wontfix"),
      ticket(".scratch/a/issues/03-z.md", "**Status:** done, deployed 2026-10-22"),
      ticket(".scratch/b/PRD.md", "Status: ready-for-agent"),
    ];
    expect(offenses(tickets, TABLE)).toEqual([]);
  });

  it("finds one offense at line 1 for a feature with an open ticket and no row", () => {
    const tickets = [ticket(".scratch/a/issues/01-x.md", "**Status:** done"), ticket(".scratch/a/issues/02-y.md", "**Status:** triage")];
    const found = offenses(tickets, TABLE);
    expect(found.map(({ line, ruleId, what }) => ({ line, ruleId, what }))).toEqual([
      { line: 1, ruleId: "tracker/state-file", what: "a has the open ticket 02-y, and the state file has no row for it." },
    ]);
  });

  it("finds one offense at the line of a row with no open ticket", () => {
    const tickets = [ticket(".scratch/a/issues/01-x.md", "**Status:** ready-for-agent"), ticket(".scratch/b/issues/01-x.md", "**Status:** done")];
    const state = `# State\n\n${TABLE}| \`a\` | 01 | none | |\n| \`b\` | 02 | none | |\n`;
    const found = offenses(tickets, state);
    expect(found.map(({ line, ruleId, fix }) => ({ line, ruleId, fix }))).toEqual([
      { line: 6, ruleId: "tracker/state-file", fix: "remove the row, because the feature is done." },
    ]);
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
      execFileSync("git", ["init", "--quiet"], { cwd: dir });
      execFileSync("git", ["add", "."], { cwd: dir });
      const found = offenses(trackedTickets(dir), readFileSync(join(dir, STATE_FILE), "utf8"));
      expect(found.map(({ path, line, ruleId }) => ({ path, line, ruleId }))).toEqual([
        { path: STATE_FILE, line: 1, ruleId: "tracker/state-file" },
      ]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
