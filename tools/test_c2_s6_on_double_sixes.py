#!/usr/bin/env python3
"""Load the C2xS6 representative generators (0-based), compute closure, and test whether any double-six is stabilized setwise (allow swap).
Writes artifacts/w33_c2s6_double_six_results.json
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def closure_generated_by(gens, degree):
    identity = tuple(range(degree))
    closure = {identity}
    q = deque([identity])
    while q:
        h = q.popleft()
        for g in gens:
            comp = tuple(g[i] for i in h)
            if comp not in closure:
                closure.add(comp)
                q.append(comp)
    return closure


def image_of_lineset(perm, lineset, lines):
    mapped = {tuple(sorted(perm[i] for i in lines[idx])) for idx in lineset}
    return mapped


def main():
    rep = json.loads(
        (ART / "sage_c2_s6_representative.json").read_text(encoding="utf-8")
    )
    gens = rep["generators"]
    pts = json.loads(
        (ROOT.parent / "artifacts" / "w33_aut_group_summary.json").read_text()
    )
    # degree is 40
    degree = 40
    closure = closure_generated_by(gens, degree)
    print("Closure size (should be 1440):", len(closure))

    # load lines and double_sixes
    from tools.find_schlafli_embedding_in_w33 import (
        compute_w33_lines,
        construct_w33_points,
    )

    lines = compute_w33_lines(construct_w33_points())

    doubles = json.loads(
        (ART / "w33_double_sixes_full.json").read_text(encoding="utf-8")
    )["double_sixes"]

    stabilized = []
    for idx, ds in enumerate(doubles):
        A = ds["A"]
        B = ds["B"]
        A_tuples = {tuple(sorted(lines[i])) for i in A}
        B_tuples = {tuple(sorted(lines[i])) for i in B}
        ok = True
        for g in closure:
            Ag = {tuple(sorted(g[i] for i in lines[i])) for i in A}
            Bg = {tuple(sorted(g[i] for i in lines[i])) for i in B}
            if not (
                (Ag == A_tuples and Bg == B_tuples)
                or (Ag == B_tuples and Bg == A_tuples)
            ):
                ok = False
                break
        if ok:
            stabilized.append({"index": idx, "A": A, "B": B})
            print("Found stabilized double-six at idx", idx)
            break

    out = {
        "closure_size": len(closure),
        "stabilized_count": len(stabilized),
        "stabilized": stabilized,
    }
    (ART / "w33_c2s6_double_six_results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print("Wrote", ART / "w33_c2s6_double_six_results.json")


if __name__ == "__main__":
    main()
