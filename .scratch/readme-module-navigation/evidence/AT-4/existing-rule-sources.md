Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base revision: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.
All source excerpts below come from Git objects at the stated revision.
No behavior test or cold task runs during this static capture.

## `apps/site/src/readme-rule.test.ts` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–175

```text
1: /**
2:  * Holds each package folder to the rule of ADR 0016: a README of under 25 lines with the headings Knows, Ports, and Does not do.
3:  * A package folder is each folder directly under src/components/, when it exists, and src/lib/, plus src/lib/ and src/hooks/ when it exists.
4:  * Each package under packages/ is a package folder too (ADR 0023), with each folder directly under its site side.
5:  * No tracked CLAUDE.md sits below the root, except one at the top of each app in apps/.
6:  */
7: import { execFileSync } from "node:child_process";
8: import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
9: import { tmpdir } from "node:os";
10: import { basename, join, relative } from "node:path";
11: import { describe, expect, it } from "vitest";
12: import { type Offense, report } from "./rule-report";
13: 
14: const ROOT = process.cwd();
15: const SRC = join(ROOT, "src");
16: const PACKAGES = join(ROOT, "..", "..", "packages");
17: 
18: /* The title, then the three headings in this order. The title text has no rule. */
19: const HEADINGS = ["## Knows", "## Ports", "## Does not do"];
20: const MAX_LINES = 24;
21: 
22: const RULE = `each package folder holds a README of under ${MAX_LINES + 1} lines with the headings Knows, Ports, and Does not do`;
23: const CLAUDE_MD_RULE = "no CLAUDE.md sits below the repo root, except one at the top of each app";
24: /* Each app keeps a short CLAUDE.md with its own commands, so apps/<app>/CLAUDE.md is allowed. See .scratch/one/PRD.md. */
25: const APP_CLAUDE_MD = /^apps\/[^/]+\/CLAUDE\.md$/;
26: const ADR = "docs/adr/0016-the-rules-are-checks.md";
27: 
28: function subfolders(dir: string): string[] {
29:   if (!existsSync(dir)) return [];
30:   return readdirSync(dir, { withFileTypes: true })
31:     .filter((entry) => entry.isDirectory() && entry.name !== "node_modules")
32:     .map((entry) => join(dir, entry.name));
33: }
34: 
35: /* The rule finds the folders and holds no list, so a new folder needs a README on its first day. */
36: function packageFolders(): string[] {
37:   const components = join(SRC, "components");
38:   const lib = join(SRC, "lib");
39:   const packages = subfolders(PACKAGES);
40:   const siteFolders = packages.flatMap((dir) => subfolders(join(dir, "site")));
41:   // The app holds no hook of its own, so src/hooks/ is a package folder only when it exists.
42:   const hooks = existsSync(join(SRC, "hooks")) ? [join(SRC, "hooks")] : [];
43:   return [...subfolders(components), lib, ...subfolders(lib), ...hooks, ...packages, ...siteFolders];
44: }
45: 
46: /* The source is null when the folder holds no README. */
47: function readFolder(dir: string): { path: string; source: string | null } {
48:   const file = join(dir, "README.md");
49:   return { path: relative(ROOT, file), source: existsSync(file) ? readFileSync(file, "utf8") : null };
50: }
51: 
52: /* The rule takes the path and the source apart from the disk, so a test can run it on one string. */
53: function offenses(path: string, source: string | null): Offense[] {
54:   const at = { path, line: 1, rule: RULE, adr: ADR };
55:   if (source === null) {
56:     return [
57:       {
58:         ...at,
59:         ruleId: "readme/missing",
60:         what: `${path.slice(0, -"/README.md".length)} holds no README.md.`,
61:         fix: "add a README.md with a one-line title and the headings Knows, Ports, and Does not do.",
62:       },
63:     ];
64:   }
65:   const found: Offense[] = [];
66:   const lines = source.replace(/\n$/, "").split("\n");
67:   const headings = lines.filter((line) => line.startsWith("#"));
68:   const titled = headings.length > 0 && headings[0].startsWith("# ");
69:   if (!titled || headings.slice(1).join("\n") !== HEADINGS.join("\n")) {
70:     found.push({
71:       ...at,
72:       ruleId: "readme/headings",
73:       what: `${basename(path)} has the headings ${headings.join(", ") || "none"}.`,
74:       fix: "write a one-line title, then exactly ## Knows, ## Ports, and ## Does not do, in that order.",
75:     });
76:   }
77:   if (lines.length > MAX_LINES) {
78:     found.push({
79:       ...at,
80:       line: MAX_LINES + 1,
81:       ruleId: "readme/length",
82:       what: `${basename(path)} has ${lines.length} lines.`,
83:       fix: `cut the README to under ${MAX_LINES + 1} lines, and move the detail into the header comments of the files.`,
84:     });
85:   }
86:   return found;
87: }
88: 
89: /* The paths come from git ls-files, so a CLAUDE.md in node_modules or in an ignored folder does not count. */
90: function claudeMdOffenses(paths: string[]): Offense[] {
91:   return paths
92:     .filter((path) => basename(path) === "CLAUDE.md" && path !== "CLAUDE.md" && !APP_CLAUDE_MD.test(path))
93:     .map((path) => ({
94:       path,
95:       line: 1,
96:       ruleId: "readme/no-claude-md",
97:       what: `${path} is a tracked CLAUDE.md below the root.`,
98:       rule: CLAUDE_MD_RULE,
99:       adr: ADR,
100:       fix: "move the text into the README.md of the folder and delete the CLAUDE.md.",
101:     }));
102: }
103: 
104: /* The pathspec ":/" and --full-name give every tracked file of the repo with its path from the repo root, from any folder. */
105: function trackedFiles(): string[] {
106:   return execFileSync("git", ["ls-files", "--full-name", "--", ":/"], { cwd: ROOT, encoding: "utf8" }).split("\n").filter(Boolean);
107: }
108: 
109: describe("the readme rule", () => {
110:   it("finds the package folders", () => {
111:     // An empty list would pass with no folder read.
112:     const paths = packageFolders().map((dir) => relative(ROOT, dir));
113:     expect(paths).toEqual(expect.arrayContaining([
114:         "../../packages/rankings/site/chapters",
115:         "../../packages/week/site/chapters",
116:         "src/lib",
117:         "../../packages/design",
118:         "../../packages/design/site/shell",
119:       ]),);
120:   });
121: 
122:   it("finds a README with the three headings and under 25 lines in each package folder", () => {
123:     const found = packageFolders()
124:       .map(readFolder)
125:       .flatMap(({ path, source }) => offenses(path, source));
126:     if (found.length > 0) throw new Error(report(found));
127:   });
128: 
129:   it("finds no tracked CLAUDE.md below the root", () => {
130:     const paths = trackedFiles();
131:     // An empty list would pass and does not run git.
132:     expect(paths).toContain("CLAUDE.md");
133:     const found = claudeMdOffenses(paths);
134:     if (found.length > 0) throw new Error(report(found));
135:   });
136: 
137:   it("finds one offense in a README of 25 lines", () => {
138:     const source = ["# lib", ...HEADINGS, ...Array(21).fill("A line.")].join("\n") + "\n";
139:     const found = offenses("src/lib/README.md", source);
140:     expect(found.map(({ ruleId, line }) => ({ ruleId, line }))).toEqual([{ ruleId: "readme/length", line: 25 }]);
141:   });
142: 
143:   it("finds one offense in a CLAUDE.md below the root", () => {
144:     const found = claudeMdOffenses([
145:       "CLAUDE.md",
146:       "apps/pipeline/CLAUDE.md",
147:       "apps/site/src/lib/CLAUDE.md",
148:       ".scratch/notes-on-CLAUDE.md",
149:     ]);
150:     expect(found.map(({ path, ruleId }) => ({ path, ruleId }))).toEqual([{ path: "apps/site/src/lib/CLAUDE.md", ruleId: "readme/no-claude-md" }]);
151:   });
152: 
153:   it("finds one offense in a folder on disk with one source file and no README", () => {
154:     // The folder goes through the same disk path as the real tree, so a break in the read also fails here.
155:     const dir = mkdtempSync(join(tmpdir(), "readme-rule-"));
156:     try {
157:       writeFileSync(join(dir, "standings.tsx"), "export const a = 1;\n");
158:       const { path, source } = readFolder(dir);
159:       expect(offenses(path, source).map(({ ruleId }) => ruleId)).toEqual(["readme/missing"]);
160:     } finally {
161:       rmSync(dir, { recursive: true, force: true });
162:     }
163:   });
164: 
165:   it("finds one offense in a README on disk with the headings out of order", () => {
166:     const dir = mkdtempSync(join(tmpdir(), "readme-rule-"));
167:     try {
168:       writeFileSync(join(dir, "README.md"), "# week\n\n## Ports\n\nNone.\n\n## Knows\n\n## Does not do\n");
169:       const { path, source } = readFolder(dir);
170:       expect(offenses(path, source).map(({ ruleId }) => ruleId)).toEqual(["readme/headings"]);
171:     } finally {
172:       rmSync(dir, { recursive: true, force: true });
173:     }
174:   });
175: });
```

## `apps/pipeline/tests/test_rule_readmes.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–220

```text
1: """
2: Checks that each package folder under src holds a README.md with the headings Knows, Ports, and Does not do.
3: Each README is under 25 lines, and the only CLAUDE.md is the one at the repo root. See ADR 0014.
4: Each package under packages/ at the repo root holds a README.md with the same headings and length. See ADR 0023.
5: """
6: import subprocess
7: from pathlib import Path
8: 
9: from rule_report import Offense, clean_git_env, report
10: 
11: ROOT = Path(__file__).resolve().parent.parent
12: # The repo root, which holds packages/.
13: REPO = ROOT.parent.parent
14: ADR = "docs/adr/0014-the-rules-are-checks.md"
15: PACKAGE_ADR = "docs/adr/0023-a-package-holds-one-domain-in-both-languages.md"
16: HEADINGS = ["## Knows", "## Ports", "## Does not do"]
17: # An agent reads the README to decide whether to open the folder. A short README means an agent reads little.
18: MAX_LINES = 24
19: 
20: MISSING_RULE = "each folder under src that holds an __init__.py holds a README.md"
21: HEADINGS_RULE = "a package README has a one-line title, then the headings Knows, Ports, and Does not do, in that order"
22: HEADINGS_FIX = "give the README a title on line 1, then exactly ## Knows, ## Ports, and ## Does not do, in that order."
23: LENGTH_RULE = "a package README is under 25 lines"
24: CLAUDE_MD_RULE = "the only CLAUDE.md is the one at the repo root"
25: 
26: 
27: def _package_folders(root: Path) -> list[Path]:
28:     """Each folder under src that holds an __init__.py."""
29:     return sorted(path.parent for path in (root / "src").rglob("__init__.py"))
30: 
31: 
32: def _readmes(root: Path) -> list[Path]:
33:     return [folder / "README.md" for folder in _package_folders(root) if (folder / "README.md").is_file()]
34: 
35: 
36: def _repo_path(path: Path, root: Path) -> str:
37:     return path.relative_to(root).as_posix()
38: 
39: 
40: def _missing_offenses(root: Path) -> list[Offense]:
41:     # The README does not exist, so the offense names line 1 of the __init__.py that makes the folder a package.
42:     return [Offense(
43:         path=_repo_path(folder / "__init__.py", root),
44:         line=1,
45:         rule_id="readme/missing",
46:         what=f"{_repo_path(folder, root)} holds an __init__.py and no README.md.",
47:         rule=MISSING_RULE,
48:         adr=ADR,
49:         fix=f"add {_repo_path(folder, root)}/README.md with a title and the headings Knows, Ports, and Does not do.",
50:     ) for folder in _package_folders(root) if not (folder / "README.md").is_file()]
51: 
52: 
53: def _heading_offenses(root: Path) -> list[Offense]:
54:     offenses: list[Offense] = []
55:     for readme in _readmes(root):
56:         lines = readme.read_text().splitlines()
57:         headings = [line for line in lines if line.startswith("#")]
58:         has_title = bool(lines) and lines[0].startswith("# ")
59:         if not has_title or headings[1:] != HEADINGS:
60:             offenses.append(Offense(
61:                 path=_repo_path(readme, root),
62:                 line=1,
63:                 rule_id="readme/headings",
64:                 what=f"The headings are: {', '.join(headings) or 'none'}.",
65:                 rule=HEADINGS_RULE,
66:                 adr=ADR,
67:                 fix=HEADINGS_FIX,
68:             ))
69:     return offenses
70: 
71: 
72: def _length_offenses(root: Path) -> list[Offense]:
73:     offenses: list[Offense] = []
74:     for readme in _readmes(root):
75:         count = len(readme.read_text().splitlines())
76:         if count > MAX_LINES:
77:             offenses.append(Offense(
78:                 path=_repo_path(readme, root),
79:                 line=MAX_LINES + 1,
80:                 rule_id="readme/length",
81:                 what=f"The README has {count} lines.",
82:                 rule=LENGTH_RULE,
83:                 adr=ADR,
84:                 fix=f"cut the README to {MAX_LINES} lines, and move each detail to the docstring of its module.",
85:             ))
86:     return offenses
87: 
88: 
89: def _package_readme_offenses(repo: Path) -> list[Offense]:
90:     """The packages under packages/ with no README.md, and each package README that breaks the heading or length rule."""
91:     offenses: list[Offense] = []
92:     for folder in sorted(path for path in (repo / "packages").glob("*") if path.is_dir()):
93:         readme = folder / "README.md"
94:         where = _repo_path(folder, repo)
95:         if not readme.is_file():
96:             offenses.append(Offense(
97:                 path=where, line=1, rule_id="readme/missing", what=f"{where} holds no README.md.",
98:                 rule="each package holds a README.md", adr=PACKAGE_ADR,
99:                 fix=f"add {where}/README.md with a title and the headings Knows, Ports, and Does not do."))
100:             continue
101:         lines = readme.read_text().splitlines()
102:         headings = [line for line in lines if line.startswith("#")]
103:         if not (lines and lines[0].startswith("# ")) or headings[1:] != HEADINGS:
104:             offenses.append(Offense(
105:                 path=_repo_path(readme, repo), line=1, rule_id="readme/headings",
106:                 what=f"The headings are: {', '.join(headings) or 'none'}.", rule=HEADINGS_RULE, adr=PACKAGE_ADR,
107:                 fix=HEADINGS_FIX))
108:         if len(lines) > MAX_LINES:
109:             offenses.append(Offense(
110:                 path=_repo_path(readme, repo), line=MAX_LINES + 1, rule_id="readme/length",
111:                 what=f"The README has {len(lines)} lines.", rule=LENGTH_RULE, adr=PACKAGE_ADR,
112:                 fix=f"cut the README to {MAX_LINES} lines, and move each detail to the docstring of its module."))
113:     return offenses
114: 
115: 
116: def _tracked_files(root: Path) -> list[str]:
117:     """The paths that git tracks, from the repo root. A staged file counts, so the hook sees a new one."""
118:     result = subprocess.run(
119:         ["git", "ls-files"], cwd=root, check=True, capture_output=True, text=True, env=clean_git_env()
120:     )
121:     return result.stdout.splitlines()
122: 
123: 
124: def _claude_md_offenses(tracked: list[str]) -> list[Offense]:
125:     # A nested CLAUDE.md loads by itself. The agent must choose to read the next level, so the folder holds a README.
126:     return [Offense(
127:         path=path,
128:         line=1,
129:         rule_id="readme/no-claude-md",
130:         what=f"{path} is a CLAUDE.md below the repo root.",
131:         rule=CLAUDE_MD_RULE,
132:         adr=ADR,
133:         fix="move the text to the README.md of the folder, and remove the CLAUDE.md.",
134:     ) for path in tracked if Path(path).name == "CLAUDE.md" and path != "CLAUDE.md"]
135: 
136: 
137: def test_each_package_of_the_repo_has_a_readme_with_the_three_headings():
138:     offenses = _package_readme_offenses(REPO)
139:     assert not offenses, report(offenses)
140: 
141: 
142: def test_the_rule_finds_a_package_of_the_repo_with_no_readme(tmp_path):
143:     (tmp_path / "packages" / "league" / "python").mkdir(parents=True)
144:     assert [(offense.path, offense.rule_id) for offense in _package_readme_offenses(tmp_path)] == [
145:         ("packages/league", "readme/missing")]
146: 
147: 
148: def test_the_rule_finds_a_package_readme_with_no_ports_heading(tmp_path):
149:     package = tmp_path / "packages" / "league"
150:     package.mkdir(parents=True)
151:     (package / "README.md").write_text("# league\n\n## Knows\n\nThe kernel.\n\n## Does not do\n\nNo app.\n")
152:     assert [(offense.path, offense.rule_id) for offense in _package_readme_offenses(tmp_path)] == [
153:         ("packages/league/README.md", "readme/headings")]
154: 
155: 
156: def test_each_package_folder_has_a_readme():
157:     offenses = _missing_offenses(ROOT)
158:     assert not offenses, report(offenses)
159: 
160: 
161: def test_each_readme_has_the_three_headings():
162:     offenses = _heading_offenses(ROOT)
163:     assert not offenses, report(offenses)
164: 
165: 
166: def test_each_readme_is_under_25_lines():
167:     offenses = _length_offenses(ROOT)
168:     assert not offenses, report(offenses)
169: 
170: 
171: def test_no_claude_md_below_the_root():
172:     offenses = _claude_md_offenses(_tracked_files(ROOT))
173:     assert not offenses, report(offenses)
174: 
175: 
176: def test_the_rule_finds_a_package_folder_with_no_readme(tmp_path):
177:     package = tmp_path / "src" / "cornerstone"
178:     package.mkdir(parents=True)
179:     (package / "__init__.py").write_text('"""A package."""\n')
180:     assert _missing_offenses(tmp_path) == [Offense(
181:         path="src/cornerstone/__init__.py",
182:         line=1,
183:         rule_id="readme/missing",
184:         what="src/cornerstone holds an __init__.py and no README.md.",
185:         rule=MISSING_RULE,
186:         adr=ADR,
187:         fix="add src/cornerstone/README.md with a title and the headings Knows, Ports, and Does not do.",
188:     )]
189: 
190: 
191: def test_the_rule_finds_a_readme_of_25_lines(tmp_path):
192:     package = tmp_path / "src" / "cornerstone"
193:     package.mkdir(parents=True)
194:     (package / "__init__.py").write_text('"""A package."""\n')
195:     (package / "README.md").write_text("# cornerstone\n" + "\n" * 24)
196:     offenses = _length_offenses(tmp_path)
197:     assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
198:         ("src/cornerstone/README.md", 25, "readme/length")]
199: 
200: 
201: def test_the_rule_finds_a_claude_md_below_the_root():
202:     offenses = _claude_md_offenses(["CLAUDE.md", "src/cornerstone/CLAUDE.md"])
203:     assert [(offense.path, offense.line, offense.rule_id) for offense in offenses] == [
204:         ("src/cornerstone/CLAUDE.md", 1, "readme/no-claude-md")]
205: 
206: 
207: def test_the_rule_finds_a_readme_with_no_ports_heading(tmp_path):
208:     package = tmp_path / "src" / "cornerstone"
209:     package.mkdir(parents=True)
210:     (package / "__init__.py").write_text('"""A package."""\n')
211:     (package / "README.md").write_text("# cornerstone\n\n## Knows\n\nThe facts.\n\n## Does not do\n\nNo prose.\n")
212:     assert _heading_offenses(tmp_path) == [Offense(
213:         path="src/cornerstone/README.md",
214:         line=1,
215:         rule_id="readme/headings",
216:         what="The headings are: # cornerstone, ## Knows, ## Does not do.",
217:         rule=HEADINGS_RULE,
218:         adr=ADR,
219:         fix=HEADINGS_FIX,
220:     )]
```

## `apps/api/tests/test_rule_api.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–49

```text
1: """
2: Runs the rule tests of the pipeline on the API app: the import layers, the suppression comments, and the READMEs.
3: The rules live in the pipeline tests, and each one takes the root it reads. See ADR 0010 and ADR 0014.
4: """
5: from pathlib import Path
6: 
7: import test_layers as layers
8: import test_rule_readmes as readmes
9: import test_rule_suppressions as suppressions
10: from rule_report import report
11: 
12: ROOT = Path(__file__).resolve().parent.parent
13: SRC = ROOT / "src"
14: MARKER = suppressions.MARKER
15: 
16: # The allow list of the API, in the shape of the allow list of the pipeline. The key is the path from the API app.
17: ALLOW: dict[tuple[str, str], str] = {
18:     ("src/cornerstone_api/app.py",
19:      f"except Exception as error:  # {MARKER}: BLE001 - the app keeps running after a failed refresh"):
20:         "the app keeps running after a failed refresh",
21:     ("src/cornerstone_api/sources.py",
22:      f"read_chart: ChartReader = partial(chart_values, read=claude_reader(parse_call))  # {MARKER}: RUF009"):
23:         "one shared partial holds no state that a call changes",
24: }
25: 
26: 
27: def test_the_api_imports_only_from_layer_write_or_a_lower_one():
28:     offenses = layers._import_offenses(layers.SRC, SRC)
29:     assert not offenses, report(offenses)
30: 
31: 
32: def test_the_rule_reads_each_module_of_the_api():
33:     modules = layers._modules(layers.SRC, SRC)
34:     assert {"cornerstone_api.app", "cornerstone_api.sources"} <= set(modules)
35: 
36: 
37: def test_no_comment_in_the_api_silences_a_rule():
38:     offenses = suppressions._comment_offenses(ROOT, ALLOW)
39:     assert not offenses, report(offenses)
40: 
41: 
42: def test_the_allow_list_of_the_api_names_only_lines_that_exist():
43:     found = {(path, text) for path, _, text in suppressions._suppressions(ROOT)}
44:     assert [key for key in ALLOW if key not in found] == []
45: 
46: 
47: def test_each_package_folder_of_the_api_has_a_readme_with_the_three_headings():
48:     offenses = readmes._missing_offenses(ROOT) + readmes._heading_offenses(ROOT) + readmes._length_offenses(ROOT)
49:     assert not offenses, report(offenses)
```

Rule source diff, base to implementation:

```diff
```
