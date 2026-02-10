#!/usr/bin/env python3
"""Find minimal commutator holonomy cycles and compute ordered root-word invariants.

Outputs:
  - analysis/minimal_holonomy_cycles_ordered_rootwords.csv
  - analysis/minimal_holonomy_cycles_ordered_rootwords.json

Quick summary: find T(u),T(v) commutator loops for all non-parallel ordered pairs (u,v) in F3^2,
construct the 4-step commutator walk from each representative basepoint, substitute
shortest-path segments in the W33 graph for each group step, canonicalize cycles up to
rotation+reversal, select minimal-length cycles (expected length 8), and compute the
ordered list of E8 root vectors on the cycle edges (using artifacts/edge_to_e8_root.json).
Then compute simple invariants (root sum, root sum mod 3) and write results.
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


def load_adj(path: Path) -> Dict[int, List[int]]:
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    adj = {}
    for i, line in enumerate(lines):
        parts = line.split()
        neighbors = [j for j, v in enumerate(parts) if v == "1"]
        adj[i] = neighbors
    return adj


def bfs_shortest_path(adj: Dict[int, List[int]], a: int, b: int, edge_to_root: Dict[str, List[int]] | None = None, require_roots: bool = False) -> List[int] | None:
    """Return a shortest path from a to b. Tie-break by preferring paths with the
    fewest edges missing in the edge_to_root mapping (if provided).

    If require_roots is True, only traverse edges that have a root mapping in
    edge_to_root (or reversed key).
    """
    if a == b:
        return [a]
    # Use Dijkstra-like lexicographic priority: (distance, missing_roots)
    import heapq

    heap = [(0, 0, [a])]
    best = {}  # node -> (dist, missing)
    while heap:
        dist, missing, path = heapq.heappop(heap)
        node = path[-1]
        if node == b:
            return path
        prev = best.get(node)
        if prev is not None and (prev[0] < dist or (prev[0] == dist and prev[1] <= missing)):
            continue
        best[node] = (dist, missing)
        for n in adj[node]:
            edge_key = f"({node}, {n})"
            has_root = False
            if edge_to_root is not None:
                if edge_key in edge_to_root or f"({n}, {node})" in edge_to_root:
                    has_root = True
            if require_roots and not has_root:
                # skip edges that lack root mapping when roots are required
                continue
            new_missing = missing + (0 if has_root else 1)
            heapq.heappush(heap, (dist + 1, new_missing, path + [n]))
    return None


def compose_perm(p: Dict[int, int], q: Dict[int, int]) -> Dict[int, int]:
    # compose p ◦ q (apply q then p)
    return {k: p[q[k]] for k in q}


def pow_perm(p: Dict[int, int], exp: int) -> Dict[int, int]:
    n = len(p)
    if exp == 0:
        return {k: k for k in p}
    if exp < 0:
        # invert and power
        inv = {v: k for k, v in p.items()}
        exp = (-exp) % 3
        res = {k: k for k in p}
        for _ in range(exp):
            res = {k: inv[res[k]] for k in res}
        return res
    res = {k: k for k in p}
    for _ in range(exp):
        res = {k: p[res[k]] for k in res}
    return res


def canonical_cycle(cycle: List[int]) -> Tuple[int, ...]:
    # canonicalize up to rotation and reversal; return smallest lex tuple
    n = len(cycle)
    rots = [tuple(cycle[i:] + cycle[:i]) for i in range(n)]
    rev = list(reversed(cycle))
    rots += [tuple(rev[i:] + rev[:i]) for i in range(n)]
    return min(rots)


def get_edge_root(edge_to_root: Dict[str, List[int]], a: int, b: int) -> List[int]:
    k1 = f"({a}, {b})"
    if k1 in edge_to_root:
        return edge_to_root[k1]
    k2 = f"({b}, {a})"
    if k2 in edge_to_root:
        # reversed orientation: return negated vector to reflect orientation flip
        return [-x for x in edge_to_root[k2]]
    raise KeyError(f"Edge root missing for {a},{b}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", type=Path, default=Path("analysis/minimal_commutator_cycles"))
    p.add_argument("--require-root-edges", action="store_true", help="Only traverse edges that have E8 root mappings")
    args = p.parse_args()

    outdir = args.outdir
    require_root_edges = bool(args.require_root_edges)
    outdir.mkdir(parents=True, exist_ok=True)

    adj = load_adj(Path("W33_adjacency_matrix.txt"))
    txj = json.loads((Path("analysis/w33_bundle_temp/analysis/W33_Heisenberg_generators_Tx_Ty_Z.json")).read_text())
    tx_perm = {int(k): int(v) for k, v in txj["Tx"]["perm_40"].items()}
    ty_perm = {int(k): int(v) for k, v in txj["Ty"]["perm_40"].items()}

    # compute all non-parallel ordered pairs (u,v) in F3^2 with det != 0
    F3 = [0, 1, 2]
    vectors = [(x, y) for x in F3 for y in F3]
    nonzero = [v for v in vectors if v != (0, 0)]

    pairs = []
    for u in nonzero:
        for v in nonzero:
            det = (u[0] * v[1] - u[1] * v[0]) % 3
            if det != 0:
                pairs.append((u, v, det))

    # H27 reps: pick t=0 vertices from the H27 CSV
    reps = []
    for r in (Path("analysis/w33_bundle_temp/analysis/H27_vertices_as_F3_cube_xy_t_holonomy_gauge.csv")).read_text().splitlines():
        if not r.strip() or r.startswith("w33_vertex"):
            continue
        parts = r.split(',')
        w = int(parts[0])
        t = int(parts[3])
        if t == 0:
            reps.append(w)

    edge_to_root = json.loads((Path("artifacts/edge_to_e8_root.json")).read_text())

    cycles_by_canonical = {}
    records = []

    for (ux, uy), (vx, vy), det in pairs:
        # T(u) = Tx^{ux} ◦ Ty^{uy}
        Tu = compose_perm(pow_perm(tx_perm, ux), pow_perm(ty_perm, uy))
        Tv = compose_perm(pow_perm(tx_perm, vx), pow_perm(ty_perm, vy))
        Tu_inv = {v: k for k, v in Tu.items()}
        Tv_inv = {v: k for k, v in Tv.items()}
        # commutator c = Tu ◦ Tv ◦ Tu^{-1} ◦ Tv^{-1}
        cperm = compose_perm(compose_perm(Tu, Tv), compose_perm(Tu_inv, Tv_inv))
        k = (-det) % 3

        for base in reps:
            p0 = base
            p1 = Tu[p0]
            p2 = Tv[p1]
            p3 = Tu_inv[p2]
            p4 = Tv_inv[p3]

            segments = []
            ok = True
            for a, b in ((p0, p1), (p1, p2), (p2, p3), (p3, p4)):
                sp = bfs_shortest_path(adj, a, b, edge_to_root, require_roots=require_root_edges)
                if sp is None:
                    ok = False
                    break
                segments.append(sp)
            if not ok:
                continue

            # closure from p4 back to p0
            spc = bfs_shortest_path(adj, p4, p0, edge_to_root, require_roots=require_root_edges)
            if spc is None:
                continue

            # concatenate paths but avoid double counting endpoints
            path = []
            for seg in segments:
                if not path:
                    path.extend(seg)
                else:
                    path.extend(seg[1:])
            if spc:
                path.extend(spc[1:])

            # if not closed (should be closed as vertices), ensure we ended at start
            if path[0] != path[-1]:
                # disallow unclosed
                continue

            cycle_vertices = path[:-1]  # drop duplicate final vertex to represent cycle
            cyc_can = canonical_cycle(cycle_vertices)
            length = len(cycle_vertices)

            # store minimal per canonical cycle
            if cyc_can in cycles_by_canonical:
                prev = cycles_by_canonical[cyc_can]
                if length < prev["length"]:
                    cycles_by_canonical[cyc_can] = {"length": length, "k": k, "u": (ux, uy), "v": (vx, vy), "representative": cycle_vertices}
            else:
                cycles_by_canonical[cyc_can] = {"length": length, "k": k, "u": (ux, uy), "v": (vx, vy), "representative": cycle_vertices}

    # collect cycles and select those with minimal length overall
    all_cycles = []
    for cyc, info in cycles_by_canonical.items():
        cyc_vertices = list(cyc)
        k = info["k"]
        length = info["length"]
        all_cycles.append({"cycle": cyc_vertices, "k": k, "length": length})

    if not all_cycles:
        print("No cycles found")
        return

    min_len = min(c["length"] for c in all_cycles)
    minimal_cycles = [c for c in all_cycles if c["length"] == min_len]

    # compute root-word invariants
    rows = []
    for idx, c in enumerate(sorted(minimal_cycles, key=lambda x: (x['k'], x['cycle']))):
        cyc = c["cycle"]
        k = c["k"]
        # ordered edges
        edges = [(cyc[i], cyc[(i + 1) % len(cyc)]) for i in range(len(cyc))]
        roots = []
        for a, b in edges:
            try:
                r = get_edge_root(edge_to_root, a, b)
            except KeyError:
                r = None
            roots.append(r)
        # compute sum
        root_sum = None
        if all(r is not None for r in roots):
            root_sum = [sum(col) for col in zip(*roots)]
            root_sum_mod3 = [int(x % 3) for x in root_sum]
        else:
            root_sum_mod3 = None
        rows.append({
            "id": idx,
            "k": int(k),
            "cycle_vertices": ",".join(str(x) for x in cyc),
            "cycle_length": int(c["length"]),
            "edge_roots_present": all(r is not None for r in roots),
            "root_sum": root_sum,
            "root_sum_mod3": root_sum_mod3,
            "edge_roots": [r for r in roots],
        })

    # write outputs
    (outdir / "minimal_holonomy_cycles_ordered_rootwords.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    # CSV summary
    import csv

    csvp = outdir / "minimal_holonomy_cycles_ordered_rootwords.csv"
    with csvp.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "k", "cycle_length", "cycle_vertices", "edge_roots_present", "root_sum_mod3"])
        for r in rows:
            w.writerow([r['id'], r['k'], r['cycle_length'], r['cycle_vertices'], r['edge_roots_present'], json.dumps(r['root_sum_mod3'])])

    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
