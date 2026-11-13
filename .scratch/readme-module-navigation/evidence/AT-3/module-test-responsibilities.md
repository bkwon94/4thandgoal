Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base revision: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.
All source excerpts below come from Git objects at the stated revision.
No behavior test or cold task runs during this static capture.

# T1 archive

The comparator orders numeric seasons descending, then numeric weeks descending. The assertion places 2027/01 before 2026/10 before 2026/02.

## `apps/site/src/lib/data/week-data.ts` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–64

```text
1: /**
2:  * Reads the week page JSON files from public/ at build time.
3:  * The week folder is the data folder, so the route and the images share one path.
4:  */
5: import { existsSync, readdirSync } from "node:fs";
6: import { join } from "node:path";
7: // Relative imports, not the @ alias: next.config imports the readers, which import this module.
8: import { weekHref } from "../routes";
9: import { parseVersioned } from "./published-file";
10: import { weekPageSchema } from "@cpc/week/schema/week";
11: import type { WeekPage, WeekSummary } from "@cpc/week/schema/week-types";
12: 
13: /* The build and the tests both run from the repo root, so public/ sits under the working folder. */
14: const PUBLIC_DIR = join(process.cwd(), "public");
15: const SEASON_DIR = /^\d{4}$/;
16: const WEEK_DIR = /^week-\d{2}$/;
17: 
18: /* The route params are the folder names, for example { season: "2026", week: "week-06" }. */
19: export type WeekRef = { season: string; week: string };
20: 
21: function dirsMatching(dir: string, pattern: RegExp): string[] {
22:   return readdirSync(dir, { withFileTypes: true })
23:     .filter((entry) => entry.isDirectory() && pattern.test(entry.name))
24:     .map((entry) => entry.name)
25:     .sort();
26: }
27: 
28: /* Every week folder that holds a page.json. A folder with only images is not a week page yet. */
29: export function listWeeks(): WeekRef[] {
30:   return dirsMatching(PUBLIC_DIR, SEASON_DIR).flatMap((season) =>
31:     dirsMatching(join(PUBLIC_DIR, season), WEEK_DIR)
32:       .filter((week) => existsSync(join(PUBLIC_DIR, season, week, "page.json")))
33:       .map((week) => ({ season, week })),
34:   );
35: }
36: 
37: /* The page JSON layout version this site reads. */
38: const SCHEMA_VERSION = 2;
39: 
40: /* A schema change must fail the build loud, so a page never renders from keys it misreads. */
41: export function loadWeek(season: string, week: string): WeekPage {
42:   // The version check runs first, so a layout change reads as a version error and not as a list of bad fields.
43:   return parseVersioned(join(PUBLIC_DIR, season, week, "page.json"), SCHEMA_VERSION, weekPageSchema);
44: }
45: 
46: /* Every published week, newest first. The sort reads the folder names as numbers, so week-10 follows week-09. */
47: export function listWeekSummaries(): WeekSummary[] {
48:   return listWeeks()
49:     .sort((a, b) => Number(b.season) - Number(a.season) || weekNumberOf(b.week) - weekNumberOf(a.week))
50:     .map(({ season, week }) => {
51:       const page = loadWeek(season, week);
52:       return {
53:         number: page.week,
54:         dates: page.dates,
55:         href: weekHref(season, week),
56:         pickTeams: [page.pick.sides[0].team.name, page.pick.sides[1].team.name] as [string, string],
57:       };
58:     });
59: }
60: 
61: /* The number in a folder name such as week-06. */
62: export function weekNumberOf(week: string): number {
63:   return Number(week.slice("week-".length));
64: }
```

## `apps/site/src/lib/data/week-data.test.ts` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 46–80

```text
46: describe("listWeekSummaries", () => {
47:   it("summarizes week 6 with its dates, its link, and the teams of its Matchup of the Week", () => {
48:     expect(listWeekSummaries()).toContainEqual({
49:       number: 6,
50:       dates: "Oct 15 – Oct 19, 2026",
51:       href: "/2026/week-06/",
52:       pickTeams: ["behold the lamb", "Bo Girds"],
53:     });
54:   });
55: 
56:   it("sorts the newest week first", () => {
57:     const numbers = listWeekSummaries().map((summary) => summary.number);
58:     expect(numbers).toEqual([...numbers].sort((a, b) => b - a));
59:   });
60: 
61:   it("sorts by season, then by week, as numbers", async () => {
62:     // A temp public/ folder holds weeks 2 and 10 of 2026 and week 1 of 2027.
63:     const root = mkdtempSync(join(tmpdir(), "week-data-"));
64:     for (const [season, week, number] of [
65:       ["2026", "week-02", 2],
66:       ["2026", "week-10", 10],
67:       ["2027", "week-01", 1],
68:     ] as const) {
69:       mkdirSync(join(root, "public", season, week), { recursive: true });
70:       writeFileSync(
71:         join(root, "public", season, week, "page.json"),
72:         weekPageJson({ week: number, dates: "d" }),
73:       );
74:     }
75:     vi.spyOn(process, "cwd").mockReturnValue(root);
76:     vi.resetModules();
77:     const { listWeekSummaries: list } = await import("./week-data");
78:     expect(list().map((summary) => summary.href)).toEqual(["/2027/week-01/", "/2026/week-10/", "/2026/week-02/"]);
79:   });
80: });
```

# T2 picker

The open effect focuses input:checked after the Change action. The test compares activeElement with the checked radio.

## `packages/analyzer/site/form/team-picker.tsx` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–122

```text
1: /**
2:  * A labelled list of teams as a radio group. Each row shows the avatar, the team name, and the manager.
3:  * The parent owns the choice, so two pickers can disable each other's pick. A pick collapses the list to that row.
4:  */
5: "use client";
6: 
7: import { AnimatePresence, motion } from "framer-motion";
8: import { useEffect, useRef, useState } from "react";
9: import type { Team } from "../lib/api";
10: import { Avatar } from "@cpc/league/avatar";
11: import { AVATAR_FALLBACK } from "@cpc/league/images";
12: import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
13: import { DURATION, EASE_OUT, INSTANT } from "@cpc/design/lib/motion";
14: import { cn } from "@cpc/design/lib/utils";
15: 
16: type TeamPickerProps = {
17:   // Also the name of the radio group, so two pickers on one page stay apart.
18:   label: string;
19:   teams: Team[];
20:   value: number | null;
21:   // The roster id that the other picker holds. This picker shows that row as disabled.
22:   disabledId: number | null;
23:   onChange: (rosterId: number) => void;
24:   // A grade runs, so every row and the Change button stay off until the grade ends.
25:   locked?: boolean;
26: };
27: 
28: export function TeamPicker({ label, teams, value, disabledId, onChange, locked = false }: TeamPickerProps) {
29:   // The list opens until a pick, then it collapses to the chosen row, so the form fits on a phone screen.
30:   const [open, setOpen] = useState(true);
31:   const off = useMotionOff();
32:   const fieldset = useRef<HTMLFieldSetElement>(null);
33:   // The Change button leaves the page when the list opens, so focus moves to the chosen radio instead of the body.
34:   const focusAfterOpen = useRef(false);
35:   const collapsed = value !== null && !open;
36:   const shown = collapsed ? teams.filter((team) => team.roster_id === value) : teams;
37: 
38:   useEffect(() => {
39:     if (!open || !focusAfterOpen.current) return;
40:     focusAfterOpen.current = false;
41:     fieldset.current?.querySelector<HTMLInputElement>("input:checked")?.focus();
42:   }, [open]);
43: 
44:   function pick(rosterId: number) {
45:     setOpen(false);
46:     onChange(rosterId);
47:   }
48: 
49:   function reopen() {
50:     focusAfterOpen.current = true;
51:     setOpen(true);
52:   }
53: 
54:   const rows = shown.map((team) => {
55:     const disabled = locked || team.roster_id === disabledId;
56:     return (
57:       <motion.div
58:         key={team.roster_id}
59:         initial={off ? false : { height: 0, opacity: 0 }}
60:         animate={{ height: "auto", opacity: 1 }}
61:         exit={{ height: 0, opacity: 0 }}
62:         transition={off ? INSTANT : { duration: DURATION.collapse, ease: EASE_OUT }}
63:         className="overflow-hidden"
64:       >
65:         {/* The gap lives inside the animated box, so a closing row takes its gap with it and nothing jumps at the end. */}
66:         <div className="pb-sp-1">
67:           <div
68:             className={cn(
69:               "group flex min-h-touch items-center rounded-card bg-card has-checked:bg-card-band has-checked:text-on-dark has-[input:focus-visible]:outline-2 has-[input:focus-visible]:outline-offset-2 has-[input:focus-visible]:outline-accent",
70:               disabled && "opacity-40",
71:             )}
72:           >
73:             <label
74:               aria-disabled={disabled || undefined}
75:               className={cn(
76:                 "flex min-h-touch min-w-0 flex-1 cursor-pointer items-center gap-sp-3 px-sp-3 py-sp-1",
77:                 disabled ? "cursor-not-allowed" : "press",
78:               )}
79:             >
80:               {/* The input is visually hidden, and the row shows the choice. The input stays in the page for the keyboard and for screen readers. */}
81:               <input
82:                 type="radio"
83:                 name={label}
84:                 value={team.roster_id}
85:                 checked={value === team.roster_id}
86:                 disabled={disabled}
87:                 onChange={() => pick(team.roster_id)}
88:                 className="sr-only"
89:               />
90:               <Avatar src={team.avatar ?? AVATAR_FALLBACK} className="flex-none rounded-full bg-page object-cover" />
91:               <span className="flex min-w-0 flex-col">
92:                 <b className="text-row leading-tight font-extrabold">{team.team}</b>
93:                 <span className="text-meta text-mute group-has-checked:text-on-dark-muted">{team.manager}</span>
94:               </span>
95:             </label>
96:             {collapsed && (
97:               <button
98:                 type="button"
99:                 onClick={reopen}
100:                 disabled={locked}
101:                 aria-label={`Change ${label.toLowerCase()}`}
102:                 className="press min-h-touch flex-none cursor-pointer rounded-card disabled:cursor-not-allowed px-sp-4 text-meta font-bold tracking-wide text-on-dark uppercase underline underline-offset-4"
103:               >
104:                 Change
105:               </button>
106:             )}
107:           </div>
108:         </div>
109:       </motion.div>
110:     );
111:   });
112: 
113:   return (
114:     <fieldset ref={fieldset} className="m-0 min-w-0 border-0 p-0">
115:       <legend className="mb-sp-2 p-0 text-meta font-bold tracking-wide text-accent-ink uppercase">{label}</legend>
116:       <div className="flex flex-col">
117:         {/* With motion off, the rows switch at once, with no exit to wait for. initial={false}: the full list shows at once on load. */}
118:         {off ? rows : <AnimatePresence initial={false}>{rows}</AnimatePresence>}
119:       </div>
120:     </fieldset>
121:   );
122: }
```

## `packages/analyzer/site/form/team-picker.test.tsx` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–52

```text
1: /**
2:  * Tests for the team picker avatar. A missing avatar and a failed avatar both show the default image.
3:  */
4: import { cleanup, fireEvent, render, screen } from "@testing-library/react";
5: import { useState } from "react";
6: import { afterEach, describe, expect, it } from "vitest";
7: import { AVATAR_FALLBACK } from "@cpc/league/images";
8: import type { Team } from "../lib/api";
9: import { TeamPicker } from "./team-picker";
10: 
11: const DEFAULT_SRC = AVATAR_FALLBACK;
12: 
13: function team(avatar: string | null): Team {
14:   return { roster_id: 1, team: "Gridiron Ghosts", manager: "Ana", avatar, players: [] };
15: }
16: 
17: function renderPicker(avatar: string | null) {
18:   const { container } = render(
19:     <TeamPicker label="My team" teams={[team(avatar)]} value={null} disabledId={null} onChange={() => {}} />,
20:   );
21:   return container.querySelector("img") as HTMLImageElement;
22: }
23: 
24: afterEach(cleanup);
25: 
26: describe("TeamPicker avatar", () => {
27:   it("renders the default avatar when the team has none", () => {
28:     expect(renderPicker(null).getAttribute("src")).toBe(DEFAULT_SRC);
29:   });
30: 
31:   it("swaps to the default avatar when a real avatar fails to load", () => {
32:     const img = renderPicker("https://cdn.test/a.png");
33:     expect(img.getAttribute("src")).toBe("https://cdn.test/a.png");
34:     fireEvent.error(img);
35:     expect(img.getAttribute("src")).toBe(DEFAULT_SRC);
36:   });
37: });
38: 
39: /* The parent owns the choice, so the test holds it in state like the trade form does. */
40: function ControlledPicker() {
41:   const [value, setValue] = useState<number | null>(null);
42:   return <TeamPicker label="My team" teams={[team(null)]} value={value} disabledId={null} onChange={setValue} />;
43: }
44: 
45: describe("TeamPicker focus", () => {
46:   it("moves focus to the checked radio after a click on Change my team", () => {
47:     render(<ControlledPicker />);
48:     fireEvent.click(screen.getByRole("radio"));
49:     fireEvent.click(screen.getByRole("button", { name: "Change my team" }));
50:     expect(document.activeElement).toBe(screen.getByRole("radio", { checked: true }));
51:   });
52: });
```

# T3 roster projection

The function builds points from week.rosters. The test adds a 30-point player and removes a 20-point player. Its total is 30.

## `packages/week/python/src/week/sheet/base.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 86–123

```text
86: def projected_totals(
87:     week: Week, client: Client, bye_weeks: dict[str, int] | None = None, through: int | None = None,
88: ) -> dict[int, dict[int, float]]:
89:     """The projected total of each roster's best lineup in each week ahead, by roster ID and week.
90: 
91:     The roster is the current roster in rosters.json. The lineup picks by that week's projections, so a player
92:     with no projection that week counts 0 and a healthy bench player takes his slot.
93:     An injured starter at zero gives his slot to the best pool player at the slot's positions, so the shift measures
94:     the real roster, not a hole. `bye_weeks` is the bye week of each NFL team, and a bye week gives no cover.
95:     A roster with no projected player in a week has no total that week.
96:     A missing week gives the roster no shift. It does not count as a total of 0.
97:     The weeks stop at the last regular week of `client`, because the file runs to the end of the NFL season for the
98:     waiver board.
99:     A playoff week in the totals would move the projected pace of the odds why.
100:     `through` sets another last week, such as the last bracket week for the season sim.
101:     """
102:     last = client.settings.last_regular_week if through is None else through
103:     totals: dict[int, dict[int, float]] = {rid: {} for rid in week.rosters}
104:     for w, projections in sorted(week.projections_ahead.items()):
105:         if w > last:
106:             continue
107:         # The pool players with a projection above zero that week, best first, with the player id as the tie rule.
108:         pool = sorted(
109:             ((pid, projections[pid], position) for pid, position in week.pool.items() if projections.get(pid, 0.0) > 0),
110:             key=lambda item: (-item[1], item[0]),
111:         )
112:         # The injury status is one snapshot for every week ahead. A player on his bye would be at zero healthy too, so
113:         # his bye week is no hole from the injury. With no schedule, no bye is known, so every injury counts.
114:         on_bye = {pid for pid, (_, team) in week.roster_players.items() if team and (bye_weeks or {}).get(team) == w}
115:         injuries = {pid: status for pid, status in week.injuries.items() if pid not in on_bye}
116:         for rid, positions in week.rosters.items():
117:             if not any(pid in projections for pid in positions):
118:                 continue
119:             points = {pid: projections.get(pid, 0.0) for pid in positions}
120:             slots = fill_slots(list(points), week.roster_positions, positions, points)
121:             starters = [pid for _, pid in slots if pid is not None]
122:             totals[rid][w] = sum(points[pid] for pid in starters) + _injury_cover(injuries, slots, points, pool)
123:     return totals
```

## `apps/pipeline/tests/test_sheet.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 700–709

```text
700: def test_the_projected_total_reads_the_current_roster_not_the_week_lineup(fixture_raw_dir):
701:     week = parse_week(load_raw(fixture_raw_dir))
702:     side = week.matchups[0].a
703:     dropped = side.lines[0].player_id
704:     # A player added after the lock is on the roster but not in the week's lines. A dropped player is the reverse.
705:     rosters = {**week.rosters, side.roster_id: {"added": "RB", **{
706:         pid: pos for pid, pos in week.rosters[side.roster_id].items() if pid != dropped}}}
707:     totals = projected_totals(week.model_copy(update={
708:         "rosters": rosters, "projections_ahead": {7: {"added": 30.0, dropped: 20.0}}}), client=CLIENT)
709:     assert totals[side.roster_id] == {7: 30.0}
```

# T4 publish

The publish calls stage and commit explicit season paths. Tests retain stray, other-season, and nonseason client files outside the commit.

## `apps/pipeline/src/cornerstone/publish.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 33–122

```text
33: def _git(cwd: Path, *args: str, ok: tuple[int, ...] = (0,)) -> int:
34:     result = subprocess.run(["git", *args], cwd=cwd, check=False, capture_output=True, text=True)
35:     if result.returncode not in ok:
36:         raise PublishError(f"git {' '.join(args)} failed in {cwd}: {result.stderr.strip() or result.stdout.strip()}")
37:     return result.returncode
38: 
39: 
40: def _commit_if_staged(cwd: Path, message: str, *paths: str) -> None:
41:     # Ask git about staged changes instead of matching its message text. The message differs
42:     # when other untracked files exist, and a retry of a failed push must not stop here.
43:     if _git(cwd, "diff", "--cached", "--quiet", "--", *paths, ok=(0, 1)) == 0:
44:         return
45:     # The pathspec keeps any other staged change out of this commit.
46:     _git(cwd, "commit", "-m", message, "--", *paths)
47: 
48: 
49: def _push(site_repo: Path) -> None:
50:     # Why: the site deploys from the remote, so a publish puts its page live only with this push. ADR 0019
51:     # allows the push to main because each publish stages only the season folders of its client.
52:     _git(site_repo, "push")
53: 
54: 
55: def _repo_root(repo: Path) -> Path:
56:     # Why: the pipeline and the site live in one repo, so the site is the root of the pipeline's own
57:     # checkout. A fixed path to a second checkout breaks in a worktree and on any other machine.
58:     result = subprocess.run(
59:         ["git", "rev-parse", "--show-toplevel"], cwd=repo, check=False, capture_output=True, text=True
60:     )
61:     if result.returncode != 0:
62:         raise PublishError(f"{repo} is not in a git checkout: {result.stderr.strip()}")
63:     return Path(result.stdout.strip())
64: 
65: 
66: def run_publish(
67:         repo: Path, season: int, week: int, slug: str, folder: Path, site_repo: Path | None = None,
68:         push: bool = True) -> str:
69:     """Publish one week of the client `slug`. `folder` is the client folder, which holds its build folder and its
70:     data. The site repo is the root of the pipeline's checkout, unless a test names another."""
71:     build = build_dir(folder)
72:     data = folder / "data"
73:     page = site_week_dir(build, season, week) / "page.json"
74:     if not page.exists():
75:         raise PublishError(f"{page} does not exist. Build the week first.")
76:     if site_repo is None:
77:         site_repo = _repo_root(repo)
78:     # Check the site repo before the first commit, so a bad path leaves no half-done publish.
79:     if not (site_repo / ".git").exists():
80:         raise PublishError(f"{site_repo} is not a git checkout.")
81: 
82:     # Why: ADR 0019 lets the publish stage only the season folders of the client. The build folder holds the season
83:     # files that the next build reads, and the API image seeds from the data folder, so both go into the report commit.
84:     # A season folder with no files yet has nothing to stage.
85:     report = [str(path) for path in (season_dir(build, season), season_dir(data, season)) if path.exists()]
86:     _git(folder, "add", "--", *report)
87:     _commit_if_staged(folder, f"Week {week} report", *report)
88: 
89:     # Copy only this week: its page.json, avatars, and headshots. A built but unpublished week must
90:     # stay off the public site. The site is a Next.js app. It renders the pages and the home
91:     # page from these folders.
92:     # Why: each client keeps its data in its own folder, and the site build copies only that client's published data.
93:     public_dir = site_repo / "clients" / slug / "published"
94:     week_path = Path(str(season)) / week_label(week)
95:     shutil.copytree(
96:         build / week_path, public_dir / week_path, dirs_exist_ok=True
97:     )
98:     # The season file holds every week to date, so it goes out with the week in the same commit.
99:     rankings = season_dir(build, season) / "rankings.json"
100:     if rankings.exists():
101:         shutil.copy2(rankings, public_dir / str(season) / "rankings.json")
102:     else:
103:         log.warning("%s missing: the publish goes out without rankings.json", rankings)
104:     # The managers file is a season file too. A thin history has none, so a missing file only warns.
105:     managers = season_dir(build, season) / "managers.json"
106:     if managers.exists():
107:         shutil.copy2(managers, public_dir / str(season) / "managers.json")
108:     else:
109:         log.warning("%s missing: the publish goes out without managers.json", managers)
110:     # Why: the repo holds code and notes too. Staging the season folder of the client only keeps a stray change
111:     # elsewhere in the tree out of the commit. ADR 0019 allows the push to main on this one condition.
112:     published = str((public_dir / str(season)).relative_to(site_repo))
113:     _git(site_repo, "add", "--", published)
114:     _commit_if_staged(site_repo, f"Week {week}", published)
115:     if push:
116:         _push(site_repo)
117:     return site_page_url(slug, season, week)
118: 
119: 
120: # The two season files of the midseason report. The report ends on the sim replay, so the two go live together. The
121: # app names the sim file, because the midseason package never imports sim.
122: MIDSEASON_FILES = (MIDSEASON_FILE, SIM_FILE)
```

## `apps/pipeline/tests/test_rule_publish.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–122

```text
1: """
2: Checks that a publish commit holds only files under the season folders of the client: published/, data/, and build/.
3: It builds a real git repo in a temp folder and runs the real publish. See ADR 0019.
4: """
5: import subprocess
6: from pathlib import Path
7: 
8: from rule_report import Offense, clean_git_env, report
9: 
10: from cornerstone.publish import run_publish
11: 
12: ADR = "docs/adr/0019-main-is-the-record-branch.md"
13: # The three season folders of the client that a publish may stage. The API image seeds from the data folder.
14: ALLOWED = ("clients/cpc/published/2026/", "clients/cpc/data/2026/", "clients/cpc/build/2026/")
15: RULE = "a publish commit stages only files under clients/<slug>/published/, data/, or build/ of the season"
16: FIX = "unstage the file, and commit it on a branch outside the publish."
17: 
18: 
19: def _git(cwd: Path, *args: str) -> str:
20:     return subprocess.run(
21:         ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=clean_git_env()
22:     ).stdout
23: 
24: 
25: def _commit_paths(root: Path, commit: str) -> list[str]:
26:     return _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", commit).splitlines()
27: 
28: 
29: def _outside_offenses(root: Path, commit: str) -> list[Offense]:
30:     """Each path of the commit outside the season folders of the client. The line is 1, because a path has no line."""
31:     return [Offense(
32:         path=path,
33:         line=1,
34:         rule_id="publish/scope",
35:         what="The publish commit holds a file outside the season folders of the client.",
36:         rule=RULE,
37:         adr=ADR,
38:         fix=FIX,
39:     ) for path in _commit_paths(root, commit) if not path.startswith(ALLOWED)]
40: 
41: 
42: def _publish_offenses(root: Path) -> list[Offense]:
43:     """The offenses of each commit of the publish: the report commit and the week commit."""
44:     commits = _git(root, "rev-list", "HEAD").split()
45:     return [offense for commit in commits for offense in _outside_offenses(root, commit)]
46: 
47: 
48: def _built_repo(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
49:     """A git repo with the pipeline at apps/pipeline and one built week 8 page in the build folder of cpc.
50: 
51:     The prek hook sets GIT_DIR. The publish calls git with the process env, so the test clears it.
52:     """
53:     for name in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE"):
54:         monkeypatch.delenv(name, raising=False)
55:     root = tmp_path / "one"
56:     pipeline = root / "apps" / "pipeline"
57:     pipeline.mkdir(parents=True)
58:     page = root / "clients" / "cpc" / "build" / "2026" / "week-08" / "page.json"
59:     page.parent.mkdir(parents=True)
60:     page.write_text("{}")
61:     raw = root / "clients" / "cpc" / "data" / "2026" / "week-08" / "raw"
62:     raw.mkdir(parents=True)
63:     (raw / "league.json").write_text("{}")
64:     _git(root, "init", "-b", "main")
65:     _git(root, "config", "user.email", "test@example.com")
66:     _git(root, "config", "user.name", "Test")
67:     return root, pipeline
68: 
69: 
70: def test_a_publish_stages_only_the_season_folders_of_the_client(tmp_path, monkeypatch):
71:     root, pipeline = _built_repo(tmp_path, monkeypatch)
72:     run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc", push=False)
73:     offenses = _publish_offenses(root)
74:     assert not offenses, report(offenses)
75:     assert _commit_paths(root, "HEAD") == ["clients/cpc/published/2026/week-08/page.json"]
76:     assert _commit_paths(root, "HEAD~1") == [
77:         "clients/cpc/build/2026/week-08/page.json", "clients/cpc/data/2026/week-08/raw/league.json",
78:     ]
79: 
80: 
81: def test_a_stray_file_stays_out_of_the_publish(tmp_path, monkeypatch):
82:     root, pipeline = _built_repo(tmp_path, monkeypatch)
83:     (root / "stray.txt").write_text("half-done work\n")
84:     run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc", push=False)
85:     assert _git(root, "status", "--short", "--", "stray.txt").strip() == "?? stray.txt"
86:     assert _publish_offenses(root) == []
87: 
88: 
89: def test_a_change_to_another_season_stays_out_of_the_publish(tmp_path, monkeypatch):
90:     root, pipeline = _built_repo(tmp_path, monkeypatch)
91:     for folder in ("published", "data", "build"):
92:         old = root / "clients" / "cpc" / folder / "2025" / "rankings.json"
93:         old.parent.mkdir(parents=True)
94:         old.write_text("{}")
95:     run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc", push=False)
96:     assert _publish_offenses(root) == []
97:     for folder in ("published", "data", "build"):
98:         status = _git(root, "status", "--short", "--", f"clients/cpc/{folder}/2025").strip()
99:         assert status == f"?? clients/cpc/{folder}/2025/"
100: 
101: 
102: def test_a_file_of_the_client_outside_the_season_folders_stays_out_of_the_publish(tmp_path, monkeypatch):
103:     root, pipeline = _built_repo(tmp_path, monkeypatch)
104:     (root / "clients" / "cpc" / "data" / "notes.json").write_text("{}")
105:     run_publish(pipeline, 2026, 8, "cpc", root / "clients" / "cpc", push=False)
106:     assert _publish_offenses(root) == []
107:     assert _git(root, "status", "--short", "--", "clients/cpc/data/notes.json").strip() == "?? clients/cpc/data/notes.json"
108: 
109: 
110: def test_the_rule_names_a_file_outside_the_season_folders(tmp_path, monkeypatch):
111:     root, _ = _built_repo(tmp_path, monkeypatch)
112:     (root / "stray.txt").write_text("half-done work\n")
113:     (root / "clients" / "cpc" / "client.toml").write_text("")
114:     _git(root, "add", "-A")
115:     _git(root, "commit", "-m", "Week 8")
116:     offenses = _outside_offenses(root, "HEAD")
117:     assert [(offense.path, offense.rule_id) for offense in offenses] == [
118:         ("clients/cpc/client.toml", "publish/scope"),
119:         ("stray.txt", "publish/scope"),
120:     ]
121:     assert "stray.txt" in report(offenses)
122:     assert ADR in report(offenses)
```

# T5 answer caps

The SQL query filters roster_id and the date of now. Yesterday’s team receives free; today’s other team receives cap.

## `apps/api/src/cornerstone_api/caps.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 82–145

```text
82: class Caps:
83:     """The spend of one client in one SQLite file. Each call opens its own connection, so the threads of the API never
84:     share one. A lock makes the sum and the alert of `record` one step, so two answers at once log one alert."""
85: 
86:     def __init__(self, path: Path, slug: str) -> None:
87:         self.path = path
88:         self.slug = slug
89:         self._lock = threading.Lock()
90:         path.parent.mkdir(parents=True, exist_ok=True)
91:         with self._connect() as db:
92:             db.executescript(SCHEMA)
93: 
94:     @contextmanager
95:     def _connect(self) -> Iterator[sqlite3.Connection]:
96:         db = sqlite3.connect(self.path)
97:         try:
98:             with db:
99:                 yield db
100:         finally:
101:             db.close()
102: 
103:     def answers_today(self, roster_id: int, now: datetime) -> int:
104:         """The Claude Answers of the team today, in the timezone of `now`."""
105:         with self._connect() as db:
106:             row = db.execute("SELECT COUNT(*) FROM spend WHERE roster_id = ? AND day = ? AND counts = 1",
107:                              (roster_id, now.date().isoformat())).fetchone()
108:         return int(row[0])
109: 
110:     def month_usd(self, now: datetime) -> float:
111:         """The Claude cost of the league in the month of `now`."""
112:         with self._connect() as db:
113:             row = db.execute("SELECT COALESCE(SUM(usd), 0) FROM spend WHERE month = ?", (_month(now),)).fetchone()
114:         return float(row[0])
115: 
116:     def check(self, roster_id: int, now: datetime) -> CapHit | None:
117:         """The cap that stops a new Claude Answer of the team, or None. Ask it before each Claude call.
118: 
119:         The league cap comes first, because it lasts longer and its line says when it ends.
120:         """
121:         if self.month_usd(now) >= LEAGUE_USD_PER_MONTH:
122:             when = _next_month(now)
123:             return CapHit("league", LEAGUE_LINE.format(date=f"{when:%b} {when.day}"))
124:         if self.answers_today(roster_id, now) >= TEAM_ANSWERS_PER_DAY:
125:             return CapHit("team", TEAM_LINE)
126:         return None
127: 
128:     def record(self, roster_id: int | None, usd: float, now: datetime, *, counts: bool) -> None:
129:         """Add the Claude cost of one call site to the league month. With `counts`, it is one Answer of the team.
130: 
131:         A kept Answer makes no call and records nothing. An honest miss, a failed call, and the head start record their
132:         cost with `counts` False. The first record past ALERT_SHARE of the month logs the one alert of the month.
133:         """
134:         month = _month(now)
135:         with self._lock, self._connect() as db:
136:             previous = _month(datetime(now.year - 1, 12, 1) if now.month == 1 else datetime(now.year, now.month - 1, 1))
137:             db.execute("DELETE FROM spend WHERE month < ?", (previous,))
138:             db.execute("INSERT INTO spend (roster_id, day, month, usd, counts) VALUES (?, ?, ?, ?, ?)",
139:                        (roster_id, now.date().isoformat(), month, usd, int(counts)))
140:             total = float(db.execute("SELECT SUM(usd) FROM spend WHERE month = ?", (month,)).fetchone()[0])
141:             if total < ALERT_SHARE * LEAGUE_USD_PER_MONTH:
142:                 return
143:             if db.execute("INSERT OR IGNORE INTO alerts (month) VALUES (?)", (month,)).rowcount == 1:
144:                 logger.warning("The league %s used $%.2f of its $%.2f Claude budget for %s, past 80%%.",
145:                                self.slug, total, LEAGUE_USD_PER_MONTH, month)
```

## `apps/api/tests/test_caps.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 18–43

```text
18:     _chunks,
19:     _leader,
20: )
21: 
22: from cornerstone_api.caps import LEAGUE_LINE, TEAM_LINE, Caps
23: 
24: # The fixture of the free answer tests: a repo with the saved weeks 1 to 5 of the recorded season.
25: repo = test_free_answer.repo
26: 
27: ASK = "/clients/cpc/ask"
28: LIL_FRIDGE = 3
29: BO_GIRDS = 6
30: QUESTION = "highest scoring team this season"
31: # The words that cap copy never holds: no manager, and no internal name (the copy rules of the spec).
32: INNER_NAMES = ("jev", "advisor", "finder", "rival", "brian")
33: 
34: 
35: def _route(api, question: str = QUESTION, roster_id: int = LIL_FRIDGE):
36:     return api.post(ASK, json={"question": question, "roster_id": roster_id, "week": 8}, headers=PASS)
37: 
38: 
39: def _fill_team(caps: Caps, roster_id: int, count: int, now: datetime = NOW) -> None:
40:     for _ in range(count):
41:         caps.record(roster_id, 0.01, now, counts=True)
42: 
43: 
```

## `apps/api/tests/test_caps.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 90–95

```text
90: def test_the_team_cap_is_per_team_and_starts_again_the_next_day(repo, fixture_raw_dir):
91:     api, _, caps = _setup(repo, fixture_raw_dir)
92:     _fill_team(caps, LIL_FRIDGE, 25, NOW - timedelta(days=1))
93:     _fill_team(caps, BO_GIRDS, 25)
94:     assert _route(api).json()["route"] == "free"
95:     assert _route(api, roster_id=BO_GIRDS).json()["route"] == "cap"
```

# T6 grade limits

GradeLimiter reads and writes daily counts through its path. The test creates another client, receives 429, then receives 200 tomorrow.

## `packages/analyzer/python/src/analyzer/ratelimit.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 80–165

```text
80: class GradeLimiter:
81:     """Count the grades of each address in a one-minute window and in a calendar day in the league timezone.
82: 
83:     The minute window lives in memory. The day counts live in a JSON file, so a restart or a deploy keeps them.
84:     The file holds only today: {"day": "2026-10-19", "counts": {"<address>": <grades>}}.
85:     """
86: 
87:     def __init__(self, per_minute: int, per_day: int, path: Path, tz: ZoneInfo,
88:                  clock: Callable[[], datetime] | None = None) -> None:
89:         self.per_day = per_day
90:         self.path = path
91:         self.tz = tz
92:         # An aware datetime, so the day is the calendar day in the league timezone wherever the host runs.
93:         self.clock = clock or (lambda: datetime.now(tz))
94:         self.minute = RateLimiter(per_minute, clock=lambda: self.clock().timestamp())
95:         # FastAPI runs the sync route in a thread pool. Without the lock, two grades at once both read N and both
96:         # write N+1, so one grade goes uncounted. The lock covers the minute check too, for the same reason.
97:         self.lock = threading.Lock()
98:         # The counts of today in this process. When a write fails, these keep the count until the process ends.
99:         self.day = ""
100:         self.counts: dict[str, int] = {}
101: 
102:     def hit(self, address: str) -> GradeLimited | None:
103:         """Count one grade. Return None when it is within both limits, else the full window and its retry-after."""
104:         with self.lock:
105:             now = self.clock().astimezone(self.tz)
106:             today = now.date().isoformat()
107:             counts = self._read(today)
108:             if self.day == today:
109:                 # A failed write leaves the file behind the memory, so the larger count of the two stands.
110:                 counts = {a: max(counts.get(a, 0), self.counts.get(a, 0)) for a in counts.keys() | self.counts.keys()}
111:             # The day comes first, so a full day says "tomorrow" and not "next minute".
112:             if counts.get(address, 0) >= self.per_day:
113:                 return GradeLimited("day", seconds_to_midnight(now))
114:             retry_after = self.minute.hit(address)
115:             if retry_after is not None:
116:                 return GradeLimited("minute", retry_after)
117:             counts[address] = counts.get(address, 0) + 1
118:             self.day, self.counts = today, counts
119:             try:
120:                 self._write(today, counts)
121:             except OSError as error:
122:                 # A full or read-only volume must not stop the grade. The count stays in memory for this process.
123:                 logger.warning("The grade count file %s is not writable, so the count stays in memory: %s",
124:                                self.path, error)
125:             return None
126: 
127:     def release(self, address: str) -> None:
128:         """Take back one grade of the address, in the minute window and in the day count. A failed read calls it.
129: 
130:         A count already at zero stays at zero, so a release never gives an address more grades than the limit.
131:         """
132:         with self.lock:
133:             now = self.clock().astimezone(self.tz)
134:             today = now.date().isoformat()
135:             counts = self._read(today)
136:             if self.day == today:
137:                 counts = {a: max(counts.get(a, 0), self.counts.get(a, 0)) for a in counts.keys() | self.counts.keys()}
138:             counts[address] = max(0, counts.get(address, 0) - 1)
139:             start, count = self.minute.windows.get(address, (now.timestamp(), 0))
140:             self.minute.windows[address] = (start, max(0, count - 1))
141:             self.day, self.counts = today, counts
142:             try:
143:                 self._write(today, counts)
144:             except OSError as error:
145:                 logger.warning("The grade count file %s is not writable, so the count stays in memory: %s",
146:                                self.path, error)
147: 
148:     def _read(self, today: str) -> dict[str, int]:
149:         """The counts of today from the file. A missing, malformed, or older file starts at zero."""
150:         try:
151:             data = json.loads(self.path.read_text())
152:             if data.get("day") != today:
153:                 return {}
154:             return {str(a): int(n) for a, n in data["counts"].items()}
155:         except FileNotFoundError:
156:             return {}
157:         except (OSError, ValueError, TypeError, AttributeError, KeyError):
158:             logger.warning("The grade count file %s is not readable, so the counts start at zero", self.path)
159:             return {}
160: 
161:     def _write(self, today: str, counts: dict[str, int]) -> None:
162:         """Write only today, so the file never grows past one day of addresses."""
163:         self.path.parent.mkdir(parents=True, exist_ok=True)
164:         body = json.dumps({"day": today, "counts": counts}, sort_keys=True).encode("utf-8")
165:         write_bytes_atomic(self.path, body)
```

## `apps/api/tests/test_api.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 195–199

```text
195: def _client(settings, sources, analyzer=None):
196:     app = create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), analyzer=analyzer)
197:     if analyzer is not None and not getattr(analyzer, "store", True):
198:         _drop_store(app)
199:     return TestClient(app)
```

## `apps/api/tests/test_api.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1104–1110

```text
1104: def _graded_client(settings, sources, clock, analyzer):
1105:     """A client whose grade limit and general limit both read the moving clock."""
1106:     client = _client(settings, sources, analyzer)
1107:     client.app.state.served["cpc"].grade_limiter.clock = clock
1108:     # The general limit reads the same clock, so a test can make more than its 30 requests in one real minute.
1109:     client.app.state.limiter.clock = lambda: clock().timestamp()
1110:     return client
```

## `apps/api/tests/test_api.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1113–1115

```text
1113: def _uncached():
1114:     """An analyzer whose app keeps no result, so each repeat is a new grade."""
1115:     return StubAnalyzer(store=False)
```

## `apps/api/tests/test_api.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1132–1152

```text
1132: def test_the_twenty_first_grade_in_a_day_is_429_across_a_restart(settings, sources):
1133:     from analyzer.tunables import GRADES_PER_DAY
1134: 
1135:     clock = MovingClock(NOW)
1136:     first = _graded_client(settings, sources, clock, _uncached())
1137:     for _ in range(GRADES_PER_DAY):
1138:         # Past the minute window each time, so only the day limit can stop a grade.
1139:         clock.advance(seconds=61)
1140:         assert first.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
1141:     clock.advance(seconds=61)
1142:     restarted = _graded_client(settings, sources, clock, _uncached())
1143:     response = restarted.post("/analyze", json=TRADE, headers=HEADERS)
1144:     assert response.status_code == 429
1145:     assert response.json() == {"detail": "Too many grades today. Try again tomorrow."}
1146:     retry_after = int(response.headers["Retry-After"])
1147:     assert 1 <= retry_after <= 86400
1148:     midnight = datetime(2026, 10, 20, 0, 0, tzinfo=ET)
1149:     assert retry_after == math.ceil((midnight - clock()).total_seconds())
1150:     # The next calendar day in Eastern time starts at zero.
1151:     clock.now = midnight
1152:     assert restarted.post("/analyze", json=TRADE, headers=HEADERS).status_code == 200
```

