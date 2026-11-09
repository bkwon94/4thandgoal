"""
Lists each attempt of a verify.json for the jev evidence: the sentences, the Jev answers, and the Claude verdicts.
Usage: python3 attempts.py <verify.json> at1|at2|at3|at7
"""
import json
import sys

path, mode = sys.argv[1], sys.argv[2]
data = json.load(open(path))
rows = [(key, n, r) for key, results in data["chapters"].items() for n, r in enumerate(results, 1)]
checked = [(k, n, r) for k, n, r in rows if not r["code_failures"]]
print(f"file: {path}")
print(f"attempts: {len(rows)}, with no code failure: {len(checked)}, with a jev: {sum(1 for *_, r in rows if r.get('jev'))}")
for key, n, r in rows:
    jev, sents = r.get("jev"), r.get("sentences") or []
    tag = "code-fail" if r["code_failures"] else "checked"
    if mode == "at1":
        ans = [a["yes"] for a in (jev or {}).get("answers", [])]
        rng = f"lowest={min(ans):.4f} highest={max(ans):.4f}" if ans else "lowest=- highest=-"
        idx = [a["index"] for a in (jev or {}).get("answers", [])]
        print(f"{key} attempt {n} [{tag}]: sentences={len(sents)} jev_answers={len(ans)} indexes={idx} {rng} "
              f"all_in_0_1={all(0 <= a <= 1 for a in ans)} model={(jev or {}).get('model')}")
    elif mode == "at2":
        ans = [a["yes"] for a in (jev or {}).get("answers", [])]
        rule = bool(r["verdicts"]) and all(v["supported"] for v in r["verdicts"])
        print(f"{key} attempt {n} [{tag}]: sentences={len(sents)} claude_verdicts={len(r['verdicts'])} "
              f"passed={r['passed']} rule_all_supported={rule} passed_equals_rule={r['passed'] == rule} "
              f"lowest_jev={min(ans):.4f}" if ans else
              f"{key} attempt {n} [{tag}]: sentences={len(sents)} claude_verdicts={len(r['verdicts'])} "
              f"passed={r['passed']} rule_all_supported={rule} passed_equals_rule={r['passed'] == rule} lowest_jev=-")
    elif mode == "at3":
        print(f"{key} attempt {n} [{tag}]: jev={json.dumps(jev)}")
