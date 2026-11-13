# Static evidence reproduction

Run these four commands in order from the spec root with Python 3 and Git available.
They use the fixed implementation Git objects and write only the feature evidence.
The second command attaches the exact rule logs and removes the first command’s temporary rule-output placeholder.
Preserve later background-check completion records before a fresh capture.
The commands do not execute any dependency tool, test suite, or cold task trial.
The absolute ROOT identifies the original spec worktree; change it only when the checkout path changes.

The original /tmp capture inputs must exist.
The evidence archive preserves both probes’ stdout and stderr, plus the three rule logs.
It also preserves the full-check launch metadata as background-check-start.json.
Restore those inputs to their recorded /tmp paths if the originals no longer exist.
The generator records a fresh capture time but retains the fixed source revision.

## Fixed-source capture

```sh
python3 - <<'PY_CAPTURE'
"""Capture README navigation evidence from fixed Git objects.
Keep document observations separate from unrun agent trials.
"""
from pathlib import Path
import ast, datetime, hashlib, json, posixpath, re, shutil, subprocess
ROOT=Path('/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation')
OUT=ROOT/'.scratch/readme-module-navigation/evidence'
SHA='dad744db4f3b49732adc1586e08c34be2f381f73'
BASE='17f45a15d1c324e36beefd0da29b77fe56b7ef91'
DOCS=['CLAUDE.md','apps/site/CLAUDE.md','apps/pipeline/CLAUDE.md','apps/site/README.md','apps/pipeline/README.md','apps/api/README.md','apps/site/src/lib/data/README.md','apps/pipeline/src/cornerstone/README.md','apps/api/src/cornerstone_api/README.md','packages/analyzer/README.md','packages/analyzer/site/form/README.md','packages/week/README.md','packages/week/python/src/week/sheet/README.md']
READ=set()
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True)
def source(path,rev=SHA):
    READ.add(path)
    return git('show',f'{rev}:{path}')
def put(path,text):
    path=OUT/path; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text)
def numbered(path,rev=SHA,start=1,end=None):
    lines=source(path,rev).splitlines(); end=len(lines) if end is None else end
    return f'## `{path}` at `{rev}`; lines {start}–{end}\n\n```text\n'+''.join(f'{i}: {s}\n' for i,s in enumerate(lines,1) if start<=i<=end)+'```\n\n'
def functions(path,names):
    text=source(path); tree=ast.parse(text); result=''
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names: result+=numbered(path,start=node.lineno,end=node.end_lineno)
    return result
HEADER=f'Implementation revision: `{SHA}`.\nBase revision: `{BASE}`.\nAll source excerpts below come from Git objects at the stated revision.\nNo behavior test or cold task runs during this static capture.\n\n'
files=set(git('ls-tree','-r','--name-only',SHA).splitlines())
def links(paths):
    out='| Source | Line | Relative target | Resolved repository target | Exists at revision |\n| --- | --- | --- | --- | --- |\n'
    for path in paths:
        for line,text in enumerate(source(path).splitlines(),1):
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
                if '://' in target or target.startswith('#'): continue
                resolved=posixpath.normpath(posixpath.join(posixpath.dirname(path),target.split('#')[0]))
                exists=resolved.rstrip('/') in files or any(f.startswith(resolved.rstrip('/')+'/') for f in files)
                out+=f'| `{path}` | {line} | `{target}` | `{resolved}` | {str(exists).lower()} |\n'
    return out
put(Path('AT-1/entry-links.md'),HEADER+''.join(numbered(p) for p in DOCS[:3])+links(DOCS[:3]))
put(Path('AT-2/app-maps.md'),HEADER+''.join(numbered(p) for p in DOCS[3:6])+links(DOCS[3:6]))
put(Path('AT-3/owner-maps.md'),HEADER+''.join(numbered(p) for p in DOCS[6:])+links(DOCS[6:]))
sections=[('T1 archive',numbered('apps/site/src/lib/data/week-data.ts')+numbered('apps/site/src/lib/data/week-data.test.ts',start=46)),('T2 picker',numbered('packages/analyzer/site/form/team-picker.tsx')+numbered('packages/analyzer/site/form/team-picker.test.tsx')),('T3 roster projection',functions('packages/week/python/src/week/sheet/base.py',{'projected_totals'})+functions('apps/pipeline/tests/test_sheet.py',{'test_the_projected_total_reads_the_current_roster_not_the_week_lineup'})),('T4 publish',numbered('apps/pipeline/src/cornerstone/publish.py',start=33,end=122)+numbered('apps/pipeline/tests/test_rule_publish.py')),('T5 answer caps',functions('apps/api/src/cornerstone_api/caps.py',{'Caps'})+numbered('apps/api/tests/test_caps.py',start=18,end=43)+functions('apps/api/tests/test_caps.py',{'test_the_team_cap_is_per_team_and_starts_again_the_next_day'})),('T6 grade limits',functions('packages/analyzer/python/src/analyzer/ratelimit.py',{'GradeLimiter'})+functions('apps/api/tests/test_api.py',{'_client', '_graded_client', '_uncached', 'test_the_twenty_first_grade_in_a_day_is_429_across_a_restart'}))]
observations=['The comparator orders numeric seasons descending, then numeric weeks descending. The assertion places 2027/01 before 2026/10 before 2026/02.','The open effect focuses input:checked after the Change action. The test compares activeElement with the checked radio.','The function builds points from week.rosters. The test adds a 30-point player and removes a 20-point player. Its total is 30.','The publish calls stage and commit explicit season paths. Tests retain stray, other-season, and nonseason client files outside the commit.','The SQL query filters roster_id and the date of now. Yesterday’s team receives free; today’s other team receives cap.','GradeLimiter reads and writes daily counts through its path. The test creates another client, receives 429, then receives 200 tomorrow.']
put(Path('AT-3/module-test-responsibilities.md'),HEADER+''.join(f'# {name}\n\n{obs}\n\n{body}' for (name,body),obs in zip(sections,observations)))
shape=HEADER+'Counts use splitlines(); each blank physical line counts. Each file ends with a newline.\n\n| Document | Physical lines | Headings in order | Extra heading |\n| --- | --- | --- | --- |\n'
for p in DOCS[6:]:
    lines=source(p).splitlines(); headings=[x for x in lines if x.startswith('#')]
    shape+=f'| `{p}` | {len(lines)} | '+ ' → '.join(headings)+' | none |\n'
    assert len(lines)<=24 and headings[0].startswith('# ') and headings[1:]==['## Knows','## Ports','## Does not do']
shape+='\nD13 receives this explicit check. Existing rules do not traverse nested package Python folders.\nTest pointers remain within Knows; no separate test heading exists.\n\n'+''.join(numbered(p) for p in DOCS[6:])
put(Path('AT-4/owner-shape.md'),shape)
RULES=['apps/site/src/readme-rule.test.ts','apps/pipeline/tests/test_rule_readmes.py','apps/api/tests/test_rule_api.py']
put(Path('AT-4/existing-rule-sources.md'),HEADER+''.join(numbered(p) for p in RULES)+'Rule source diff, base to implementation:\n\n```diff\n'+git('diff',BASE,SHA,'--',*RULES)+'```\n')
put(Path('AT-4/rule-output.md'),HEADER+'Exact README-rule commands and output await the orchestrator’s capture.\nOld /tmp/readme-ticket01-*-rules.log files lack command and revision metadata.\nThose logs do not establish the required fixed-revision run and are not used here.\n')
preservation=HEADER+'The app instruction diffs add only each app README pointer. Existing command and rule sections remain byte-for-byte.\nThe root Where the work sits section still requires state, then one ticket.\nThe cold-trial exception appears in the approved procedure only.\n\n'
for p in DOCS:
    if p in files:
        exists=subprocess.run(['git','cat-file','-e',f'{BASE}:{p}'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        preservation+=f'# Before and after: `{p}`\n\n'
        preservation+=numbered(p,BASE) if exists else 'The base has no such document.\n\n'
        preservation+=numbered(p)
procedure='.scratch/readme-module-navigation/decisions/03-grill-cold-agent-test-procedure.md'
preservation+=numbered(procedure,start=17,end=29)
put(Path('AT-5/document-duties.md'),preservation)
api=HEADER+numbered('CLAUDE.md',start=1,end=13)+numbered('apps/api/README.md')+'## Root diff\n\n```diff\n'+git('diff',BASE,SHA,'--','CLAUDE.md')+'```\n\n'+numbered('apps/api/pyproject.toml')+numbered('apps/api/tests/test_rule_api.py')
imports=[]
for p in sorted(files):
    if p.startswith('apps/api/src/') and p.endswith('.py'):
        text=source(p)
        for node in ast.walk(ast.parse(text)):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                imports.append((p,node.lineno,ast.get_source_segment(text,node)))
api+='## Complete static API product import inventory\n\nPython AST import statements from all tracked apps/api/src/**/*.py files follow.\nThis static inventory does not execute imports. No statement imports cornerstone or pipeline.\nTest helpers belong to apps/api/tests; pyproject lists cornerstone only in the dev dependency group.\nThe uv source map declares resolution; it does not add a product dependency.\n\n```text\n'+''.join(f'{p}:{n}: {s}\n' for p,n,s in imports)+'```\n'
put(Path('AT-6/api-dependencies.md'),api)
changes=git('diff','--name-status',BASE,SHA)
product=git('diff','--no-ext-diff','--binary',BASE,SHA,'--',*DOCS)
put(Path('AT-16/product.diff'),product)
roles=['root entry, all tasks','site entry, T1 and T2','pipeline entry, T3 and T4','site map, T1 and T2','pipeline map, T3 and T4','API map, T5 and T6','archive, T1','publish, T4','answer caps, T5; grade boundary, T6','form, T2; grade limits, T6','picker, T2','sheet and odds boundary, T3','current roster, T3']
scope=HEADER+'## Approved product inventory\n\n| ID | Path | Route |\n| --- | --- | --- |\n'+''.join(f'| D{i} | `{p}` | {r} |\n' for i,(p,r) in enumerate(zip(DOCS,roles),1))
scope+='\n## Complete changed-file list at fixed revision\n\n```text\n'+changes+'```\n\n## Classification\n\nProduct documents are exactly D1 through D13.\nFeature tracker records are .scratch/readme-module-navigation/* and docs/agents/state.md.\nEvidence records do not exist in the fixed implementation commit.\nThis capture adds only EVIDENCE.md and evidence/ beneath the feature tracker.\nThe full product diff is product.diff. The full feature diff is ../AT-17/feature.diff.\n'
put(Path('AT-16/document-scope.md'),scope)
put(Path('AT-17/feature.diff'),git('diff','--no-ext-diff','--binary',BASE,SHA))
historical='.scratch/week-8-fixes/issues/07-the-readmes-name-the-module-an-agent-needs.md'
excluded=HEADER+'The complete changed-file list is ../AT-16/document-scope.md. feature.diff contains the full feature diff.\nEvery changed path in the fixed implementation diff is Markdown. No module move, product code, test code, schema, or API contract file changes.\nThe product maps group responsibilities; they contain no T1–T6 answer table or exhaustive package catalogue.\nThe full 13 document snapshots appear in ../AT-5/document-duties.md for direct inspection.\nNo root README or separate API instruction file enters the diff.\nProvider-refresh, saved-data, prompt-test, fact-selection, and build-behavior gaps receive no feature edit.\nThe current-roster projection route addresses one historical gap; it does not complete historical ticket 07.\n\n## Historical ticket at implementation\n\n'+numbered(historical)+'## Historical ticket diff\n\n```diff\n'+git('diff',BASE,SHA,'--',historical)+'```\n\n## Deferred scope decision\n\n'+numbered('.scratch/readme-module-navigation/decisions/02-grill-readme-coverage-and-structure.md',start=72,end=81)
put(Path('AT-17/excluded-scope.md'),excluded)
checks=[]
for p in DOCS:
    expected=source(p).encode(); actual=(ROOT/p).read_bytes(); assert expected==actual,p
    checks.append({'path':p,'worktree_matches_implementation':True,'git_blob':git('rev-parse',f'{SHA}:{p}').strip(),'sha256':hashlib.sha256(actual).hexdigest()})
put(Path('snapshot.json'),json.dumps({'implementation':SHA,'base':BASE,'capture_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worktree':str(ROOT),'comparison':'git show IMPLEMENTATION:path bytes == worktree file bytes','products':checks},indent=2)+'\n')
probe="CODEX_ROLLOUT_TRACE_ROOT=/tmp/readme-context-probe codex exec --ephemeral --json -C /Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation -m gpt-6-astra 'Reply OK.' > /tmp/readme-context-probe.stdout.jsonl 2> /tmp/readme-context-probe.stderr"
for name in ['readme-context-probe.stderr','readme-context-probe.stdout.jsonl']:
    put(Path('infrastructure')/name,Path('/tmp',name).read_text())
manifest={'implementation':SHA,'task_trial_count':0,'task_trials':[],'tasks_not_launched':['T1','T2','T3','T4','T5','T6'],'probe_count':1,'probe_is_task_trial':False,'probe_prompt':'Reply OK.','command':probe,'reported_exit_code':1,'stdout_bytes':Path('/tmp/readme-context-probe.stdout.jsonl').stat().st_size,'trace_directory_exists':Path('/tmp/readme-context-probe').exists(),'provenance':'Exact command and exit status supplied by orchestrator from capture agent. Copied stdout and stderr verified from disk.'}
put(Path('infrastructure/manifest.json'),json.dumps(manifest,indent=2)+'\n')
put(Path('infrastructure/README.md'),HEADER+'One infrastructure probe fails before agent startup. It has no task prompt or module-navigation result.\nThe supplied command and exit status come from the orchestrator’s capture record.\nThe copied stdout is empty; stderr contains the startup error. No trace directory exists.\nA complete automatic context inventory is unavailable because startup never completes.\nFresh collaboration agents start at the main checkout, per the orchestrator’s launch observation.\nThis directory has no independent trace of that collaboration-agent observation.\nThat start directory cannot prove the fixed spec-root procedure.\nNo cold task agent starts. The manifest records zero task trials, with no inferred answers or file counts.\n\n```sh\n'+probe+'\n```\n')
accept=source('.scratch/readme-module-navigation/ACCEPTANCE.md')
entry_files={1:['entry-links.md'],2:['app-maps.md'],3:['owner-maps.md','module-test-responsibilities.md'],4:['owner-shape.md','existing-rule-sources.md','rule-output.md'],5:['document-duties.md'],6:['api-dependencies.md'],16:['document-scope.md','product.diff'],17:['excluded-scope.md','feature.diff']}
obs={1:'The root links each app README. App instructions link their READMEs; the root states the full owner route.',2:'The maps separate the approved responsibilities. Each relative target exists at the implementation revision.',3:'Owner maps pair modules with tests and name adjacent owners. Source excerpts show the six stated responsibilities and assertions.',4:'The seven numbered READMEs have the required headings and at most 24 physical lines. Exact rule output awaits capture.',5:'Complete before/after documents preserve existing duties. Normal state and ticket reads remain; the approved exception covers cold trials only.',6:'Root and API documents exclude pipeline product imports. The AST inventory and dev dependencies distinguish test helper reuse.',16:'The fixed revision changes all 13 approved product documents. The inventory separates tracker records and maps documents to six routes.',17:'The fixed implementation diff changes Markdown only. Historical ticket 07 remains ready-for-agent with unchecked requirements; deferred gaps retain separate scope.'}
evidence=f'# README module navigation: evidence\n\nSpec: `.scratch/readme-module-navigation/PRD.md`. Acceptance tests: `.scratch/readme-module-navigation/ACCEPTANCE.md`.\nBuilt from: `{SHA}`, on 2026-11-12. Base: `{BASE}`.\nThe agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.\nRound time: not applicable; document capture has no screenshot runner or completed cold trial.\n\nProduct byte checks: `evidence/snapshot.json`.\nInfrastructure record: `evidence/infrastructure/manifest.json` and `evidence/infrastructure/README.md`.\nNo cold task trial starts. AT-7 through AT-15 have no observed task results.\n\n'
for match in re.finditer(r'^AT-(\d+): (.+)\nApp: (.+)\n(?:.*?\n)*?Then: (.+)\n',accept,re.M):
    n=int(match[1]); title,app,then=match.group(2,3,4)
    listed=', '.join(f'`evidence/AT-{n}/{f}`' for f in entry_files[n]) if n in entry_files else 'none'
    observation=obs.get(n,'Skipped: ticket 02 is blocked before launch by the agent infrastructure. No task trial runs; no task evidence is inferred.')
    evidence+=f'## AT-{n}: {title}\n\nApp: {app}\nThen: {then}\nFiles: {listed}\nObservation: {observation}\n\n'
(ROOT/'.scratch/readme-module-navigation/EVIDENCE.md').write_text(evidence)
put(Path('read-inventory.txt'),'Fixed-revision source files read for static capture, not a cold-agent file-read log:\n'+''.join(p+'\n' for p in sorted(READ)))
print(json.dumps({'evidence_files':len(list(OUT.rglob('*'))),'entries':len(re.findall(r'^## AT-',evidence,re.M)),'product_count':len(checks),'source_reads':len(READ)},indent=2))
PY_CAPTURE
```

## Exact rule records and stage timing

```sh
python3 - <<'PY_CAPTURE'
"""Attach exact rule records to the fixed README evidence capture.
Keep the active full check and absent cold trials explicit.
"""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path('/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation')
FEATURE=ROOT/'.scratch/readme-module-navigation'; E=FEATURE/'evidence'
SHA='dad744db4f3b49732adc1586e08c34be2f381f73'; HEAD='85d54d463a6bb111bb37c58bd810c24d1d9f4131'
meta=json.loads(Path('/tmp/readme-full-check.meta.json').read_text())
snapshot=json.loads((E/'snapshot.json').read_text())
assert snapshot['capture_utc']>meta['start']
for row in snapshot['products']:
    assert (ROOT/row['path']).read_bytes()==subprocess.check_output(['git','show',SHA+':'+row['path']],cwd=ROOT)
status=subprocess.check_output(['git','diff','--name-status',SHA,HEAD],cwd=ROOT,text=True)
assert all('.scratch/readme-module-navigation/issues/' in row for row in status.splitlines())
rule_cases=[('site',ROOT,'NODE_OPTIONS=--experimental-strip-types pnpm --dir apps/site exec vitest run src/readme-rule.test.ts',7),('pipeline',ROOT/'apps/pipeline','uv run --exact --package cornerstone pytest -q tests/test_rule_readmes.py',11),('api',ROOT/'apps/api','uv run --exact --package cpc-api pytest -q tests/test_rule_api.py',5)]
text=f'''# Existing README rule execution

Fixed implementation revision: `{SHA}`.
Execution checkout HEAD: `{HEAD}`.
The orchestrator supplies the commands, working directories, revision, and successful exit status for these exact reruns.
The raw logs below contain the complete output. Each copied file retains its original bytes.
The fixed implementation and execution HEAD differ only in two ticket status records.
The product byte comparison in `../snapshot.json` confirms all 13 documents against the fixed implementation.
The full HEAD delta below also excludes any rule-test or source change.
No rule code changes for this feature. No cold task trial runs.

```text
'''+status+'```\n\n'
for app,cwd,command,count in rule_cases:
    original=Path('/tmp')/f'readme-static-{app}-rules.log'; copied=E/'AT-4'/original.name
    raw=original.read_bytes(); copied.write_bytes(raw)
    text+=f'''## {app}

Command: `{command}`.
Working directory: `{cwd}`.
Exit status: `0`, reported by the orchestrator.
Observed output: `{count}` tests pass in the existing rule file.
Raw output: `{original.name}`.
SHA-256: `{hashlib.sha256(raw).hexdigest()}`.

```text
{raw.decode()}```

'''
(E/'AT-4/rule-output.md').write_text(text)
(E/'background-check-start.json').write_bytes(Path('/tmp/readme-full-check.meta.json').read_bytes())
(E/'capture-stage.md').write_text(f'''# Evidence stage capture

Implementation revision: `{SHA}`.
Execution checkout HEAD: `{HEAD}`.
Background full check start: `{meta['start']}`.
Static recapture time: `{snapshot['capture_utc']}`.
The static collector runs after the full background check starts.
The full check command and launch metadata appear in `background-check-start.json`.
The full check log remains `/tmp/readme-full-check.log`; this record does not claim its completion.
This worker runs pure Python and read-only Git commands only.
The exact README-rule reruns finish before this recapture; their raw logs appear under `AT-4/`.
No dependency command starts in this worker while the full check owns the shared environment.
Preparation before the background check supplies no separate acceptance result.
The fixed implementation diff excludes later evidence formats and ticket status updates.
No cold task trial runs; the infrastructure record remains separate from task evidence.
''')
p=FEATURE/'EVIDENCE.md'; s=p.read_text()
s=s.replace('Product byte checks: `evidence/snapshot.json`.','Product byte checks: `evidence/snapshot.json`.\nCapture method: `evidence/capture-method.md`. Reproduction commands: `evidence/reproduce.md`.\nEvidence-stage recapture: `evidence/capture-stage.md`.')
s=s.replace('Exact rule output awaits capture.','The exact existing rule logs report 7 site, 11 pipeline, and 5 API tests passed.')
s=s.replace('`evidence/AT-4/rule-output.md`','`evidence/AT-4/rule-output.md`, `evidence/AT-4/readme-static-site-rules.log`, `evidence/AT-4/readme-static-pipeline-rules.log`, `evidence/AT-4/readme-static-api-rules.log`')
p.write_text(s)
p=E/'read-inventory.txt'; p.write_text(p.read_text()+'''
Additional planning and capture files read outside the fixed-revision collector:
.scratch/readme-module-navigation/PRD.md
.scratch/readme-module-navigation/ACCEPTANCE.md
.scratch/readme-module-navigation/MAP.md
.scratch/readme-module-navigation/issues/02-prove-all-six-routes-with-cold-agents.md
.scratch/readme-module-navigation/decisions/01-grill-representative-task-set.md
.scratch/readme-module-navigation/decisions/02-grill-readme-coverage-and-structure.md
.scratch/readme-module-navigation/decisions/03-grill-cold-agent-test-procedure.md
/Users/brian.kwon/repos/4thandgoal/.agents/skills/4ag-implement/evidence.md
/tmp/readme-ticket01-site-rules.log
/tmp/readme-ticket01-pipeline-rules.log
/tmp/readme-ticket01-api-rules.log
/tmp/readme-context-probe.stderr
/tmp/readme-context-probe.stdout.jsonl
/tmp/readme-static-site-rules.log
/tmp/readme-static-pipeline-rules.log
/tmp/readme-static-api-rules.log
/tmp/readme-full-check.meta.json
/tmp/build-readme-static-evidence.py
/tmp/finalize-readme-static-evidence.py

Unavailable reads:
The worktree evidence.md skill path is absent; the main-checkout copy supplies the template.
The supplied ~/.Codex STE rules path is absent; task instructions supply output rules.
''')
for n,name in [(1,'entry-links.md'),(2,'app-maps.md'),(3,'owner-maps.md')]:
    assert '| false |' not in (E/f'AT-{n}'/name).read_text()
assert p.exists()
print('Static recapture follows full-check launch; 13 product byte comparisons agree; exact rule logs retained.')
PY_CAPTURE
```

## Second infrastructure startup record

Run this archival command after the first two reproduction commands.
It preserves both original probes; it does not execute either codex command or launch any task.
Restore both probes’ stdout and stderr to the recorded /tmp paths before this archival step.
The two commands above recreate the first capture; this final step adds the later infrastructure probe.

```sh
python3 - <<'PY_CAPTURE'
"""Preserve two infrastructure startup probes as evidence.
Keep both probes separate from the six unrun cold tasks.
"""
from pathlib import Path
import hashlib,json
ROOT=Path('/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation')
E=ROOT/'.scratch/readme-module-navigation/evidence'; INF=E/'infrastructure'
manifest=json.loads((INF/'manifest.json').read_text())
command2='''mkdir -p /tmp/readme-context-probe2-db /tmp/readme-context-probe2-logs; CODEX_ROLLOUT_TRACE_ROOT=/tmp/readme-context-probe2 codex exec --strict-config -c 'sqlite_home="/tmp/readme-context-probe2-db"' -c 'log_dir="/tmp/readme-context-probe2-logs"' --ephemeral --json -C /Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation -m gpt-6-astra 'Reply OK.' > /tmp/readme-context-probe2.stdout.jsonl 2> /tmp/readme-context-probe2.stderr'''
command1="CODEX_ROLLOUT_TRACE_ROOT=/tmp/readme-context-probe codex exec --ephemeral --json -C /Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation -m gpt-6-astra 'Reply OK.' > /tmp/readme-context-probe.stdout.jsonl 2> /tmp/readme-context-probe.stderr"
probes=[]
for index,stem,command in [(1,'readme-context-probe',command1),(2,'readme-context-probe2',command2)]:
    outputs={}
    for suffix in ['stdout.jsonl','stderr']:
        name=stem+'.'+suffix; raw=Path('/tmp',name).read_bytes(); (INF/name).write_bytes(raw)
        assert (INF/name).read_bytes()==raw
        outputs[suffix]={'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    probes.append({'probe':index,'is_task_trial':False,'prompt':'Reply OK.','command':command,'reported_exit_code':1,'trace_directory_exists':Path('/tmp',stem).exists(),'output':outputs})
manifest={k:manifest[k] for k in ['implementation','task_trial_count','task_trials','tasks_not_launched']}
manifest.update({'probe_count':2,'probes':probes,'provenance':'Exact commands and exit statuses supplied by orchestrator. Copied stdout and stderr verified byte-for-byte from disk.','probe2_configuration':'Supported sqlite_home and log_dir CLI overrides target /tmp. No source config, HOME, CODEX_HOME, auth, instructions, or sandbox change.'})
(INF/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
text=f'''# Infrastructure startup probes

Implementation revision: `{manifest['implementation']}`.
The archive holds exactly two infrastructure-only startup probes and zero cold task trials.
Each probe receives only `Reply OK.`; neither receives any approved task prompt.
Both commands exit before agent startup with the same in-process app-server permission error.
Both stdout files contain zero bytes. Neither trace directory exists.
The manifest preserves each exact command, reported exit code, output size, and output hash.
The orchestrator supplies commands and exit statuses; this worker verifies the archived output bytes.

Probe 2 uses supported sqlite_home and log_dir CLI overrides under /tmp.
The orchestrator reports that SQLite files appear under the selected /tmp directory before the same startup error.
No source config, HOME, CODEX_HOME, auth, instructions, or sandbox setting changes.
Neither probe establishes an automatic context inventory or any task result.
No cold task agent starts; no task failure, chosen paths, reasons, or file counts are inferred.

Fresh collaboration agents start at the main checkout, per the orchestrator’s launch observation.
This directory has no independent trace of that collaboration-agent observation.
That start directory cannot prove the fixed spec-root procedure.

'''
for probe in probes:
    text+=f"## Probe {probe['probe']}\n\n```sh\n{probe['command']}\n```\n\n"
(INF/'README.md').write_text(text)
p=E/'read-inventory.txt'; text=p.read_text()
for name in ['/tmp/readme-context-probe2.stdout.jsonl','/tmp/readme-context-probe2.stderr','/tmp/append-readme-probe2.py']:
    if name not in text: text+='\n'+name
p.write_text(text+'\n')
p=E/'file-inventory.md'; files=sorted({E.parent/'EVIDENCE.md',p,*[x for x in E.rglob('*') if x.is_file()]})
p.write_text('# Evidence file inventory\n\nAll paths are relative to `.scratch/readme-module-navigation/`.\n\n'+''.join('- `'+str(x.relative_to(E.parent))+'`\n' for x in files))
assert manifest['task_trial_count']==0 and len(probes)==2
print('Two startup probes preserved; zero cold task trials; raw copies match.')
PY_CAPTURE
```

## Full repository check completion record

Run this archival command after the earlier capture commands.
It preserves the completed process log and its metadata; it does not execute the full check.
Restore the archived full-check files to their original /tmp paths before this step if necessary.
The process exits with code 2; the repository check remains incomplete.

```sh
python3 - <<'PY_CAPTURE'
"""Archive the full repository check and its infrastructure limit.
Keep the existing static evidence and task-trial count unchanged.
"""
from pathlib import Path
import hashlib,json
ROOT=Path('/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation')
FEATURE=ROOT/'.scratch/readme-module-navigation'; E=FEATURE/'evidence'; INF=E/'infrastructure'
meta=json.loads(Path('/tmp/readme-full-check.meta.json').read_text())
log=Path('/tmp/readme-full-check.log').read_bytes()
assert meta['exit_code']==2 and b'1334 passed (1334)' in log
assert b'Permission denied (1100)' in log and b'MachPortRendezvousServer' in log
for name in ['readme-full-check.log','readme-full-check.meta.json']:
    raw=Path('/tmp',name).read_bytes(); (INF/name).write_bytes(raw)
    assert (INF/name).read_bytes()==raw
manifest=json.loads((INF/'manifest.json').read_text())
manifest['repository_check']={'command':meta['command'],'cwd':meta['cwd'],'head':meta['head'],'implementation':meta['implementation'],'start':meta['start'],'end':meta['end'],'exit_code':meta['exit_code'],'log':'readme-full-check.log','metadata':'readme-full-check.meta.json','log_sha256':hashlib.sha256(log).hexdigest(),'site_unit_tests_passed':1334,'later_members_reached':False,'limitation':'Chromium Mach port bootstrap_check_in fails with Permission denied (1100) in Playwright rule suites. The full repository check remains incomplete.'}
(INF/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
summary=f'''## Full repository check

Command: `{meta['command']}`.
Working directory: `{meta['cwd']}`.
Checkout HEAD: `{meta['head']}`. Product revision: `{meta['implementation']}`.
Start: `{meta['start']}`. End: `{meta['end']}`. Exit code: `2`.
The full output and metadata appear in `readme-full-check.log` and `readme-full-check.meta.json`.
The log reports 131 site unit-test files and 1,334 tests passed before the browser rule suites.
Chromium startup fails at `bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer` with `Permission denied (1100)`.
Playwright reports 22 rule tests failed and one passed; the site check then stops.
The site build and export steps do not run after the browser failure.
The later pipeline and API members do not run in this full-check invocation.
The full repository check remains incomplete. This record gives no acceptance Test verdict.
No product behavior, test behavior, or sandbox restriction changes to bypass this failure.
The two independent startup probes remain non-task probes; the cold-trial count remains zero.
'''
p=INF/'README.md'; text=p.read_text().split('## Full repository check')[0].rstrip(); p.write_text(text+'\n\n'+summary)
p=E/'capture-stage.md'; text=p.read_text()
text=text.replace('The full check log remains `/tmp/readme-full-check.log`; this record does not claim its completion.','The full-check process ends with exit 2; the repository check remains incomplete.\nIts full log and completion metadata appear under `infrastructure/`.')
p.write_text(text)
p=FEATURE/'EVIDENCE.md'; text=p.read_text(); needle='Round time: not applicable; document capture has no screenshot runner or completed cold trial.\n'
note='\nFull repository check: exit 2 after Chromium startup reports `Permission denied (1100)` in the Playwright rule suites.\nThe log reports 1,334 site unit tests passed; later members are not reached. The full repository check remains incomplete.\nFull log and completion metadata: `evidence/infrastructure/readme-full-check.log`, `evidence/infrastructure/readme-full-check.meta.json`.\n'
if note not in text: text=text.replace(needle,needle+note)
p.write_text(text)
p=E/'read-inventory.txt'; text=p.read_text()
for name in ['/tmp/readme-full-check.log','/tmp/readme-full-check.meta.json','/tmp/append-readme-full-check.py','Makefile']:
    if name not in text.splitlines(): text+='\n'+name
p.write_text(text+'\n')
p=E/'file-inventory.md'; files=sorted({FEATURE/'EVIDENCE.md',p,*[x for x in E.rglob('*') if x.is_file()]})
p.write_text('# Evidence file inventory\n\nAll paths are relative to `.scratch/readme-module-navigation/`.\n\n'+''.join('- `'+str(x.relative_to(FEATURE))+'`\n' for x in files))
print(f'Full check log and completion metadata preserved; {len(files)} evidence files.')
PY_CAPTURE
```
