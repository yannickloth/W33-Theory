#!/usr/bin/env python3
"""Local repair optimizer for W33->E8 bijection.

Greedy hill-climb that swaps edge->root assignments to increase the
number of triangles satisfying the cocycle condition
r_ab + r_bc = ± r_ac.

Usage:
    python scripts/optimize_bijection_cocycle.py --in checks/PART_CVII_e8_bijection.json --out checks/PART_CVII_e8_bijection_repaired.json --iters 2000 --time 10 --seed 42
"""
from __future__ import annotations

import argparse
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from e8_embedding_group_theoretic import build_w33, generate_e8_roots
from w33_e8_bijection import (
    classify_roots_z3_grading,
    decompose_w33_edges,
    verify_bijection_properties,
)


def load_bijection(path: Path):
    j = json.loads(path.read_text(encoding="utf-8"))
    bij_raw = j.get("bijection", {})
    bij = {int(k): int(v) for k, v in bij_raw.items()}
    return bij, j


def build_triangles(n, adj):
    tri_set = set()
    for a in range(n):
        for b in adj[a]:
            if b <= a:
                continue
            for c in adj[b]:
                if c <= b:
                    continue
                if a in adj[c]:
                    tri_set.add(tuple(sorted([a, b, c])))
    tri_list = list(tri_set)
    return tri_list


def triangle_exact(roots, bij, edges, tri):
    # tri: (a,b,c)
    edge_to_idx = {(u, v): i for i, (u, v) in enumerate(edges)}
    edge_to_idx.update({(v, u): i for i, (u, v) in enumerate(edges)})

    a, b, c = tri
    e_ab = edge_to_idx.get((a, b))
    e_bc = edge_to_idx.get((b, c))
    e_ac = edge_to_idx.get((a, c))
    if e_ab is None or e_bc is None or e_ac is None:
        return False

    r_ab = roots[bij[e_ab]]
    r_bc = roots[bij[e_bc]]
    r_ac = roots[bij[e_ac]]

    # Check r_ab + r_bc = ± r_ac (allow multiple sign combos)
    sums = [
        tuple(np.add(r_ab, r_bc)),
        tuple(np.subtract(r_ab, r_bc)),
        tuple(np.add(r_ab, tuple([-x for x in r_bc]))),
        tuple(np.subtract(tuple([-x for x in r_ab]), r_bc)),
    ]
    targets = {tuple(r_ac), tuple([-x for x in r_ac])}
    return any(s in targets for s in sums)


def optimize(
    bij_init,
    edges,
    adj,
    roots,
    iterations=2000,
    time_limit=10.0,
    seed=42,
    restrict_sector=True,
):
    rng = random.Random(seed)
    n = len(adj)
    tri_list = build_triangles(n, adj)

    # mapping edge->triangles
    edge_triangles = defaultdict(list)
    for t_idx, tri in enumerate(tri_list):
        a, b, c = tri
        edge_to_idx = {(u, v): i for i, (u, v) in enumerate(edges)}
        edge_to_idx.update({(v, u): i for i, (u, v) in enumerate(edges)})
        e_ab = edge_to_idx.get((a, b))
        e_bc = edge_to_idx.get((b, c))
        e_ac = edge_to_idx.get((a, c))
        for e in (e_ab, e_bc, e_ac):
            edge_triangles[e].append(t_idx)

    # initial exact flags
    exact_flags = [triangle_exact(roots, bij_init, edges, tri) for tri in tri_list]
    current_score = sum(exact_flags)
    best_score = current_score
    bij = dict(bij_init)
    best_bij = dict(bij)

    # sector partitioning
    n_vertices, vertices, _adj, _edges = build_w33()
    edge_decomp = decompose_w33_edges(n_vertices, vertices, edges)
    # Build edge index sets for sectors
    edge_idx_map = {e: i for i, e in enumerate(edges)}
    sector_sets = {
        "incident": {
            edge_idx_map[e] for e in edge_decomp["incident"] if e in edge_idx_map
        },
        "h12": {
            edge_idx_map[e] for e in edge_decomp["h12_internal"] if e in edge_idx_map
        },
        "h27": {
            edge_idx_map[e] for e in edge_decomp["h27_internal"] if e in edge_idx_map
        },
        "cross": {edge_idx_map[e] for e in edge_decomp["cross"] if e in edge_idx_map},
    }
    all_edge_idxs = list(range(len(edges)))

    start = time.time()
    it = 0
    while it < iterations and (time.time() - start) < time_limit:
        it += 1
        # pick swap candidates
        if restrict_sector:
            # pick a random sector weighted by size
            sec = rng.choice(["h27", "cross", "h12", "incident"])
            pool = list(sector_sets[sec])
            if len(pool) < 2:
                continue
            e1, e2 = rng.sample(pool, 2)
        else:
            e1, e2 = rng.sample(all_edge_idxs, 2)

        affected_tris = set(edge_triangles[e1]) | set(edge_triangles[e2])
        prev_matches = sum(exact_flags[t] for t in affected_tris)

        # swap
        bij[e1], bij[e2] = bij[e2], bij[e1]

        new_matches = 0
        for t in affected_tris:
            if triangle_exact(roots, bij, edges, tri_list[t]):
                new_matches += 1

        delta = new_matches - prev_matches
        if delta >= 0:
            # accept and update flags
            for t in affected_tris:
                exact_flags[t] = triangle_exact(roots, bij, edges, tri_list[t])
            current_score += delta
            if current_score > best_score:
                best_score = current_score
                best_bij = dict(bij)
        else:
            # reject swap: revert
            bij[e1], bij[e2] = bij[e2], bij[e1]

    return {
        "best_bij": best_bij,
        "best_score": best_score,
        "initial_score": (
            current_score
            if best_score == current_score
            else sum(triangle_exact(roots, bij_init, edges, t) for t in tri_list)
        ),
        "iterations": it,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in", dest="inpath", default="checks/PART_CVII_e8_bijection.json"
    )
    parser.add_argument(
        "--out", dest="outpath", default="checks/PART_CVII_e8_bijection_repaired.json"
    )
    parser.add_argument("--iters", type=int, default=2000)
    parser.add_argument("--time", type=float, default=10.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-sector", dest="restrict_sector", action="store_false")
    args = parser.parse_args()

    inpath = Path(args.inpath)
    outpath = Path(args.outpath)

    bij_init, raw = load_bijection(inpath)

    n, vertices, adj, edges = build_w33()
    roots = generate_e8_roots()

    print(f"Loaded bijection ({len(bij_init)} entries) from {inpath}")

    res = optimize(
        bij_init,
        edges,
        adj,
        roots,
        iterations=args.iters,
        time_limit=args.time,
        seed=args.seed,
        restrict_sector=args.restrict_sector,
    )

    # Build verification for best bijection
    z3 = classify_roots_z3_grading(roots)
    edge_decomp = decompose_w33_edges(n, adj, edges)
    verification = verify_bijection_properties(
        res["best_bij"], edges, roots, z3, edge_decomp, adj, n
    )

    output = {
        "bijection": {str(k): int(v) for k, v in res["best_bij"].items()},
        "initial_score": int(res["initial_score"]),
        "best_score": int(res["best_score"]),
        "iterations": res["iterations"],
        "verification": verification,
    }

    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote repaired bijection to {outpath}")


if __name__ == "__main__":
    main()
