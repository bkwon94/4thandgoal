"""The counts of AT-41 from the frame logs: motion over frames, one-frame jumps of place, and fades of opacity.
Usage: python3 at41-count.py <evidence/AT-41 folder>"""
import re, sys, collections
D = sys.argv[1]
LINE = re.compile(r"^t=(\d+)ms (\S+) (#\d+) (.*?) \(x ([\d.-]+), y ([\d.-]+), w [\d.]+, h [\d.]+, opacity ([\d.]+)\) -> \(x ([\d.-]+), y ([\d.-]+), w [\d.]+, h [\d.]+, opacity ([\d.]+)\)")
for mode in ["reduced-light", "reduced-dark", "full-light", "full-dark"]:
    rows = [LINE.match(l) for l in open(f"{D}/frames-{mode}.txt") if l.startswith("t=")]
    rows = [m for m in rows if m]
    frames = sorted({int(m[1]) for m in rows})
    pos = collections.defaultdict(list)
    ops = collections.defaultdict(list)
    names = {}
    for m in rows:
        t, kind, el = int(m[1]), m[2], m[3]
        names.setdefault(el, m[4])
        if "pos" in kind:
            pos[el].append((t, float(m[5]), float(m[6]), float(m[8]), float(m[9]), float(m[10])))
        if "opacity" in kind:
            ops[el].append((t, float(m[7]), float(m[10])))
    # Motion: a change of place on two logged frames in a row of the same element, with no other frame of the log between them.
    idx = {t: i for i, t in enumerate(frames)}
    moving = {el for el, ps in pos.items() if any(idx[b[0]] - idx[a[0]] == 1 for a, b in zip(ps, ps[1:]))}
    jumps = [(el, p) for el, ps in pos.items() if el not in moving for p in ps]
    at_full = sum(1 for _, p in jumps if p[5] >= 0.999)
    fades = {el: o for el, o in ops.items() if any(0 < x[2] < 1 for x in o)}
    steps = {el: o for el, o in ops.items() if el not in fades}
    print(f"{mode}: {len(frames)} frames with a change, from t={frames[0]}ms to t={frames[-1]}ms")
    print(f"  elements that change place on two frames in a row (motion): {len(moving)}")
    print(f"  changes of place on one frame only (a jump, no motion between): {len(jumps)} on {len({el for el, _ in jumps})} elements; at the jump frame, shown opacity 1 for {at_full}, under 1 for {len(jumps) - at_full}")
    print(f"  elements that change shown opacity: {len(ops)}; with values between 0 and 1 on some frame (a fade): {len(fades)}; with a step and no value between: {len(steps)}")
    for el, o in list(fades.items())[:3]:
        print(f"    fade example {el} {names[el]}: " + " -> ".join(f"{x[2]}@{x[0]}ms" for x in o[:10]) + (" ..." if len(o) > 10 else ""))
    for el, o in list(steps.items())[:10]:
        print(f"    step {el} {names[el]}: " + " -> ".join(f"{x[1]}->{x[2]}@{x[0]}ms" for x in o[:4]))
    for el in list(moving)[:5]:
        print(f"    motion example {el} {names[el]}: " + "; ".join(f"t={p[0]}ms ({p[1]}, {p[2]}) -> ({p[3]}, {p[4]})" for p in pos[el][:5]))
    for el, p in jumps[:6]:
        print(f"    jump example {el} {names[el]}: t={p[0]}ms ({p[1]}, {p[2]}) -> ({p[3]}, {p[4]}), shown opacity {p[5]}")
