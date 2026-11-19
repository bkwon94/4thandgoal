# Next.js security patch

Kind: bug
Status: done
Branch: `bug-next-security-patch`.
Source: the session of 2026-11-19.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The site uses a Next.js version with a known security vulnerability

Done condition: The site resolves a Next.js version that no known security advisory covers, so `pnpm audit` names no advisory of `next` and `next build` of both clients ends with no `SecurityFatalError`.
Method: diagnosing-bugs
Cause: `apps/site/package.json` sets `"next": "^16.4.2"`, and the root `pnpm-lock.yaml` resolves `next@16.4.2`, which falls in the ranges of GHSA-mfr8-8qww-v76h and GHSA-vc7v-qv4w-wrv8; 16.4.5 is the first patched version.
Red: at `dec02a0b`, the parent of the fix commit, because the loop is a command and no file in the repo, `pnpm --dir apps/site audit --prod --json 2>/dev/null | python3 -c "import json,sys; a=[v for v in json.load(sys.stdin).get('advisories',{}).values() if v['module_name']=='next']; [print(v['github_advisory_id'], v['vulnerable_versions'], v['title']) for v in a]; print(f'next advisories: {len(a)}'); sys.exit(1 if a else 0)"; echo exit=$?`

```text
GHSA-mfr8-8qww-v76h >=16.3.0 <=16.4.4 Next.js: Information disclosure across root params when a 'use cache' function is called through unstable_cache()
GHSA-vc7v-qv4w-wrv8 >=16.2.0 <=16.4.4 Next.js: Cache leak across root param values in nested 'use cache' functions via delayed inner stream metadata
next advisories: 2
exit=1
```

Green: at `cae51993`, `pnpm --dir apps/site audit --prod --json 2>/dev/null | python3 -c "import json,sys; a=[v for v in json.load(sys.stdin).get('advisories',{}).values() if v['module_name']=='next']; [print(v['github_advisory_id'], v['vulnerable_versions'], v['title']) for v in a]; print(f'next advisories: {len(a)}'); sys.exit(1 if a else 0)"; echo exit=$?`

```text
next advisories: 0
exit=0
```

`pnpm --dir apps/site audit --prod` at `cae51993` prints "No known vulnerabilities found". The site is the one workspace member that depends on `next`; no member depends on `eslint-config-next` or another `@next/*` package, and each `@next/*` entry of the lock file is at 16.4.5.

The build proof at `cae51993`, in `apps/site`, each client twice:

```text
bp-cpc-1 exit=0 next=Next.js 16.4.5 SecurityFatalError=0
bp-norcal-1 exit=0 next=Next.js 16.4.5 SecurityFatalError=0
bp-cpc-2 exit=0 next=Next.js 16.4.5 SecurityFatalError=0
bp-norcal-2 exit=0 next=Next.js 16.4.5 SecurityFatalError=0
```

`make check-fast BASE=main` at `cae51993` passed on the second run: the site run shows `Tests  1731 passed (1731)`. The first run failed only on the known flaky `page-free.test.tsx` under load from other sessions.
`make -C apps/site check` at `cae51993` passed: `Tests  1731 passed (1731)`, and `check:export` passed for `cpc` and `norcal`.
Test verdict: PASS

## Comments

- Closes with the squash merge of the PR of `bug-next-security-patch`. Commits: `dec02a0b`, `cae51993`, `85c4f43c`. Date: 2026-11-19.
- The audit loop went red with 2 advisories of `next` at `dec02a0b`, then green with 0 at `cae51993`, and 1731 site tests pass.
- Four builds of both clients on Next.js 16.4.5 printed no `SecurityFatalError`; 16.4.6 also exists and needs no change now.
- Read 4 files: AGENTS.md, apps/site/AGENTS.md, apps/site/package.json, .scratch/bugs/next-security-patch.md.
