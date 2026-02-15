#!/usr/bin/env python3
"""
Information-theoretic diagnostics for W(3,3)

Pillar 44 — Lovász theta & Shannon-capacity bounds for W33
- Compute graph eigenvalues and closed-form Lovász theta for a regular/vertex-transitive graph
- Compute maximum independent set (α)
- Report bounds: α(G) ≤ Θ(G) ≤ ϑ(G) (Shannon capacity bounded by independence and theta)

Usage:
    python scripts/w33_information_theory.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Set

import numpy as np
from w33_homology import build_w33


def lovasz_theta_from_srg_params(n: int, k: float, lambda_min: float) -> float:
    """Closed-form Lovász theta for a regular, vertex-transitive graph.
    Formula (vertex-transitive): theta(G) = -n * lambda_min / (k - lambda_min)
    Works for W33 (and many SRG examples like C5).
    """
    return float(-n * lambda_min / (k - lambda_min))


def adjacency_matrix_from_adjlist(adj: List[List[int]]) -> np.ndarray:
    n = len(adj)
    A = np.zeros((n, n), dtype=float)
    for i, nbrs in enumerate(adj):
        for j in nbrs:
            A[i, j] = 1.0
    return A


def max_independent_set(adj: List[List[int]]) -> List[int]:
    """Branch-and-bound maximum independent set (simple, effective for n=40).
    Returns a list of vertex indices in a maximum independent set.
    """
    n = len(adj)
    nbrs = [set(ne) | {i} for i, ne in enumerate(adj)]

    best: List[int] = []

    # order vertices by degree (heuristic)
    order = sorted(range(n), key=lambda x: len(adj[x]))

    def dfs(candidates: Set[int], cur: List[int]):
        nonlocal best
        # bound
        if len(cur) + len(candidates) <= len(best):
            return
        if not candidates:
            if len(cur) > len(best):
                best = cur.copy()
            return
        # choose pivot with largest degree in candidate subgraph
        v = max(candidates, key=lambda x: len(nbrs[x] & candidates))
        # try including v
        new_cand = candidates - nbrs[v]
        cur.append(v)
        dfs(new_cand, cur)
        cur.pop()
        # try excluding v
        candidates.remove(v)
        dfs(candidates, cur)
        candidates.add(v)

    dfs(set(range(n)), [])
    return sorted(best)


def analyze_w33_information():
    t0 = time.time()
    n, vertices, adj, edges = build_w33()
    A = adjacency_matrix_from_adjlist(adj)
    k = float(len(adj[0]))
    eigs = np.linalg.eigvalsh(A)
    lambda_min = float(np.min(eigs))

    theta = lovasz_theta_from_srg_params(n=n, k=k, lambda_min=lambda_min)

    mis = max_independent_set(adj)
    alpha = len(mis)

    results = {
        "n": n,
        "k": k,
        "lambda_min": lambda_min,
        "lovasz_theta": theta,
        "independence_number": alpha,
        "independent_set": mis,
        "shannon_capacity_bounds": [alpha, "<= Theta(G) <=", theta],
        "elapsed_seconds": time.time() - t0,
    }

    out_dir = Path(__file__).resolve().parent.parent / "checks"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"PART_CXIV_information_theory_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    r = analyze_w33_information()
    print(json.dumps(r, indent=2))
