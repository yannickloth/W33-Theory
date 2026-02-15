#!/usr/bin/env python3
"""
Graviton / Spin-2 sector from W(3,3) K4 pairing (Pillar 43)
=============================================================

Checks performed:
- enumerate the 90 K4 components (outer quads + center quads)
- confirm they form 45 fixed-point-free dual pairs (outer <-> center)
- compute graviton polarization count = 90 / 45 = 2

Usage:
  python scripts/w33_graviton.py
"""
from __future__ import annotations

import json

# Import repository utilities
import sys
import time
from pathlib import Path
from pathlib import Path as _P

import numpy as np

sys.path.insert(0, str(_P(__file__).resolve().parent))
from e8_embedding_group_theoretic import build_w33


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def find_k4_components_from_adj(adj: list[list[int]]):
    """Find all K4 components from adjacency (collinearity) data.

    Returns list of dicts: { 'outer': (a,b,c,d), 'center': (c0,c1,c2,c3) }
    """
    n = len(adj)
    col = [set(adj[i]) for i in range(n)]
    noncol = [set(range(n)) - col[i] - {i} for i in range(n)]

    k4_list = []
    for a in range(n):
        for b in noncol[a]:
            if b <= a:
                continue
            for c in noncol[a] & noncol[b]:
                if c <= b:
                    continue
                for d in noncol[a] & noncol[b] & noncol[c]:
                    if d <= c:
                        continue
                    common = col[a] & col[b] & col[c] & col[d]
                    if len(common) == 4:
                        k4_list.append(
                            {
                                "outer": tuple(sorted([a, b, c, d])),
                                "center": tuple(sorted(common)),
                            }
                        )
    return k4_list


def find_dual_pairs(k4_list: list[dict]):
    """Return list of index-pairs (i,j) implementing outer<->center involution."""
    outer_to_idx = {k4["outer"]: i for i, k4 in enumerate(k4_list)}
    pairs = []
    seen = set()
    for i, k4 in enumerate(k4_list):
        if i in seen:
            continue
        j = outer_to_idx.get(k4["center"])
        if j is None or i == j:
            continue
        # sanity check symmetry
        if k4_list[j]["center"] != k4["outer"]:
            continue
        pairs.append((i, j))
        seen.add(i)
        seen.add(j)
    return pairs


def main():
    t0 = time.time()
    n, vertices, adj, edges = build_w33()

    k4s = find_k4_components_from_adj(adj)
    pairs = find_dual_pairs(k4s)

    results = {
        "n_k4": len(k4s),
        "n_pairs": len(pairs),
        "polarizations_per_pair": len(k4s) // len(pairs) if len(pairs) else None,
        "elapsed_seconds": time.time() - t0,
    }

    out_dir = Path(__file__).resolve().parent.parent / "checks"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"PART_CXLIV_graviton_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"Wrote: {fname}")
    print(results)
    return results


if __name__ == "__main__":
    main()
