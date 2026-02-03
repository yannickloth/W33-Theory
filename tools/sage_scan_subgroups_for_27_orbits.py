#!/usr/bin/env sage
"""Scan conjugacy classes of subgroups of Aut(W(3,3)) for orbits of size 27..30 on the 40 lines.
For each matching orbit: if orbit size ==27, test SRG parameters; if size in 28..30 enumerate all 27-subsets and test.
Writes artifacts/sage_subgroup_27_orbit_scan.json with results.
"""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from tools.find_schlafli_embedding_in_w33 import compute_w33_lines
from tools.w33_aut_group_construct import build_points, generate_group, matrix_to_perm

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

try:
    from sage.interfaces.gap import gap
except Exception as e:
    print("This script must be run inside Sage: missing GAP interface:", e)
    raise SystemExit(1)

from itertools import combinations

import numpy as np


def is_srg_adj_matrix(adj):
    # adj: numpy 27x27 0/1
    n = adj.shape[0]
    if n != 27:
        return False
    degs = adj.sum(axis=1)
    if not np.all(degs == 16):
        return False
    lam = None
    mu = None
    for i in range(n):
        for j in range(i + 1, n):
            common = int((adj[i] & adj[j]).sum())
            if adj[i, j]:
                if lam is None:
                    lam = common
                elif lam != common:
                    return False
            else:
                if mu is None:
                    mu = common
                elif mu != common:
                    return False
    return lam == 10 and mu == 8


def main():
    pts = build_points()
    _, point_perms = generate_group(pts)
    lines = compute_w33_lines(pts)
    nlines = len(lines)
    assert nlines == 40

    # Build GAP group on lines
    line_perms = []
    line_index = {tuple(sorted(l)): i for i, l in enumerate(lines)}
    for perm in point_perms:
        images_idx = [
            line_index[tuple(sorted(perm[i] for i in line))] + 1 for line in lines
        ]
        line_perms.append(images_idx)
    perm_exprs = ["PermList([%s])" % ",".join(str(x) for x in p) for p in line_perms]
    group_expr = "Group(" + ",".join(perm_exprs) + ")"

    classes = gap("ConjugacyClassesSubgroups(%s)" % group_expr)
    nclasses = int(classes.Length())
    print("Total conjugacy classes:", nclasses)

    results = []

    # Precompute adjacency matrix for lines graph
    import networkx as nx

    G = nx.Graph()
    G.add_nodes_from(range(nlines))
    for i in range(nlines):
        for j in range(i + 1, nlines):
            if set(lines[i]).isdisjoint(set(lines[j])):
                G.add_edge(i, j)

    for i in range(1, nclasses + 1):
        H = classes[i].Representative()
        order = int(H.Order())
        # compute orbits of H on lines (1-based)
        pts_list_expr = "[" + ",".join(str(k) for k in range(1, nlines + 1)) + "]"
        gap_pts = gap(pts_list_expr)
        orbs = H.Orbits(gap_pts)
        orb_sizes = [int(o.Length()) for o in orbs]
        interesting = [s for s in orb_sizes if 27 <= s <= 30]
        if not interesting:
            continue
        print("Found class", i, "order", order, "with orbit sizes", orb_sizes)
        # collect orbit lists (0-based)
        orb_lists = []
        for j in range(1, int(orbs.Length()) + 1):
            L = orbs[j]
            lst = [int(L[k]) - 1 for k in range(1, int(L.Length()) + 1)]
            if 27 <= len(lst) <= 30:
                orb_lists.append(lst)
        entry = {
            "class_index": i,
            "order": order,
            "structure": str(H.StructureDescription()),
            "orb_sizes": orb_sizes,
            "matching_orbits": [],
        }
        for orb in orb_lists:
            s = len(orb)
            if s == 27:
                # test directly
                S = orb
                adj = np.zeros((27, 27), dtype=int)
                for a in range(27):
                    for b in range(a + 1, 27):
                        if G.has_edge(S[a], S[b]):
                            adj[a, b] = adj[b, a] = 1
                ok = is_srg_adj_matrix(adj)
                entry["matching_orbits"].append(
                    {"orbit": orb, "type": "orbit27", "is_srg": ok}
                )
            else:
                # enumerate all 27-subsets of orb
                found_subs = []
                count = 0
                for subset in combinations(orb, 27):
                    count += 1
                    S = list(subset)
                    adj = np.zeros((27, 27), dtype=int)
                    for a in range(27):
                        for b in range(a + 1, 27):
                            if G.has_edge(S[a], S[b]):
                                adj[a, b] = adj[b, a] = 1
                    if is_srg_adj_matrix(adj):
                        found_subs.append(list(S))
                entry["matching_orbits"].append(
                    {
                        "orbit": orb,
                        "type": f"orb{s}",
                        "n_subsets_tested": count,
                        "n_found": len(found_subs),
                        "examples": found_subs[:3],
                    }
                )
        results.append(entry)
    (ART / "sage_subgroup_27_orbit_scan.json").write_text(
        json.dumps({"results": results}, indent=2), encoding="utf-8"
    )
    print("Wrote", ART / "sage_subgroup_27_orbit_scan.json")


if __name__ == "__main__":
    main()
