#!/usr/bin/env python3
"""Classify z3 candidates by conjugacy class and centralizer size.

Loads latest PART_CVII_z3_candidates_*.json and computes, for each candidate:
 - permutation order (on 40 vertices)
 - centralizer size in PSp(4,3)
 - conjugacy class size = |G| / |centralizer|

Prints a summary and writes checks/PART_CVII_z3_conjugacy_<ts>.json
"""
from __future__ import annotations

import glob
import json
import time
from collections import defaultdict
from pathlib import Path

from w33_full_decomposition import build_psp43_group
from w33_homology import build_w33


def compose(p, q):
    # p, q are tuples representing permutations on {0..n-1}
    return tuple(p[q[i]] for i in range(len(q)))


def perm_power(p, k):
    n = len(p)
    res = tuple(range(n))
    for _ in range(k):
        res = compose(p, res)
    return res


def main():
    files = sorted(
        glob.glob("checks/PART_CVII_z3_candidates_*.json"),
        key=lambda p: Path(p).stat().st_mtime,
    )
    if not files:
        raise FileNotFoundError("No candidate file found")
    f = files[-1]
    data = json.load(open(f, "r", encoding="utf-8"))

    n, vertices, adj, edges = build_w33()
    group = build_psp43_group(vertices, edges)
    group_elems = list(group.keys())
    Gsize = len(group_elems)

    results = []
    seen_reprs = {}
    for i, cand in enumerate(data.get("candidates", []), start=1):
        vperm = tuple(cand["vertex_perm"])
        # order on 40 vertices
        ord1 = 1
        cur = vperm
        while cur != tuple(range(len(vperm))):
            cur = compose(vperm, cur)
            ord1 += 1
            if ord1 > 200:
                break
        # centralizer size
        cen = 0
        for g in group_elems:
            if compose(vperm, g) == compose(g, vperm):
                cen += 1
        conj_size = Gsize // cen if cen > 0 else None
        results.append(
            {
                "index": i,
                "order_verts": ord1,
                "centralizer_size": cen,
                "conj_class_size": conj_size,
            }
        )

    ts = int(time.time())
    out = Path("checks") / f"PART_CVII_z3_conjugacy_{ts}.json"
    out.write_text(
        json.dumps({"file": f, "Gsize": Gsize, "results": results}, indent=2),
        encoding="utf-8",
    )
    print("Wrote", out)


if __name__ == "__main__":
    main()
